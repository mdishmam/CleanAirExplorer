
import os
import json
import requests
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy as np


# Setup cache and retry session globally
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DISTRICT_DATA_URL = "https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json"

def load_districts():
    try:
        response = requests.get(DISTRICT_DATA_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data['districts']
    except requests.RequestException as e:
        print(f"Error fetching districts data: {e}")
        return []

# def load_districts():
#     with open(os.path.join(BASE_DIR, 'districts.json'), 'r', encoding='utf-8') as file:
#         data = json.load(file)
#         return data['districts']


def get_weather_and_air_quality(latitude, longitude, start_date=None, end_date=None):
    weather_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "timezone": "Asia/Dhaka"
    }

    air_params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "pm2_5",
        "timezone": "Asia/Dhaka"
    }

    if start_date and end_date:
        weather_params["start_date"] = start_date
        weather_params["end_date"] = end_date
        air_params["start_date"] = start_date
        air_params["end_date"] = end_date
    else:
        weather_params["forecast_days"] = 7
        air_params["forecast_days"] = 7

    weather_res = openmeteo.weather_api(
        "https://api.open-meteo.com/v1/forecast",
        params=weather_params
    )[0]

    air_res = openmeteo.weather_api(
        "https://air-quality-api.open-meteo.com/v1/air-quality",
        params=air_params
    )[0]


    temperature = weather_res.Hourly().Variables(0).ValuesAsNumpy()
    temperature_clean = temperature[~np.isnan(temperature)]
    pm25 = air_res.Hourly().Variables(0).ValuesAsNumpy()
    pm25_clean = pm25[~np.isnan(pm25)]


    return temperature_clean, pm25_clean


def get_avg_temp_pm25(latitude, longitude):
    temperature, pm25 = get_weather_and_air_quality(latitude, longitude)
    print('Inside get_avg_temp_pm25: ', temperature, pm25)

    temps_at_2pm = temperature[14::24]
    avg_temp = np.mean(temps_at_2pm)
    avg_pm25 = np.mean(pm25)

    return avg_temp, avg_pm25


def get_temp_pm25_at_date(latitude, longitude, date):
    temperature, pm25 = get_weather_and_air_quality(latitude, longitude, start_date=date, end_date=date)

    # Temperature & PM2.5 at 2 PM (index 14)
    temp_at_2pm = temperature[14]
    pm25_at_2pm = pm25[14]

    return temp_at_2pm, pm25_at_2pm


if __name__ == '__main__':
    # print(load_districts())
    dist = {
            "id": "63",
            "division_id": "4",
            "name": "Narail",
            "bn_name": "নড়াইল",
            "lat": "23.172534",
            "long": "89.512672"
        }
    latitude = float(dist['lat'])
    longitude = float(dist['long'])

    temperature, pm25 = get_weather_and_air_quality(latitude, longitude)
    print('Inside get_avg_temp_pm25: ', temperature, pm25)

    avg_temp, avg_pm25 = get_avg_temp_pm25(latitude, longitude)
    print(avg_temp, avg_pm25)