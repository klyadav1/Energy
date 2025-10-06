import requests

API_KEY = "18a9e977d32e4a7a8e961308252106"
LOCATION = "Pune"

def get_weather():
    url = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={LOCATION}"
    response = requests.get(url)
    data = response.json()
    
    return {
        "temperature": data["current"]["temp_c"],
        "humidity": data["current"]["humidity"],
        "conditions": data["current"]["condition"]["text"]
    }

weather = get_weather()
print(weather)

