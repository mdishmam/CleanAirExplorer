# Clean Air Explorer

Clean Air Explorer is a Django REST API application that provides information about air quality and temperature in different districts in Bangladesh. It helps users find the best districts in terms of air quality and temperature, and provides travel recommendations based on weather and air quality comparisons.

## Data Sources

- Weather and air quality data is fetched from the [Open-Meteo API](https://open-meteo.com/)
- District information is loaded from a local JSON file
- The application focuses on Bangladesh districts (timezone: Asia/Dhaka)
- Temperature data is measured in Celsius and air quality in PM2.5 concentration

## Features

- Get a list of the top 10 districts with the best combination of cool temperature and good air quality
- Get personalized travel recommendations by comparing your current location with a destination

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/mdishmam/CleanAirExplorer.git
   cd CleanAirExplorer
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Start the development server:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/api/`.

## API Endpoints

### 1. Best Districts

Returns the top 10 districts sorted by coolest temperature and best air quality.

- **URL**: `/api/best-districts/`
- **Method**: GET
- **Response Example**:
  ```json
  [
    {
      "district": "Sylhet",
      "avg_temp": 22.5,
      "avg_pm25": 10.2
    },
    {
      "district": "Cox's Bazar",
      "avg_temp": 23.1,
      "avg_pm25": 12.5
    },
    {
      "district": "Rangamati",
      "avg_temp": 24.2,
      "avg_pm25": 15.8
    },
    ...
  ]
  ```

### 2. Travel Recommendation

Compares user's current location with a destination to recommend travel based on temperature and air quality.

- **URL**: `/api/travel-recommendation/`
- **Method**: POST
- **Request Body**:
  ```json
  {
    "latitude": 23.7115253,
    "longitude": 90.4111451,
    "destination": "Chattogram",
    "travel_date": "2023-07-25"
  }
  ```
- **Response Example**:
  ```json
  {
    "recommended": "Recommended",
    "reason": "Your destination is 2.5°C cooler and has better air quality (PM2.5 is lower by 5.3). Enjoy your trip!"
  }
  ```

## Testing the API

### Using curl

1. Get best districts:
   ```bash
   curl -X GET http://127.0.0.1:8000/api/best-districts/
   ```

2. Get travel recommendation:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/travel-recommendation/ \
     -H "Content-Type: application/json" \
     -d '{"latitude": 23.7115253, "longitude": 90.4111451, "destination": "Chattogram", "travel_date": "2023-07-25"}'
   ```

### Using Postman

1. Get best districts:
   - Set the request type to GET
   - Enter the URL: `http://127.0.0.1:8000/api/best-districts/`
   - Click Send

2. Get travel recommendation:
   - Set the request type to POST
   - Enter the URL: `http://127.0.0.1:8000/api/travel-recommendation/`
   - Go to the Body tab, select raw and JSON
   - Enter the request body:
     ```json
     {
       "latitude": 23.7115253,
       "longitude": 90.4111451,
       "destination": "Chattogram",
       "travel_date": "2023-07-25"
     }
     ```
   - Click Send

## License

[MIT License](LICENSE)
