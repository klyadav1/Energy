import pandas as pd
import matplotlib.pyplot as plt
import glob
import os

# Define directories
source_dir = 'D:/IndustrialOvenHeatUpPrediction/Research Data CED OVEN/30s_sampled_data/'
output_dir = 'D:/IndustrialOvenHeatUpPrediction/Research Data CED OVEN/30s_results/'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Get list of all CSV files in the 30s_sampled_data directory
csv_files = glob.glob(os.path.join(source_dir, '*.CSV'))

for file_path in csv_files:
    print(f"\nProcessing file: {file_path}")
    
    # Read the CSV file
    df = pd.read_csv(
        file_path,
        delimiter='\t',
        skipinitialspace=True,
        skip_blank_lines=True,
        encoding='utf-16'
    )
    
    # Clean and prepare data
    df['Time'] = df['Time'].str.strip()
    
    # Create datetime column for plotting
    datetime_format = '%d-%b-%y %I:%M:%S %p'
    df['DateTime'] = pd.to_datetime(
        df['Date'] + ' ' + df['Time'],
        format=datetime_format,
        errors='coerce'
    ).dropna()
    
    # Get temperature columns
    temp_columns = [col for col in df.columns if 'ActValue' in col]
    
    # Create plot
    plt.figure(figsize=(14, 8))
    for sensor in temp_columns:
        plt.plot(df['DateTime'], df[sensor], label=sensor)
    
    # Customize plot
    filename = os.path.basename(file_path)
    plt.title(f'30s Sampled Temperature Trends\n{filename}', pad=20)
    plt.xlabel('Timestamp')
    plt.ylabel('Temperature (°C)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot
    output_filename = filename.replace('.CSV', '.png')
    output_path = os.path.join(output_dir, output_filename)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved plot to: {output_path}")
    
    # Show plot (optional)
    plt.show()
    plt.close()

print("\nFinished processing all files. Graphs saved in:", output_dir)