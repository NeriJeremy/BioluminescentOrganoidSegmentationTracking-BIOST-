from scipy import signal
from cellpose import models
from skimage import morphology, io
from skimage.measure import label, regionprops
from tqdm import tqdm
from pathlib import Path
import pandas as pd
import numpy as np
import trackpy as tp
import matplotlib.pyplot as plt
import glob
import os
import sys
import tifffile

class BIOST:
    
    def __init__(self, directory, GetRims, save_dir, Save, FigParameters, ProcessingParameters):
        
        self.directory = directory
        self.GetRims = GetRims
        self.save_dir = save_dir
        self.Save = Save
        self.FigParameters = FigParameters
        self.ProcessingParameters = ProcessingParameters
    
    #function to store abs and fluo datas in a dictionary
    def Open_tiff_GUI(self):
        
        Img_dict = {}
            
        try:
            for file in glob.glob(os.path.join(self.directory, "*.tif")):
           
                # Read the file into a DataFrame
                img = io.imread(file)
                #keep only the name of the file in the dico (instead of the whole path)
                file_name = os.path.basename(file)
                Img_dict[file_name] = img
                            
                # Add the DataFrame to the dictionary
                print(f"Opened file: {file}")
                        
            # Return the dictionary of DataFrames
            return Img_dict
        
        except FileNotFoundError:
            print(f"Error: no file in {self.directory}")
            return None
        
    def Cellpose_seg(self, Img_dict):
        
        Seg_Results = {}
        
        try:
            
            # Get the path to the folder containing the executable
            if getattr(sys, 'frozen', False):
                # If running as a PyInstaller bundle
                app_path = Path(sys._MEIPASS)
            else:
                # Use the main script’s directory
                app_path = Path(sys.argv[0]).resolve().parent
            
            model_path = app_path / 'models' / 'cyto2_3_biolum'
            
            #path to the trained model
            #model_path = 'C:/Users/jneri/Desktop/Local/For_Constanza/scripts/cellpose/models/cyto2_3_biolum'
            #Load the trained model
            model = models.CellposeModel(pretrained_model=str(model_path))
            
        except Exception as e:
            print(f'Error when importing Cellpose model: {e}')
            
        try:
            
            for img_name, img in Img_dict.items():
                
                print(f" Segmenting {img_name}...")
                img_masks = []
                
                for num in tqdm(range(img.shape[0]), desc=f"Segmenting slices of {img_name}", unit="slice"):
                    
                    # Get the slice (num-th slice in the stack)
                    slice_img = img[num, :, :]
                    # Run segmentation on the current image
                    masks, flows, styles = model.eval(slice_img, diameter=None, channels=[0, 0])
                    
                    if self.GetRims:
                        #Apply dilate and erode and then substract the dilated mask by the eroded mask to keep only the organoid rings
                        dilate = morphology.binary_dilation(masks)
                        erode = morphology.binary_erosion(masks, footprint=[(np.ones((5, 1)), 1), (np.ones((1, 5)), 1)])
                        masks = np.logical_and(dilate, ~erode) #soustraction des pixels de dilate par les pixels de erode
                    masks = masks.astype(np.uint16)
                    img_masks.append(masks)
        
                img_masks = np.stack(img_masks, axis=0)
        
                Seg_Results[img_name] = img_masks
                
                if self.Save[0]:
                    save_path = os.path.join(self.save_dir, f"{img_name}_segmented.tiff")
                    print(f"Saving segmented result for {img_name} as {save_path}...")                        
                    # Save masks as a multi-page .tiff 
                    tifffile.imwrite(save_path, img_masks.astype(np.uint16))
            
            return Seg_Results
        
        except Exception as e:
            print(f'Error when segmenting images: {e}')
    
    def Tracking(self, Img_dict, Seg_Results):
        
        Totrack = {}
        
        try:
            #Concatenate the acquisition with the segmented images
            for img_name in Img_dict.keys():
                raw_img = Img_dict[img_name]
                seg_img = Seg_Results[img_name]
                concatenated_img = np.stack((raw_img, seg_img), axis=-1)
                Totrack[img_name] = concatenated_img
            
        except Exception as e:
            print(f'Error when concatenating raw data with segmented data: {e}')

        try:
            # Dictionary to store results for each image
            tracking_results = {}

            # For each image (file) in Totrack
            for img_name, img in Totrack.items():
                print(f"Tracking image: {img_name}...")

                # Features for tracking (separately for each image)
                featuresCentro = []
                featuresBiolum = []

                # Iterate through the stacks (frames) of the current image
                for num in range(img.shape[0]):
                    slice_img = img[num, :, :, 1]  # Select the segmented image slice (index 1 for segmented image)
                    label_image = label(slice_img, background=0)
                    
                    for region in regionprops(label_image, intensity_image=slice_img):  # Use segmented image for regionprops
                        # Skip small or large areas
                        if region.area < 200 or region.area > 1200:
                            continue
                        # Skip small areas on the top of the image
                        if region.centroid[0] < 260 and region.area < 80:
                            continue
                        # Store features for the centroid (region properties)
                        featuresCentro.append({
                            'y': region.centroid[0],
                            'x': region.centroid[1],
                            'frame': num,
                            'region': region.label,
                            'image_name': img_name,  # Track which image this is from
                        })

                # Collect features for bioluminescence
                for num in range(img.shape[0]):
                    slice_img = img[num, :, :, 1]  # Select the segmented image slice (index 1 for segmented image)
                    label_image = label(slice_img, background=0)
                    
                    for region in regionprops(label_image, intensity_image=Totrack[img_name][num, :, :, 0]):  # Use raw image for intensity
                        
                        featuresBiolum.append({
                            'area': region.area,
                            'BiolumInt': region.intensity_mean,
                            'region': region.label,
                            'frame': num,
                            'image_name': img_name,  # Track which image this is from
                        })

                # Convert the collected features into DataFrames
                featuresCentro_df = pd.DataFrame(featuresCentro)
                featuresBiolum_df = pd.DataFrame(featuresBiolum)
                
                # Merge centroid features with bioluminescence features based on frame and region
                dfTracking = pd.merge(featuresCentro_df, featuresBiolum_df, how='left', on=['frame', 'region', 'image_name'])

                # Use Trackpy to link the objects across frames
                t = tp.link_df(dfTracking, search_range=75, memory=20, link_strategy='auto')
                
                # Store the tracking result for this image
                tracking_results[img_name] = t               
                
            # Return the tracking results for all images as a dictionary
            return tracking_results

        except Exception as e:
            print(f'Tracking error: {e}')
    
    def processdata(self, tracking_results):
        
        data = {}
        
        #Sort the particles to keep only those who have more than 48 localisations
        for filename, df in tracking_results.items():
            
            freq_df = df.groupby('particle').size().reset_index(name='Freq')        
            # Merge the frequency count back to the original dataframe on 'particle'
            df_merged = df.merge(freq_df, on='particle', how='left')        
            # Filter rows where 'Freq' is greater than or equal to the min track length choosen by user input
            df_filtered = df_merged[df_merged['Freq'] >= self.ProcessingParameters['min_track_length']]        
            data[filename] = df_filtered
        
        processed_data = {}
        
        for filename, df in data.items():
            
            for particle in df['particle'].unique():
                
                particle_data = df[df['particle'] == particle].copy()
                
                if self.ProcessingParameters['baselineCorr']: # Apply baseline correction with scipy.detrend function
                    particle_data = df[df['particle'] == particle]
                    particle_data.loc[:, 'BiolumInt'] = signal.detrend(particle_data['BiolumInt'])    
                    
                if self.ProcessingParameters['normalize']: # Normalize fluo data
                    # Apply Min-Max normalization
                    biolum = particle_data['BiolumInt']
                    particle_data.loc[:, 'BiolumInt'] = (biolum - biolum.min()) / (biolum.max() - biolum.min())
                
                if self.ProcessingParameters['smooth_biolum']: # mean smoothing of the data
                    particle_data.loc[:, 'BiolumInt'] = (particle_data['BiolumInt'].rolling(
                        window=self.ProcessingParameters['smooth_biolum_factor'], center=True, min_periods=1).mean())
                
                if self.ProcessingParameters['smooth_area']: # mean smoothing of the data
                    particle_data.loc[:, 'area'] = (particle_data['area'].rolling(
                        window=self.ProcessingParameters['smooth_area_factor'], center=True, min_periods=1).mean())
                 
                if filename not in processed_data: # convert filename into a pd dataframe
                    processed_data[filename] = pd.DataFrame()
                processed_data[filename] = pd.concat([processed_data[filename], particle_data])
            
        return processed_data
    
    def makefigures(self, processed_data):
        
        for filename, df in processed_data.items():
            
            if self.FigParameters['MakeFig']:
                
                if self.FigParameters['PoolOrg']:
                        
                    fig, ax = plt.subplots(figsize=(8, 6))
                        
                    for particle in df['particle'].unique():
                        # Filter data for the current particle
                        particle_data = df[df['particle'] == particle]
                        ax.plot(particle_data['frame'], particle_data['BiolumInt'], label=f'Particle {particle}')
                            
                    ax.set_xlabel('Frame')
                    ax.set_ylabel('Bioluminescence Intensity')
                    ax.set_title(f'{filename}')
                    ax.legend(title='Particles')
                    
                    # Save the plot
                    if self.Save[2]:
                        save_path = f"{self.save_dir}/{filename}_particle_{particle}_plot.png"
                        fig.savefig(save_path)
                        print(f"Saved plot for {filename} - Particle {particle} at {save_path}")
                    plt.close()
                        
                else:
                        
                    for particle in df['particle'].unique():
                            
                        if self.FigParameters['PlotSize']:
                                
                            particle_df = df[df['particle'] == particle]
                            # Create a new figure for each particle
                            fig, ax1 = plt.subplots(figsize=(8, 6))
                                
                            # Create the first axis for BiolumInt
                            ax1 = plt.gca()  # Get the current axis
                            ax1.plot(particle_df['frame'], particle_df['BiolumInt'], label='Bioluminescence', color='tab:blue')
                                
                            # Label the first Y axis
                            ax1.set_xlabel('Frame')
                            ax1.set_ylabel('Bioluminescence', color='tab:blue')
                            ax1.tick_params(axis='y', labelcolor='tab:blue')
                                
                            # Create the second axis for Area
                            ax2 = ax1.twinx()  # This creates a second Y axis that shares the same X axis                        
                            ax2.plot(particle_df['frame'], particle_df['area'], label='Area', color='tab:orange')
                                
                            # Label the second Y axis
                            ax2.set_ylabel('Area', color='tab:orange')
                            ax2.tick_params(axis='y', labelcolor='tab:orange')
                                
                            # Set the title and legend
                            plt.title(f'Bioluminescence and Area for particle {particle} in {filename}')
                                
                            # Combine the legends
                            lines = ax1.get_lines() + ax2.get_lines()  # Get both lines for the two axes
                            labels = [line.get_label() for line in lines]  # Get the labels for the lines
                            plt.legend(lines, labels) 
                                
                        else:
                            #Create a df for each particle
                            particle_df = df[df['particle'] == particle]
                            fig, ax = plt.subplots(figsize=(8, 6))
                            ax.plot(particle_df['frame'], particle_df['BiolumInt'], label=f'particle {particle}')
                            ax.set_xlabel('Frame')
                            ax.set_ylabel('Bioluminescence')
                            ax.set_title(f'Bioluminescence for particle {particle} in ({filename})')
                            ax.legend()
                            
                        # Save the plot
                        if self.Save[2]:
                            save_path = f"{self.save_dir}/{filename}_particle_{particle}_plot.png"
                            fig.savefig(save_path)
                            print(f"Saved plot for {filename} - Particle {particle} at {save_path}")
                        plt.close()                
            
            # Save the data
            if self.Save[1]:    
                for filename, df in processed_data.items():
                    save_path = f"{self.save_dir}/{filename}.csv"
                    df.to_csv(save_path)     
            
        return processed_data