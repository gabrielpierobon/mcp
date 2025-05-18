from typing import Dict, Any
import httpx
import datetime

async def get_weather(location: str = "Madrid, Spain") -> Dict[str, Any]:
    """
    Get the current and forecast weather for any location in the world.
    
    Args:
        location: City name or address (e.g., "New York", "Tokyo, Japan", "Paris, France")
                 Defaults to "Madrid, Spain" if not specified
    
    Returns:
        Weather data including current temperature and forecast
    """
    print(f"INFO: Fetching weather data for location: {location}")
    
    try:
        # Step 1: Geocode the location (convert location name to coordinates)
        geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1&language=en&format=json"
        
        async with httpx.AsyncClient() as client:
            # Get coordinates for the location
            geocode_response = await client.get(geocoding_url, timeout=10.0)
            geocode_response.raise_for_status()
            geocode_data = geocode_response.json()
            
            if not geocode_data.get("results"):
                return {
                    "error": f"Could not find location: {location}",
                    "status": "error"
                }
            
            # Extract coordinates and location name
            result = geocode_data["results"][0]
            latitude = result["latitude"]
            longitude = result["longitude"]
            location_name = f"{result.get('name', '')}, {result.get('country', '')}"
            
            # Step 2: Get weather data using coordinates
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,weathercode&current_weather=true&timezone=auto"
            
            weather_response = await client.get(weather_url, timeout=10.0)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            
            # Process the weather data
            current_weather = weather_data.get("current_weather", {})
            hourly = weather_data.get("hourly", {})
            utc_offset_seconds = weather_data.get("utc_offset_seconds", 0) # Get UTC offset for the location
            forecast_timezone = datetime.timezone(datetime.timedelta(seconds=utc_offset_seconds)) # Create timezone object
            
            # Create a more readable description of the weather code
            weather_codes = {
                0: "Clear sky",
                1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Fog", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
                80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
            }
            
            current_code = current_weather.get("weathercode")
            current_condition = weather_codes.get(current_code, "Unknown")
            
            # Get forecast for next 24 hours (in 6-hour intervals)
            forecast = []
            if "time" in hourly and "temperature_2m" in hourly and "weathercode" in hourly:
                times = hourly["time"]
                temperatures = hourly["temperature_2m"]
                weather_codes_hourly = hourly["weathercode"]
                
                now_dt = datetime.datetime.now(datetime.timezone.utc) # Use timezone-aware now
                
                # Start from the nearest upcoming hour
                start_index = 0
                for i, time_str in enumerate(times):
                    # time_str from API is naive local time for the forecast location
                    naive_time_obj = datetime.datetime.fromisoformat(time_str)
                    # Make it offset-aware using the location's timezone
                    aware_time_obj_local = naive_time_obj.replace(tzinfo=forecast_timezone)
                    
                    if aware_time_obj_local > now_dt: # Compare aware local time with aware UTC time
                        start_index = i
                        break
                
                # Create forecast entries
                for i in range(start_index, min(start_index + 48, len(times)), 6):
                    if i < len(times):
                        current_forecast_naive_time = datetime.datetime.fromisoformat(times[i])
                        current_forecast_aware_local_time = current_forecast_naive_time.replace(tzinfo=forecast_timezone)
                        
                        weather_code = weather_codes_hourly[i]
                        weather_desc = weather_codes.get(weather_code, "Unknown")
                        
                        forecast.append({
                            "time": current_forecast_aware_local_time.strftime("%Y-%m-%d %H:%M %z"), # Format with UTC offset
                            "temperature": temperatures[i],
                            "condition": weather_desc
                        })
            
            return {
                "location": location_name,
                "coordinates": {"latitude": latitude, "longitude": longitude},
                "current_weather": {
                    "temperature": current_weather.get("temperature"),
                    "condition": current_condition,
                    "wind_speed": current_weather.get("windspeed"),
                    "units": {
                        "temperature": weather_data.get("hourly_units", {}).get("temperature_2m", "°C"),
                        "wind_speed": weather_data.get("current_weather_units", {}).get("windspeed", "km/h")
                    }
                },
                "forecast": forecast,
                "source": "Open-Meteo API",
                "status": "success"
            }
            
    except httpx.HTTPStatusError as e:
        error_message = f"API request failed (HTTP {e.response.status_code}): {e.response.text}"
        print(f"ERROR: {error_message}")
        return {
            "error": error_message,
            "status": "error"
        }
    except httpx.RequestError as e:
        error_message = f"Request failed: {str(e)}"
        print(f"ERROR: {error_message}")
        return {
            "error": error_message,
            "status": "error"
        }
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        print(f"ERROR: {error_message}")
        return {
            "error": error_message,
            "status": "error"
        }

def register(mcp_instance):
    mcp_instance.tool()(get_weather) 