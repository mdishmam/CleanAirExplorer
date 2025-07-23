from rest_framework.decorators import api_view
from rest_framework.response import Response
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

