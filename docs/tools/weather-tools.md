# Weather Tools Documentation

Tools for accessing current weather conditions and forecasts worldwide using the Open-Meteo API.

## Overview

The Weather tools provide AI agents with access to real-time weather data and forecasts for any location on Earth. No API key required.

## Installation Requirements

- `httpx` (included in main requirements)
- `python-dotenv` (included in main requirements)

## Environment Variables

None required. Uses the free Open-Meteo API.

## Available Functions

### `get_weather`

Gets current weather conditions and forecast for any location worldwide.

**What it does:**
- Automatically geocodes location names to coordinates
- Provides current temperature, conditions, and wind data
- Returns 48-hour weather forecast in 6-hour intervals
- Translates weather codes to human-readable descriptions
- Supports timezone-aware forecast times

**Parameters:**
- `location` (optional) - City name, address, or location description (default: "Madrid, Spain")

**Returns:**
- Current weather conditions (temperature, description, wind)
- Location coordinates and resolved location name
- 48-hour forecast with timestamps
- Weather condition descriptions
- Temperature and wind speed units

## Supported Locations

- City names: "New York", "London", "Tokyo"
- City with country: "Paris, France", "Sydney, Australia"
- Addresses: "1600 Pennsylvania Avenue, Washington DC"
- Landmarks: "Eiffel Tower, Paris", "Times Square, New York"

## Weather Conditions

The tool provides human-readable weather descriptions including:
- Clear sky, partly cloudy, overcast
- Light/moderate/heavy rain and snow
- Fog and drizzle conditions
- Thunderstorms and severe weather
- Wind and precipitation details

## Use Cases

- Travel planning and destination weather
- Event planning and outdoor activity decisions
- Daily weather briefings and alerts
- Climate research and data collection
- Emergency preparedness and safety planning

## Data Source

- **Open-Meteo API** - Free, high-quality meteorological data
- Global coverage for any coordinates
- Real-time updates with reliable forecasting
- No rate limits or usage restrictions