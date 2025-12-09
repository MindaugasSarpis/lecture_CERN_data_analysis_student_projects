import fastf1
import fastf1.utils
import pandas as pd
import numpy as np
import os

# Enable FastF1 Cache
CACHE_DIR = 'fastf1_cache'
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)
fastf1.Cache.enable_cache(CACHE_DIR)

def get_session_data(year, gp, session_type):
    """Loads a session and returns the session object and laps."""
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()
        return session
    except Exception as e:
        print(f"Error loading session: {e}")
        return None

def format_lap_time(timedelta_val):
    """Formats Timedelta to 1:23.456 string."""
    if pd.isnull(timedelta_val):
        return ""
    total_seconds = timedelta_val.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    return f"{minutes}:{seconds:06.3f}"

def calculate_delta(ref_lap, comp_lap):
    """
    Calculates time delta between two laps based on distance.
    Resamples comp_lap to match ref_lap's distance grid.
    """
    try:
        # Get telemetry
        ref_tel = ref_lap.get_car_data().add_distance()
        comp_tel = comp_lap.get_car_data().add_distance()

        # Create a common distance grid based on the reference lap
        # We assume tracks are roughly similar length; if completely different, this is meaningless
        dist_grid = ref_tel['Distance']
        
        # Interpolate comparison lap time to reference distance
        comp_time_interp = np.interp(dist_grid, comp_tel['Distance'], comp_tel['Time'].dt.total_seconds())
        ref_time_seconds = ref_tel['Time'].dt.total_seconds()
        
        delta = comp_time_interp - ref_time_seconds
        return dist_grid, delta
    except Exception as e:
        print(f"Error calculating delta: {e}")
        return None, None

def get_weather_info(session):
    """Extracts basic weather info."""
    if session.weather_data is None or session.weather_data.empty:
        return "Weather data unavailable"
    
    # Get average conditions
    air_temp = session.weather_data['AirTemp'].mean()
    track_temp = session.weather_data['TrackTemp'].mean()
    humidity = session.weather_data['Humidity'].mean()
    
    return f"Air: {air_temp:.1f}°C | Track: {track_temp:.1f}°C | Humidity: {humidity:.1f}%"