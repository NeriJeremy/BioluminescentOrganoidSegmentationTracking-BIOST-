import traceback

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, font
    from fun.moduleBIOST import BIOST

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
        
        #Make sure the smoothing factors are integers
        try:
            smooth_biolum_factor = int(smooth_biolum_factor_entry.get())
        except ValueError:
            smooth_biolum_factor = 0
        try:
            smooth_area_factor = int(smooth_area_factor_entry.get())
        except ValueError:
            smooth_area_factor = 0
        try:
            min_track_length = int(min_track_length_entry.get())
        except ValueError:
            min_track_length = 0
        
        ProcessingParameters = {
            'baselineCorr': baselineCorr.get(),
            'normalize' : norm_var.get(),
            'smooth_biolum' : smooth_biolum_var.get(),
            'smooth_area' : smooth_area_var.get(),
            'smooth_biolum_factor' : smooth_biolum_factor,
            'smooth_area_factor' : smooth_area_factor,
            'min_track_length' : min_track_length
        }

        Save = [save_raw_images_var.get(), save_csv_var.get(), save_plots_var.get()]

        try:
            Var = BIOST(directory, GetRims, save_dir, Save, FigParameters, ProcessingParameters)
            Img_dict = Var.Open_tiff_GUI()
            Seg_Results = Var.Cellpose_seg(Img_dict)
            tracking_results = Var.Tracking(Img_dict, Seg_Results)
            processed_data = Var.processdata(tracking_results)
            plots = Var.makefigures(processed_data)

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
    
    root.geometry("700x600")
    # Create a bold font
    bold_font = font.Font(root, weight="bold", size=10)
    
    root.title("BIOST: Bioluminescent Organoig Segmentation and Tracking")

    tk.Label(root, text="Select directory containing .tiff files :").pack(padx=10, pady=5)
    directory_entry = tk.Entry(root, width=60)
    directory_entry.pack(padx=10, pady=5)
    directory_button = tk.Button(root, text="Browse", command=lambda: select_directory(directory_entry))
    directory_button.pack(padx=10, pady=5)

    tk.Label(root, text="Select directory to save results :").pack(padx=10, pady=5)
    save_dir_entry = tk.Entry(root, width=60)
    save_dir_entry.pack(padx=10, pady=5)
    save_dir_button = tk.Button(root, text="Browse", command=lambda: select_directory(save_dir_entry))
    save_dir_button.pack(padx=10, pady=5)
    
    # ----------------- Processing Options -----------------
    Process_frame = tk.LabelFrame(root, text="Processing Options :", padx=10, pady=10, font=bold_font)
    Process_frame.pack(padx=10, pady=10, fill="x")
    # Container to hold the columns, centered
    proc_container = tk.Frame(Process_frame)
    proc_container.pack(padx=10, pady=5, anchor='center')
    
    # Column 1 (Left)
    proc_left = tk.Frame(proc_container)
    proc_left.pack(side='left', padx=20, anchor='n')
    
    # Column 2 (Middle)
    proc_middle = tk.Frame(proc_container)
    proc_middle.pack(side='left', padx=20, anchor='n')
    
    # Column 3 (Right)
    proc_right = tk.Frame(proc_container)
    proc_right.pack(side='left', padx=20, anchor='n')
    
    # Column 1 (Left)
    baselineCorr = tk.BooleanVar(value=False)
    tk.Checkbutton(proc_left, text="Apply baseline correction", variable=baselineCorr).pack(anchor="w")
    get_rims_var = tk.BooleanVar(value=True)
    tk.Checkbutton(proc_left, text="Segment the rims", variable=get_rims_var).pack(anchor="w")
    norm_var = tk.BooleanVar(value=True)
    tk.Checkbutton(proc_left, text="Apply normalization", variable=norm_var).pack(anchor="w")
    
    # Column 2 (middle)
    smooth_biolum_var = tk.BooleanVar(value=False)
    tk.Checkbutton(proc_middle, text="Smooth Biolum", variable=smooth_biolum_var).pack(anchor="w")
    tk.Label(proc_middle, text="Smooth Factor for Biolum data:").pack(anchor="w")
    smooth_biolum_factor_entry = tk.Entry(proc_middle, width=10)
    smooth_biolum_factor_entry.insert(0, "3")
    smooth_biolum_factor_entry.pack(anchor="w")
    
    
    # Column 3 (Right)
    smooth_area_var = tk.BooleanVar(value=False)
    tk.Checkbutton(proc_right, text="Smooth Area", variable=smooth_area_var).pack(anchor="w")
    tk.Label(proc_right, text="Smooth Factor for size data:").pack(anchor="w")
    smooth_area_factor_entry = tk.Entry(proc_right, width=10)
    smooth_area_factor_entry.insert(0, "3")
    smooth_area_factor_entry.pack(anchor="w")
    tk.Label(proc_right, text="Min track length (hours):").pack(anchor="w")
    min_track_length_entry = tk.Entry(proc_right, width=10)
    min_track_length_entry.insert(0, "48")
    min_track_length_entry.pack(anchor="w")

    # ----------------- Figure Parameters and Save Options -----------------
    bottom_frame = tk.Frame(root)
    bottom_frame.pack(padx=10, pady=10, fill="x")
    
    # Figure Parameters Frame
    Figparam_frame = tk.LabelFrame(bottom_frame, text="Figure Parameters :", padx=10, pady=10, font=bold_font)
    Figparam_frame.pack(side='left', padx=20, fill="both", expand=True)
    
    fig_param_makefig_var = tk.BooleanVar(value=True)
    tk.Checkbutton(Figparam_frame, text="Make Figure", variable=fig_param_makefig_var).pack(anchor="w")
    fig_param_plot_size_var = tk.BooleanVar(value=True)
    tk.Checkbutton(Figparam_frame, text="Plot Size", variable=fig_param_plot_size_var).pack(anchor="w")
    fig_param_pool_org_var = tk.BooleanVar(value=False)
    tk.Checkbutton(Figparam_frame, text="Pool Organoids", variable=fig_param_pool_org_var).pack(anchor="w")
    
    # Save Options Frame
    save_options_frame = tk.LabelFrame(bottom_frame, text="Save Options :", padx=10, pady=10, font=bold_font)
    save_options_frame.pack(side='left', padx=20, fill="both", expand=True)
    
    save_raw_images_var = tk.BooleanVar(value=False)
    tk.Checkbutton(save_options_frame, text="Save Segmented Images", variable=save_raw_images_var).pack(anchor="w")
    save_csv_var = tk.BooleanVar(value=True)
    tk.Checkbutton(save_options_frame, text="Save CSV", variable=save_csv_var).pack(anchor="w")
    save_plots_var = tk.BooleanVar(value=True)
    tk.Checkbutton(save_options_frame, text="Save Plots", variable=save_plots_var).pack(anchor="w")
    


    run_button = tk.Button(root, text="Run Analysis", command=run_analysis)
    run_button.pack(padx=10, pady=20)

    root.mainloop()

except Exception as e:
    with open("error.log", "w") as f:
        traceback.print_exc(file=f)
