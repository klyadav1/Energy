import joblib
import requests
import pandas as pd
from datetime import datetime, timedelta

# Configuration
WEATHER_API_KEY = "18a9e977d32e4a7a8e961308252106"
LOCATION = "Pune"
MODEL_PATH = "D:/IndustrialOvenHeatUpPrediction/oven_time_predictor.pkl"

def get_target_time():
    """Get target time from user with validation"""
    while True:
        try:
            time_str = input("Enter target time in HH:MM format (e.g., 03:00 for 3 AM): ")
            return datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            print("Invalid format! Please use HH:MM (e.g., 06:30)")

# Sensor targets
SENSOR_TARGETS = {
    'WU311': 160,
    'WU312': 190,
    'WU314': 190,
    'WU321': 190,
    'WU322': 190,
    'WU323': 190
}

def get_weather():
    """Fetch current weather data and calculate oven temperature"""
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={LOCATION}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        ambient_temp = data["current"]["temp_c"]
        return {
            "ambient_temp": ambient_temp,
            "oven_temp": ambient_temp + 8,  # Add 5°C buffer
            "humidity": data["current"]["humidity"],
            "conditions": data["current"]["condition"]["text"]
        }
    except Exception as e:
        print(f"Weather API error: {e}")
        # Return default values if API fails
        return {
            "ambient_temp": 25.0,
            "oven_temp": 30.0,
            "humidity": 60,
            "conditions": "Unknown"
        }

def calculate_start_times(target_time):
    """Calculate start times for all sensors to reach target by specified time"""
    try:
        model, feature_names = joblib.load(MODEL_PATH)
        weather_data = get_weather()
        
        # Combine today's date with target time
        target_datetime = datetime.combine(datetime.today(), target_time)
        current_temp = weather_data["oven_temp"]
        
        start_times = {}
        for sensor, target_temp in SENSOR_TARGETS.items():
            input_data = pd.DataFrame({
                'start_temp': [current_temp],
                'ambient_temp': [weather_data["ambient_temp"]],
                'humidity': [weather_data["humidity"]],
                'target_temp': [target_temp],
                **{f'sensor_{s}': [1 if s == sensor else 0] for s in SENSOR_TARGETS}
            })[feature_names]

            heating_time = model.predict(input_data)[0] + 10  # 10 min buffer
            start_time = target_datetime - timedelta(minutes=heating_time)
            
            start_times[sensor] = {
                'heating_time': heating_time,
                'start_time': start_time.strftime("%H:%M"),
                'target_temp': target_temp
            }
        
        latest_start = min(start_times.values(), key=lambda x: x['start_time'])
        
        # Display results
        print(f"\n{' Current Conditions ':-^40}")
        print(f"Atmospheric Temperature: {weather_data['ambient_temp']}°C")
        print(f"Oven Starting Temperature: {current_temp}°C")
        print(f"Humidity: {weather_data['humidity']}%")
        print(f"Weather Conditions: {weather_data['conditions']}\n")
        
        print(f"{' Sensor Requirements ':-^40}")
        for sensor, data in start_times.items():
            print(f"{sensor} (Target: {data['target_temp']}°C):")
            print(f"→ Required Heating Time: {data['heating_time']:.1f} minutes")
            print(f"→ Latest Start Time: {data['start_time']}\n")
        
        print(f"{' OPERATIONAL DECISION ':-^40}")
        print(f"To reach all targets by {target_time.strftime('%H:%M')}:")
        print(f"→ Start ALL burners by: {latest_start['start_time']}")
        print(f"→ Based on longest heating time: {latest_start['heating_time']:.1f} minutes")

    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    print(f"{' Oven Heating Calculator ':=^40}")
    target_time = get_target_time()
    calculate_start_times(target_time)