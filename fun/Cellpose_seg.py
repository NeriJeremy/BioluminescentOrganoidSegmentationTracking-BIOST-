from cellpose import models
import numpy as np
from skimage import morphology
from tqdm import tqdm
from pathlib import Path
import os
import sys
import tifffile

def Cellpose_seg(Img_dict, GetRims, SaveDir, Save):
    
    Seg_Results = {}
    
    try:
        
        # Get the path to the folder containing the executable
        if getattr(sys, 'frozen', False):
            # If running as a PyInstaller bundle
            app_path = Path(sys._MEIPASS)
        else:
            # Use the main script’s directory
            app_path = Path(sys.argv[0]).resolve().parent
        
        print(f"App Path: {app_path}")
        
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
                
                if GetRims:
                    #Apply dilate and erode and then substract the dilated mask by the eroded mask to keep only the organoid rings
                    dilate = morphology.binary_dilation(masks)
                    erode = morphology.binary_erosion(masks, footprint=[(np.ones((5, 1)), 1), (np.ones((1, 5)), 1)])
                    masks = np.logical_and(dilate, ~erode) #soustraction des pixels de dilate par les pixels de erode
                masks = masks.astype(np.uint16)
                img_masks.append(masks)
    
            img_masks = np.stack(img_masks, axis=0)
    
            Seg_Results[img_name] = img_masks
            
            if Save[0]:
                save_path = os.path.join(SaveDir, f"{img_name}_segmented.tiff")
                print(f"Saving segmented result for {img_name} as {save_path}...")                        
                # Save masks as a multi-page .tiff 
                tifffile.imwrite(save_path, img_masks.astype(np.uint16))
        
        return Seg_Results
    
    except Exception as e:
        print(f'Error when segmenting images: {e}')
        

