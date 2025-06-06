import matplotlib.pyplot as plt


def MakeFigures_GUI(FigParameters,tracking_results, SaveDir, Save):
    
    Results = {}
    
    #Sort the particles to keep only those who have more than 48 localisations
    for filename, df in tracking_results.items():
        
        freq_df = df.groupby('particle').size().reset_index(name='Freq')        
        # Merge the frequency count back to the original dataframe on 'particle'
        df_merged = df.merge(freq_df, on='particle', how='left')        
        # Filter rows where 'Freq' is greater than or equal to 48
        df_filtered = df_merged[df_merged['Freq'] >= 48]        
        Results[filename] = df_filtered
    
        if FigParameters['MakeFig']:
            
            if FigParameters['PoolOrg']:
                    
                fig, ax = plt.subplots(figsize=(8, 6))
                    
                for particle in df_filtered['particle'].unique():
                    # Filter data for the current particle
                    particle_data = df_filtered[df_filtered['particle'] == particle]
                    ax.plot(particle_data['frame'], particle_data['BiolumInt'], label=f'Particle {particle}')
                        
                ax.set_xlabel('Frame')
                ax.set_ylabel('Bioluminescence Intensity')
                ax.set_title(f'{filename}')
                ax.legend(title='Particles')
                
                # Save the plot
                if Save[2]:
                    save_path = f"{SaveDir}/{filename}_particle_{particle}_plot.png"
                    fig.savefig(save_path)
                    print(f"Saved plot for {filename} - Particle {particle} at {save_path}")
                plt.close()
                    
            else:
                    
                for particle in df_filtered['particle'].unique():
                        
                    if FigParameters['PlotSize']:
                            
                        particle_df = df_filtered[df_filtered['particle'] == particle]
        
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
                        particle_df = df_filtered[df_filtered['particle'] == particle]
                            
                        fig, ax = plt.subplots(figsize=(8, 6))
                        ax.plot(particle_df['frame'], particle_df['BiolumInt'], label=f'particle {particle}')
                        ax.set_xlabel('Frame')
                        ax.set_ylabel('Bioluminescence')
                        ax.set_title(f'Bioluminescence for particle {particle} in ({filename})')
                        ax.legend()
                        
                    # Save the plot
                    if Save[2]:
                        save_path = f"{SaveDir}/{filename}_particle_{particle}_plot.png"
                        fig.savefig(save_path)
                        print(f"Saved plot for {filename} - Particle {particle} at {save_path}")
                    plt.close()                
        
        # Save the data
        if Save[1]:    
            for filename, df in Results.items():
                save_path = f"{SaveDir}/{filename}.csv"
                df.to_csv(save_path)     
        
    return Results

      
            
    