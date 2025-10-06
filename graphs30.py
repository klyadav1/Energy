import pandas as pd
import os

#convert the CSV files of every seconds data interval to 30s seconds interval

# Configuration
input_file = 'D:/IndustrialOvenHeatUpPrediction/Research Data CED OVEN/280425.CSV'
output_dir = 'D:/IndustrialOvenHeatUpPrediction/Research Data CED OVEN/30s_sampled_data'
os.makedirs(output_dir, exist_ok=True)

# Read and clean data
df = pd.read_csv(
    input_file,
    delimiter='\t',
    skipinitialspace=True,
    skip_blank_lines=True,
    encoding='utf-16'
)

# Clean data - remove rows with empty/missing time values
df = df.dropna(subset=['Time'])
df['Time'] = df['Time'].astype(str).str.strip()

# Convert time to seconds (handles AM/PM format)
def time_to_seconds(time_str):
    try:
        # Handle "03:00:55 am" format
        time_part = time_str.split()[0]  # Get "03:00:55"
        h, m, s = map(int, time_part.split(':'))
        # Convert to 24-hour format if PM
        if 'pm' in time_str.lower() and h != 12:
            h += 12
        elif 'am' in time_str.lower() and h == 12:
            h = 0
        return h * 3600 + m * 60 + s
    except:
        return None  # For invalid time formats

# Apply conversion and drop invalid times
df['TimeSeconds'] = df['Time'].apply(time_to_seconds)
df = df.dropna(subset=['TimeSeconds'])

# Create 30-second intervals
start_seconds = int(df['TimeSeconds'].min())
end_seconds = int(df['TimeSeconds'].max())
time_intervals = range(start_seconds, end_seconds + 30, 30)

# Function to find nearest time
def find_nearest_row(target_seconds):
    idx = (df['TimeSeconds'] - target_seconds).abs().idxmin()
    return df.loc[idx]

# Create sampled data
sampled_data = []
for interval in time_intervals:
    nearest_row = find_nearest_row(interval)
    sampled_data.append({
        'Date': nearest_row['Date'],
        'Time': nearest_row['Time'],
        **{col: nearest_row[col] for col in df.columns if 'ActValue' in col}
    })

# Create output DataFrame
result = pd.DataFrame(sampled_data)

# Save to new CSV
output_file = os.path.join(output_dir, '280425_30s.CSV')
result.to_csv(
    output_file,
    sep='\t',
    index=False,
    encoding='utf-16'
)

print(f"Created 30-second sampled file:\n{output_file}")
print("\nFirst 5 rows:")
print(result.head())