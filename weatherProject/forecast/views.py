from django.shortcuts import render
import requests
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import mean_squared_error
from datetime import datetime, timedelta
import pytz
import os

# Fetch Current Weather Data
def get_current_weather(city):
    api_key = "348a7e5cc69c5a7e83a99a3784d75ce5"  # Replace with your actual API key
    base_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(base_url)
        data = response.json()

        if data.get("cod") != 200:
            print(f"Error: {data.get('message', 'Failed to fetch weather data')}")
            return None

        return {
            'current_temp': data['main'].get('temp', 0),
            'feels_like': data['main'].get('feels_like', 0),
            'temp_min': data['main'].get('temp_min', 0),
            'temp_max': data['main'].get('temp_max', 0),
            'humidity': data['main'].get('humidity', 0),
            'pressure': data['main'].get('pressure', 0),
            'description': data['weather'][0].get('description', ''),
            'country': data['sys'].get('country', ''),
            'Wind_Gust_Speed': data['wind'].get('gust', 0),
            'wind_gust_dir': data['wind'].get('deg', 0),
            'clouds': data['clouds'].get('all', 0),
            'visibility': data.get('visibility', 0),
        }

    except Exception as e:
        print(f"Error occurred while fetching weather data: {e}")
        return None

# Prepare data for training
def prepare_data(data):
    le = LabelEncoder()
    data = data.dropna()
    data['WindGustDir'] = le.fit_transform(data['WindGustDir'])
    data['RainTomorrow'] = le.fit_transform(data['RainTomorrow'])

    x = data[['MinTemp', 'MaxTemp', 'WindGustDir', 'WindGustSpeed', 'Humidity', 'Pressure', 'Temp']]
    y = data['RainTomorrow']

    return x, y, le

# Train Rain Prediction Model
def train_rain_model(x, y):
    if len(x) == 0 or len(y) == 0:
        print("Error: Insufficient training data.")
        return None
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(x_train, y_train)
    return model

# Train Regression Model
def train_regression_model(x, y):
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(x, y)
    return model

# Predict Future
def predict_future(model, current_value):
    predictions = [current_value]
    for _ in range(5):
        next_value = model.predict(np.array([[predictions[-1]]]))
        predictions.append(next_value[0])
    return predictions[1:]

# Weather Analysis Function
def weather_view(request):
    if request.method == 'POST':
        city = request.POST.get('city')
        current_weather = get_current_weather(city)

        if current_weather:
            csv_path = os.path.join('D:\\2 semester\\Capstone\\Weather_Project\\weather.csv')
            historical_data = pd.read_csv(csv_path)

            x, y, le = prepare_data(historical_data)
            rain_model = train_rain_model(x, y)

            x_temp = historical_data['Temp'].values[:-1].reshape(-1, 1)
            y_temp = historical_data['Temp'].values[1:]
            x_hum = historical_data['Humidity'].values[:-1].reshape(-1, 1)
            y_hum = historical_data['Humidity'].values[1:]

            temp_model = train_regression_model(x_temp, y_temp)
            hum_model = train_regression_model(x_hum, y_hum)

            future_temp = predict_future(temp_model, current_weather['temp_min'])
            future_humidity = predict_future(hum_model, current_weather['humidity'])

            timezone = pytz.timezone('America/Toronto')
            now = datetime.now(timezone)
            future_times = [(now + timedelta(hours=i)).strftime("%H:00") for i in range(1, 6)]


            #time1, time2, time3, time4, time5 = future_times
            #temp1, temp2, temp3, temp4, temp5 = future_temp
            #hum1, hum2, hum3, hum4, hum5 = future_humidity

            context = {
                'city': city,
                'current_temp': current_weather['current_temp'],
                'MinTemp': current_weather['temp_min'],
                'MaxTemp': current_weather['temp_max'],
                'feels_like': current_weather['feels_like'],
                'humidity': current_weather['humidity'],
                'clouds': current_weather['clouds'],
                'description': current_weather['description'],
                'country': current_weather['country'],
                'time': now.strftime("%Y-%m-%d %H:%M:%S"),
                'pressure': current_weather['pressure'],
                'visibility': current_weather['visibility'],
                'wind': current_weather['Wind_Gust_Speed'],
                'forecasts': [
                    {'time': future_times[i], 'temp': round(future_temp[i], 1), 'humidity': round(future_humidity[i], 1)}
                    for i in range(5)
                ]
            }

            return render(request, 'weather.html', context)

    return render(request, 'weather.html')
