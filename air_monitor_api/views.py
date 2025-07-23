from rest_framework.decorators import api_view
from rest_framework.response import Response
import openmeteo_requests
import requests_cache
from retry_requests import retry
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from .utils import load_districts, get_weather_and_air_quality, get_avg_temp_pm25


@api_view(['GET'])
def best_districts(request):
    districts = load_districts()
    results = []

    for dist in districts:
        latitude = float(dist['lat'])
        longitude = float(dist['long'])

        avg_temp, avg_pm25 = get_avg_temp_pm25(latitude, longitude)

        result = {
            "district": dist['name'],
            "avg_temp": avg_temp,
            "avg_pm25": avg_pm25
        }

        print(result)

        results.append(result)

    print('results: \n', results)
    # Sort by coolest temperature, then best air quality
    results_sorted = sorted(results, key=lambda x: (x['avg_temp'], x['avg_pm25']))[:10]

    return Response(results_sorted)


# @api_view(['POST'])
# def travel_recommendation(request):
#     user_lat = request.data.get('latitude')
#     user_long = request.data.get('longitude')
#     destination_name = request.data.get('destination')
#     travel_date = request.data.get('travel_date')  # format YYYY-MM-DD
#
#     districts = load_districts()
#     destination = next((d for d in districts if d['name'].lower() == destination_name.lower()), None)
#     if not destination:
#         return Response({"error": "District not found."}, status=404)
#
#     weather_params_user = {
#         "latitude": user_lat,
#         "longitude": user_long,
#         "hourly": "temperature_2m",
#         "start_date": travel_date,
#         "end_date": travel_date,
#         "timezone": "Asia/Dhaka"
#     }
#
#     weather_params_dest = {
#         "latitude": float(destination['lat']),
#         "longitude": float(destination['long']),
#         "hourly": "temperature_2m",
#         "start_date": travel_date,
#         "end_date": travel_date,
#         "timezone": "Asia/Dhaka"
#     }
#
#     air_params_user = weather_params_user.copy()
#     air_params_user["hourly"] = "pm2_5"
#
#     air_params_dest = weather_params_dest.copy()
#     air_params_dest["hourly"] = "pm2_5"
#
#     user_weather_res = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=weather_params_user)[0]
#     dest_weather_res = openmeteo.weather_api("https://api.open-meteo.com/v1/forecast", params=weather_params_dest)[0]
#     user_air_res = openmeteo.weather_api("https://air-quality-api.open-meteo.com/v1/air-quality", params=air_params_user)[0]
#     dest_air_res = openmeteo.weather_api("https://air-quality-api.open-meteo.com/v1/air-quality", params=air_params_dest)[0]
#
#     user_temp = user_weather_res.Hourly().Variables(0).ValuesAsNumpy()[14]  # 2 PM temp
#     dest_temp = dest_weather_res.Hourly().Variables(0).ValuesAsNumpy()[14]
#
#     user_pm25 = user_air_res.Hourly().Variables(0).ValuesAsNumpy()[14]
#     dest_pm25 = dest_air_res.Hourly().Variables(0).ValuesAsNumpy()[14]
#
#     recommended = dest_temp < user_temp and dest_pm25 < user_pm25
#
#     reason = ""
#     if recommended:
#         reason = f"Your destination is {user_temp - dest_temp:.1f}°C cooler and has better air quality (PM2.5 is lower by {user_pm25 - dest_pm25:.1f}). Enjoy your trip!"
#     else:
#         reason = "Your destination is hotter or has worse air quality. It's better to stay where you are."
#
#     return Response({
#         "recommended": "Recommended" if recommended else "Not Recommended",
#         "reason": reason
#     })
@api_view(['POST'])
def travel_recommendation(request):
    user_lat = request.data.get('latitude')
    user_long = request.data.get('longitude')
    destination_name = request.data.get('destination')
    travel_date = request.data.get('travel_date')  # format YYYY-MM-DD

    districts = load_districts()
    destination = next((d for d in districts if d['name'].lower() == destination_name.lower()), None)
    if not destination:
        return Response({"error": "District not found."}, status=404)

    # Get weather & air data
    user_temp, user_pm25 = get_weather_and_air_quality(user_lat, user_long, travel_date, travel_date)
    dest_temp, dest_pm25 = get_weather_and_air_quality(float(destination['lat']), float(destination['long']), travel_date, travel_date)

    try:
        user_temp_2pm = user_temp[14]
        dest_temp_2pm = dest_temp[14]
        user_pm25_2pm = user_pm25[14]
        dest_pm25_2pm = dest_pm25[14]
    except IndexError:
        return Response({"error": "Insufficient hourly data from API."}, status=500)

    recommended = dest_temp_2pm < user_temp_2pm and dest_pm25_2pm < user_pm25_2pm

    if recommended:
        reason = (
            f"Your destination is {user_temp_2pm - dest_temp_2pm:.1f}°C cooler "
            f"and has better air quality (PM2.5 is lower by {user_pm25_2pm - dest_pm25_2pm:.1f}). Enjoy your trip!"
        )
    else:
        reason = "Your destination is hotter or has worse air quality. It's better to stay where you are."

    return Response({
        "recommended": "Recommended" if recommended else "Not Recommended",
        "reason": reason
    })