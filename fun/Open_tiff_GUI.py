import glob
import os
from skimage import io



#function to store abs and fluo datas in a dictionary
def Open_tiff_GUI(directory):
    
    Img_dict = {}
        
    try:
        for file in glob.glob(os.path.join(directory, "*.tif")):
       
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
        print(f"Error: no file in {directory}")
        return None
    