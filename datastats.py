import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import glob
import os
from datetime import datetime

#this code give the statistics of the data saved in 30s interval

# Configuration
data_dir = 'D:/IndustrialOvenHeatUpPrediction/Research Data CED OVEN/30s_sampled_data/'
output_dir = 'D:/IndustrialOvenHeatUpPrediction/Analysis_Results/'
os.makedirs(output_dir, exist_ok=True)

# 1. Define Sensor-Specific Target Temperatures
SENSOR_TARGETS = {
    'WU311': 160,
    'WU312': 190,
    'WU314': 190,
    'WU321': 190,
    'WU322': 190,
    'WU323': 190
}

# 2. Data Loading and Preprocessing
def load_and_process(file_path):
    try:
        df = pd.read_csv(file_path, delimiter='\t', encoding='utf-16')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, delimiter='\t', encoding='utf-8')
    
    # Clean and prepare data
    df['Time'] = df['Time'].str.strip()
    df['DateTime'] = pd.to_datetime(df['Date'] + ' ' + df['Time'], format='%d-%b-%y %I:%M:%S %p')
    df['ElapsedMinutes'] = (df['DateTime'] - df['DateTime'].iloc[0]).dt.total_seconds() / 60
    
    # Process each sensor column
    results = {}
    for col in df.columns:
        if 'ActValue' in col:
            # Extract sensor name from column header
            sensor_name = None
            for key in SENSOR_TARGETS.keys():
                if key in col:
                    sensor_name = key
                    break
            
            if sensor_name:
                target_temp = SENSOR_TARGETS[sensor_name]
                try:
                    # Find first row reaching target temperature
                    reach_target = df[df[col] >= target_temp].iloc[0]
                    results[sensor_name] = {
                        'StartTime': df['DateTime'].iloc[0].strftime('%Y-%m-%d %H:%M:%S'),
                        'StartTemp': df[col].iloc[0],
                        'TargetReachedTime': reach_target['DateTime'].strftime('%Y-%m-%d %H:%M:%S'),
                        'TimeToTarget': reach_target['ElapsedMinutes'],
                        'FinalTemp': df[col].iloc[-1],
                        'HeatingRate': (target_temp - df[col].iloc[0]) / reach_target['ElapsedMinutes'],
                        'TargetTemp': target_temp,
                        'DataPoints': len(df)
                    }
                except IndexError:
                    results[sensor_name] = {
                        'StartTime': df['DateTime'].iloc[0].strftime('%Y-%m-%d %H:%M:%S'),
                        'StartTemp': df[col].iloc[0],
                        'TargetReachedTime': None,
                        'TimeToTarget': None,
                        'FinalTemp': df[col].iloc[-1],
                        'HeatingRate': None,
                        'TargetTemp': target_temp,
                        'DataPoints': len(df)
                    }
    
    return df, results

# 3. Analyze All Data Files
all_results = {}
for file_path in glob.glob(os.path.join(data_dir, '*.CSV')):
    try:
        date_str = os.path.basename(file_path)[:6]  # Extract date from filename
        date = datetime.strptime(date_str, '%d%m%y').strftime('%d-%b-%Y')
        df, results = load_and_process(file_path)
        all_results[date] = results
        
        # Plot heating curves
        plt.figure(figsize=(12, 8))
        for col in df.columns:
            if 'ActValue' in col:
                sensor_name = None
                for key in SENSOR_TARGETS.keys():
                    if key in col:
                        sensor_name = key
                        break
                
                if sensor_name:
                    target_temp = SENSOR_TARGETS[sensor_name]
                    plt.plot(df['ElapsedMinutes'], df[col], 
                            label=f"{sensor_name} (Target: {target_temp}°C)")
                    plt.axhline(y=target_temp, color='r', linestyle='--', alpha=0.3)
        
        plt.xlabel('Time (minutes)')
        plt.ylabel('Temperature (°C)')
        plt.title(f'Oven Heating Profile - {date}')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f'heating_curve_{date_str}.png'), 
                   dpi=300, bbox_inches='tight')
        plt.close()
        
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

# 4. Generate Analysis Report with Timestamps
report_path = os.path.join(output_dir, 'heating_analysis_report.txt')
with open(report_path, 'w') as f:
    f.write("Industrial Oven Heating Analysis\n")
    f.write("="*50 + "\n\n")
    
    for date in sorted(all_results.keys()):
        f.write(f"Date: {date}\n")
        f.write("-"*50 + "\n")
        
        for sensor in sorted(all_results[date].keys()):
            res = all_results[date][sensor]
            f.write(f"Sensor: {sensor}\n")
            f.write(f"Target Temperature: {res['TargetTemp']}°C\n")
            f.write(f"Start Time: {res['StartTime']}\n")
            f.write(f"Starting Temperature: {res['StartTemp']:.2f}°C\n")
            
            if res['TimeToTarget']:
                f.write(f"Target Reached Time: {res['TargetReachedTime']}\n")
                f.write(f"Time to Target: {res['TimeToTarget']:.1f} minutes\n")
                f.write(f"Heating Rate: {res['HeatingRate']:.2f}°C/min\n")
            else:
                f.write("Target NOT reached during this session\n")
            
            f.write(f"Final Temperature: {res['FinalTemp']:.2f}°C\n")
            f.write(f"Data Points: {res['DataPoints']}\n")
            f.write("\n")
        
        f.write("\n")

# 5. Summary Statistics with Timestamps
summary_stats = {}
for sensor in SENSOR_TARGETS.keys():
    times = []
    rates = []
    start_times = []
    reach_times = []
    
    for date in all_results:
        if sensor in all_results[date] and all_results[date][sensor]['TimeToTarget']:
            times.append(all_results[date][sensor]['TimeToTarget'])
            rates.append(all_results[date][sensor]['HeatingRate'])
            start_times.append(all_results[date][sensor]['StartTime'])
            reach_times.append(all_results[date][sensor]['TargetReachedTime'])
    
    if times:
        summary_stats[sensor] = {
            'AvgTime': np.mean(times),
            'StdTime': np.std(times),
            'MinTime': np.min(times),
            'MaxTime': np.max(times),
            'AvgRate': np.mean(rates),
            'StdRate': np.std(rates),
            'EarliestStart': min(start_times) if start_times else None,
            'LatestStart': max(start_times) if start_times else None,
            'FastestReach': min(reach_times) if reach_times else None,
            'SlowestReach': max(reach_times) if reach_times else None
        }

# Save summary statistics
summary_path = os.path.join(output_dir, 'summary_statistics.txt')
with open(summary_path, 'w') as f:
    f.write("Summary Statistics Across All Dates\n")
    f.write("="*50 + "\n\n")
    
    for sensor in sorted(summary_stats.keys()):
        stats = summary_stats[sensor]
        f.write(f"Sensor: {sensor}\n")
        f.write(f"Target Temperature: {SENSOR_TARGETS[sensor]}°C\n")
        f.write(f"Average Time to Target: {stats['AvgTime']:.1f} ± {stats['StdTime']:.1f} mins\n")
        f.write(f"Range: {stats['MinTime']:.1f} - {stats['MaxTime']:.1f} mins\n")
        f.write(f"Average Heating Rate: {stats['AvgRate']:.2f} ± {stats['StdRate']:.2f}°C/min\n")
        f.write(f"Earliest Start Time: {stats['EarliestStart']}\n")
        f.write(f"Latest Start Time: {stats['LatestStart']}\n")
        f.write(f"Fastest Target Achievement: {stats['FastestReach']}\n")
        f.write(f"Slowest Target Achievement: {stats['SlowestReach']}\n")
        f.write("\n")

print(f"Analysis complete! Results saved to {output_dir}")
print(f"Report: {report_path}")
print(f"Summary: {summary_path}")