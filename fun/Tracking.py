import numpy as np
import pandas as pd
from skimage.measure import label, regionprops
import trackpy as tp

def Tracking(Img_dict, Seg_Results, SaveDir, Save):
    
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
