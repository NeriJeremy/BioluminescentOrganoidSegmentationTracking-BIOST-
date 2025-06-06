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
        
        ProcessingParameters = {
            'baselineCorr': baselineCorr.get()
        }

        Save = [save_raw_images_var.get(), save_csv_var.get(), save_plots_var.get()]

        try:
            Var = BIOST(directory, GetRims, save_dir, Save, FigParameters, ProcessingParameters)
            Img_dict = Var.Open_tiff_GUI()
            Seg_Results = Var.Cellpose_seg(Img_dict)
            tracking_results = Var.Tracking(Img_dict, Seg_Results)
            Results = Var.MakeFigures_GUI(tracking_results)

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
    
    # Create a bold font
    bold_font = font.Font(root, weight="bold", size=10)
    
    root.title("Organoid segmentation and tracking GUI")

    tk.Label(root, text="Select directory containing .tiff files :").pack(padx=10, pady=5)
    directory_entry = tk.Entry(root, width=50)
    directory_entry.pack(padx=10, pady=5)
    directory_button = tk.Button(root, text="Browse", command=lambda: select_directory(directory_entry))
    directory_button.pack(padx=10, pady=5)

    tk.Label(root, text="Select directory to save results :").pack(padx=10, pady=5)
    save_dir_entry = tk.Entry(root, width=50)
    save_dir_entry.pack(padx=10, pady=5)
    save_dir_button = tk.Button(root, text="Browse", command=lambda: select_directory(save_dir_entry))
    save_dir_button.pack(padx=10, pady=5)
    
    Process_frame = tk.LabelFrame(root, text="Processing Options :", padx=10, pady=5, font=bold_font)
    Process_frame.pack(padx=10, pady=5, fill="x")
    baselineCorr = tk.BooleanVar(value=False)
    tk.Checkbutton(Process_frame, text="Apply baseline correction", variable=baselineCorr).pack(anchor="w")
    get_rims_var = tk.BooleanVar(value=True)
    tk.Checkbutton(Process_frame, text="Segment the rims", variable=get_rims_var).pack(anchor="w")

    Figparam_frame = tk.LabelFrame(root, text="Figure Parameters :", padx=10, pady=5, font=bold_font)
    Figparam_frame.pack(padx=10, pady=5, fill="x")
    fig_param_makefig_var = tk.BooleanVar(value=True)
    tk.Checkbutton(Figparam_frame, text="Make Figure", variable=fig_param_makefig_var).pack(anchor="w")
    fig_param_plot_size_var = tk.BooleanVar(value=True)
    tk.Checkbutton(Figparam_frame, text="Plot Size", variable=fig_param_plot_size_var).pack(anchor="w")
    fig_param_pool_org_var = tk.BooleanVar(value=False)
    tk.Checkbutton(Figparam_frame, text="Pool Organoids", variable=fig_param_pool_org_var).pack(anchor="w")

    save_options_frame = tk.LabelFrame(root, text="Save Options :", padx=10, pady=5, font=bold_font)
    save_options_frame.pack(padx=10, pady=5, fill="x")
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
