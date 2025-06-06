import sys
import traceback

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from fun.Open_tiff_GUI import Open_tiff_GUI
    from fun.Cellpose_seg import Cellpose_seg
    from fun.Tracking import Tracking
    from fun.MakeFigures_GUI import MakeFigures_GUI

    def run_analysis():
        directory = directory_entry.get()
        save_dir = save_dir_entry.get()
        
        if not directory or not save_dir:
            messagebox.showerror("Error", "Please specify both input directory and save directory.")
            return

        GetRims = get_rims_var.get()

        FigParameters = {
            'MakeFig': fig_param_makefig_var.get(),
            'PlotSize': fig_param_plot_size_var.get(),
            'PoolOrg': fig_param_pool_org_var.get(),
        }

        Save = [save_raw_images_var.get(), save_csv_var.get(), save_plots_var.get()]

        try:
            Img_dict = Open_tiff_GUI(directory)
            Seg_Results = Cellpose_seg(Img_dict, GetRims, save_dir, Save)
            tracking_results = Tracking(Img_dict, Seg_Results, save_dir, Save)
            Results = MakeFigures_GUI(FigParameters, tracking_results, save_dir, Save)

            messagebox.showinfo("Success", "Analysis completed successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def select_directory(entry_field):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            entry_field.delete(0, tk.END)
            entry_field.insert(0, folder_selected)

    # GUI setup
    root = tk.Tk()
    root.title("Organoid segmentation and tracking GUI")

    tk.Label(root, text="Select directory containing .tiff files").pack(padx=10, pady=5)
    directory_entry = tk.Entry(root, width=50)
    directory_entry.pack(padx=10, pady=5)
    directory_button = tk.Button(root, text="Browse", command=lambda: select_directory(directory_entry))
    directory_button.pack(padx=10, pady=5)

    tk.Label(root, text="Select directory to save results").pack(padx=10, pady=5)
    save_dir_entry = tk.Entry(root, width=50)
    save_dir_entry.pack(padx=10, pady=5)
    save_dir_button = tk.Button(root, text="Browse", command=lambda: select_directory(save_dir_entry))
    save_dir_button.pack(padx=10, pady=5)

    get_rims_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Segment the rims", variable=get_rims_var).pack(padx=10, pady=5)

    tk.Label(root, text="Figure Parameters :").pack(padx=10, pady=5)
    fig_param_makefig_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Make Figure", variable=fig_param_makefig_var).pack(padx=10, pady=5)
    fig_param_plot_size_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Plot Size", variable=fig_param_plot_size_var).pack(padx=10, pady=5)
    fig_param_pool_org_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Pool Organoids", variable=fig_param_pool_org_var).pack(padx=10, pady=5)

    tk.Label(root, text="Save Options :").pack(padx=10, pady=5)
    save_raw_images_var = tk.BooleanVar(value=False)
    tk.Checkbutton(root, text="Save Raw Images", variable=save_raw_images_var).pack(padx=10, pady=5)
    save_csv_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Save CSV", variable=save_csv_var).pack(padx=10, pady=5)
    save_plots_var = tk.BooleanVar(value=True)
    tk.Checkbutton(root, text="Save Plots", variable=save_plots_var).pack(padx=10, pady=5)

    run_button = tk.Button(root, text="Run Analysis", command=run_analysis)
    run_button.pack(padx=10, pady=20)

    root.mainloop()

except Exception as e:
    with open("error.log", "w") as f:
        traceback.print_exc(file=f)
"""
import tkinter as tk
from tkinter import filedialog, messagebox
from fun.Open_tiff_GUI import Open_tiff_GUI
from fun.Cellpose_seg import Cellpose_seg
from fun.Tracking import Tracking
from fun.MakeFigures_GUI import MakeFigures_GUI


def run_analysis():
    directory = directory_entry.get()
    save_dir = save_dir_entry.get()
    
    if not directory or not save_dir:
        messagebox.showerror("Error", "Please specify both input directory and save directory.")
        return

    GetRims = get_rims_var.get()

    FigParameters = {
        'MakeFig': fig_param_makefig_var.get(),
        'PlotSize': fig_param_plot_size_var.get(),
        'PoolOrg': fig_param_pool_org_var.get(),
    }

    Save = [save_raw_images_var.get(), save_csv_var.get(), save_plots_var.get()]

    try:
        # Call functions with the selected parameters
        Img_dict = Open_tiff_GUI(directory)
        Seg_Results = Cellpose_seg(Img_dict, GetRims, save_dir, Save)
        tracking_results = Tracking(Img_dict, Seg_Results, save_dir, Save)
        Results = MakeFigures_GUI(FigParameters, tracking_results, save_dir, Save)

        messagebox.showinfo("Success", "Analysis completed successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to open file dialog for selecting directory
def select_directory(entry_field):
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        entry_field.delete(0, tk.END)  # Clear existing text
        entry_field.insert(0, folder_selected)  # Insert new path

# Create the main window
root = tk.Tk()
root.title("Organoid segmentation and tracking GUI")

# Directory input (for .tiff files)
tk.Label(root, text="Select directory containing .tiff files").pack(padx=10, pady=5)
directory_entry = tk.Entry(root, width=50)
directory_entry.pack(padx=10, pady=5)
directory_button = tk.Button(root, text="Browse", command=lambda: select_directory(directory_entry))
directory_button.pack(padx=10, pady=5)

# Directory input (for saving output)
tk.Label(root, text="Select directory to save results").pack(padx=10, pady=5)
save_dir_entry = tk.Entry(root, width=50)
save_dir_entry.pack(padx=10, pady=5)
save_dir_button = tk.Button(root, text="Browse", command=lambda: select_directory(save_dir_entry))
save_dir_button.pack(padx=10, pady=5)

# Checkboxes for user options
get_rims_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Segment the rims", variable=get_rims_var).pack(padx=10, pady=5)

# Figure parameters
tk.Label(root, text="Figure Parameters :").pack(padx=10, pady=5)
fig_param_makefig_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Make Figure", variable=fig_param_makefig_var).pack(padx=10, pady=5)

fig_param_plot_size_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Plot Size", variable=fig_param_plot_size_var).pack(padx=10, pady=5)

fig_param_pool_org_var = tk.BooleanVar(value=False)
tk.Checkbutton(root, text="Pool Organoids", variable=fig_param_pool_org_var).pack(padx=10, pady=5)

# Checkboxes for save options
tk.Label(root, text="Save Options :").pack(padx=10, pady=5)
save_raw_images_var = tk.BooleanVar(value=False)
tk.Checkbutton(root, text="Save Raw Images", variable=save_raw_images_var).pack(padx=10, pady=5)

save_csv_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Save CSV", variable=save_csv_var).pack(padx=10, pady=5)

save_plots_var = tk.BooleanVar(value=True)
tk.Checkbutton(root, text="Save Plots", variable=save_plots_var).pack(padx=10, pady=5)

# Run button
run_button = tk.Button(root, text="Run Analysis", command=run_analysis)
run_button.pack(padx=10, pady=20)

# Start the GUI loop
root.mainloop()
"""