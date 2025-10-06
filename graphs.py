import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

#used to buid the Graphs of all the raw data obtained from scada


data_dir = 'D:/IndustrialOvenHeatUpPrediction/Research Data CED OVEN/'
output_dir = 'D:/IndustrialOvenHeatUpPrediction/Research Data CED OVEN/graphs/'

os.makedirs(output_dir, exist_ok=True)

csv_files = glob.glob(data_dir + '*.CSV')

for file_path in csv_files:
    print(f"\nProcessing file: {file_path}")
    
    
    df = pd.read_csv(
        file_path,
        delimiter='\t',
        skipinitialspace=True,
        skip_blank_lines=True,
        encoding='utf-16'
    )
    df['Time'] = df['Time'].str.strip()
    
    
    datetime_format = '%d-%b-%y %I:%M:%S %p'
    df['DateTime'] = pd.to_datetime(
        df['Date'] + ' ' + df['Time'],
        format=datetime_format,
        errors='coerce'
    )
    df = df.dropna(subset=['DateTime'])
    
    temp_columns = [col for col in df.columns if 'ActValue' in col]
    
    plt.figure(figsize=(14, 8))
    for sensor in temp_columns:
        plt.plot(df['DateTime'], df[sensor], label=sensor)

    filename = os.path.basename(file_path)
    plt.title(f'Industrial Oven Temperature Trends\n{filename}', pad=20)
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature (°C)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    
    output_filename = filename.replace('.CSV', '.png')
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to: {output_path}")
    
    
    plt.show()
    plt.close()  # Close the figure to free memory

print("\nFinished processing all files.")