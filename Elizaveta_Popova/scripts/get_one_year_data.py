import requests
import csv
import json
import os
import sys
from datetime import datetime, timedelta

def check_existing_file(filename):
    """
    Check if file exists and give user options
    """
    if os.path.exists(filename):
        print(f"\n⚠️  File '{filename}' already exists!")
        print("What would you like to do?")
        print("1. Overwrite the existing file")
        print("2. Create a new file with a different name")
        print("3. Append data to the existing file")
        print("4. Cancel the operation")
        
        while True:
            choice = input("Enter your choice (1-4): ").strip()
            if choice == '1':
                return 'overwrite'
            elif choice == '2':
                new_name = input("Enter new filename: ").strip()
                if not new_name.endswith('.csv'):
                    new_name += '.csv'
                return ('rename', new_name)
            elif choice == '3':
                return 'append'
            elif choice == '4':
                return 'cancel'
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
    else:
        return 'proceed'

def save_to_csv(data, filename, mode='w'):
    """
    Save flattened data to CSV file with different modes
    """
    if not data:
        print("No data to save.")
        return False
    
    # Define CSV headers
    fieldnames = [
        'date', 'id', 'name', 'nasa_jpl_url', 'absolute_magnitude_h',
        'is_potentially_hazardous', 'is_sentry_object',
        'estimated_diameter_min_km', 'estimated_diameter_max_km',
        'close_approach_date', 'close_approach_date_full',
        'relative_velocity_km_s', 'miss_distance_astronomical',
        'miss_distance_km', 'orbiting_body', 'orbit_class_type',
        'orbit_class_description', 'eccentricity', 'semi_major_axis_au',
        'inclination_deg', 'orbital_period_days', 'perihelion_distance_au',
        'aphelion_distance_au'
    ]
    
    try:
        with open(filename, mode, newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # Write header only if not appending or file is empty
            if mode == 'w' or csvfile.tell() == 0:
                writer.writeheader()
            
            writer.writerows(data)
        
        print(f"Data successfully saved to {filename}")
        print(f"Total records: {len(data)}")
        return True
    except Exception as e:
        print(f"Error saving to CSV: {e}")
        return False

def fetch_neo_data_for_date_range(api_key, start_date, end_date):
    """
    Fetch NEO data for a date range, handling the 7-day limit per API call
    """
    all_data = {
        'near_earth_objects': {},
        'element_count': 0
    }
    
    current_start = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    while current_start <= end_date:
        # Calculate end date for this batch (max 7 days from start)
        current_end = current_start + timedelta(days=6)
        if current_end > end_date:
            current_end = end_date
        
        batch_start = current_start.strftime('%Y-%m-%d')
        batch_end = current_end.strftime('%Y-%m-%d')
        
        print(f"Fetching data from {batch_start} to {batch_end}...")
        
        batch_data = fetch_neo_data(api_key, batch_start, batch_end)
        
        if batch_data:
            # Merge the data
            if 'near_earth_objects' in batch_data:
                all_data['near_earth_objects'].update(batch_data['near_earth_objects'])
            all_data['element_count'] += batch_data.get('element_count', 0)
        
        # Move to next batch
        current_start = current_end + timedelta(days=1)
    
    return all_data

def fetch_neo_data(api_key, start_date, end_date):
    """
    Fetch Near Earth Object data from NASA API for a single date range
    """
    url = "https://api.nasa.gov/neo/rest/v1/feed"
    
    params = {
        'start_date': start_date,
        'end_date': end_date,
        'detailed': 'true',
        'api_key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {start_date} to {end_date}: {e}")
        return None

def safe_get(data, keys, default=''):
    """
    Safely get nested dictionary values
    """
    try:
        for key in keys:
            data = data[key]
        return data
    except (KeyError, TypeError, IndexError):
        return default

def flatten_neo_data(neo_data):
    """
    Flatten the nested NEO data structure into a list of dictionaries
    """
    flattened_data = []
    
    # Iterate through each date in the near_earth_objects
    for date, neo_list in neo_data['near_earth_objects'].items():
        for neo in neo_list:
            # Extract basic information
            record = {
                'date': date,
                'id': safe_get(neo, ['id']),
                'name': safe_get(neo, ['name']),
                'nasa_jpl_url': safe_get(neo, ['nasa_jpl_url']),
                'absolute_magnitude_h': safe_get(neo, ['absolute_magnitude_h']),
                'is_potentially_hazardous': safe_get(neo, ['is_potentially_hazardous_asteroid'], False),
                'is_sentry_object': safe_get(neo, ['is_sentry_object'], False),
                
                # Estimated diameter in kilometers
                'estimated_diameter_min_km': safe_get(neo, ['estimated_diameter', 'kilometers', 'estimated_diameter_min']),
                'estimated_diameter_max_km': safe_get(neo, ['estimated_diameter', 'kilometers', 'estimated_diameter_max']),
                
                # Close approach data (taking first approach if multiple exist)
                'close_approach_date': safe_get(neo, ['close_approach_data', 0, 'close_approach_date']),
                'close_approach_date_full': safe_get(neo, ['close_approach_data', 0, 'close_approach_date_full']),
                'relative_velocity_km_s': safe_get(neo, ['close_approach_data', 0, 'relative_velocity', 'kilometers_per_second']),
                'miss_distance_astronomical': safe_get(neo, ['close_approach_data', 0, 'miss_distance', 'astronomical']),
                'miss_distance_km': safe_get(neo, ['close_approach_data', 0, 'miss_distance', 'kilometers']),
                'orbiting_body': safe_get(neo, ['close_approach_data', 0, 'orbiting_body']),
                
                # Orbital data (with safe access)
                'orbit_class_type': safe_get(neo, ['orbital_data', 'orbit_class', 'orbit_class_type']),
                'orbit_class_description': safe_get(neo, ['orbital_data', 'orbit_class', 'orbit_class_description']),
                'eccentricity': safe_get(neo, ['orbital_data', 'eccentricity']),
                'semi_major_axis_au': safe_get(neo, ['orbital_data', 'semi_major_axis']),
                'inclination_deg': safe_get(neo, ['orbital_data', 'inclination']),
                'orbital_period_days': safe_get(neo, ['orbital_data', 'orbital_period']),
                'perihelion_distance_au': safe_get(neo, ['orbital_data', 'perihelion_distance']),
                'aphelion_distance_au': safe_get(neo, ['orbital_data', 'aphelion_distance'])
            }
            flattened_data.append(record)
    
    return flattened_data

def save_sentry_objects(data, original_filename):
    """
    Create a new CSV file containing only sentry objects
    """
    if not data:
        print("No data to filter for sentry objects.")
        return
    
    # Filter for sentry objects
    sentry_data = [item for item in data if item.get('is_sentry_object')]
    
    if not sentry_data:
        print("No sentry objects found in the data.")
        return
    
    sentry_filename = original_filename.replace(".csv", "_sentry.csv")
    
    # Define CSV headers (same as original)
    fieldnames = [
        'date', 'id', 'name', 'nasa_jpl_url', 'absolute_magnitude_h',
        'is_potentially_hazardous', 'is_sentry_object',
        'estimated_diameter_min_km', 'estimated_diameter_max_km',
        'close_approach_date', 'close_approach_date_full',
        'relative_velocity_km_s', 'miss_distance_astronomical',
        'miss_distance_km', 'orbiting_body', 'orbit_class_type',
        'orbit_class_description', 'eccentricity', 'semi_major_axis_au',
        'inclination_deg', 'orbital_period_days', 'perihelion_distance_au',
        'aphelion_distance_au'
    ]
    
    try:
        with open(sentry_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(sentry_data)
        
        print(f"\n✓ Sentry objects saved to: {sentry_filename}")
        print(f"  Total sentry objects: {len(sentry_data)}")
            
    except Exception as e:
        print(f"Error saving sentry objects: {e}")

def print_summary(data):
    """
    Print a summary of the collected data
    """
    if not data:
        return
    
    hazardous_count = sum(1 for item in data if item['is_potentially_hazardous'])
    sentry_count = sum(1 for item in data if item['is_sentry_object'])
    
    # Get date range
    dates = sorted(set(item['date'] for item in data))
    
    print(f"\nSummary:")
    print(f"Date range: {dates[0]} to {dates[-1]}")
    print(f"Total NEOs: {len(data)}")
    print(f"Unique dates: {len(dates)}")
    print(f"Potentially hazardous: {hazardous_count}")
    print(f"Sentry objects: {sentry_count}")

def main():
    # Configuration
    API_KEY = "6ZpPKIgsSZP6dapx1Olb5Gf1OFL0pGLfDUQV2NVp"
    
    if len(sys.argv) < 3:
        print("Usage: python script.py <start_date> <end_date>")
        print("Example: python script.py 2024-11-22 2025-11-22")
        sys.exit(1)
    
    START_DATE = sys.argv[1]
    END_DATE = sys.argv[2]

    try:
        datetime.strptime(START_DATE, '%Y-%m-%d')
        datetime.strptime(END_DATE, '%Y-%m-%d')
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        sys.exit(1)

    OUTPUT_FILENAME = os.path.join("data", f"neo_data_{START_DATE}_to_{END_DATE}.csv")
    
    print(f"Fetching NEO data from {START_DATE} to {END_DATE}...")
    print("This may take a while for a full year of data...")
    
    # Check if file exists and get user preference
    file_action = check_existing_file(OUTPUT_FILENAME)
    
    if file_action == 'cancel':
        print("Operation cancelled.")
        return
    
    # Determine filename and mode
    if file_action == 'overwrite':
        filename = OUTPUT_FILENAME
        mode = 'w'
        print("Overwriting existing file...")
    elif file_action[0] == 'rename':
        filename = file_action[1]
        mode = 'w'
        print(f"Creating new file: {filename}")
    elif file_action == 'append':
        filename = OUTPUT_FILENAME
        mode = 'a'
        print("Appending to existing file...")
    else:  # 'proceed'
        filename = OUTPUT_FILENAME
        mode = 'w'
    
    # Fetch data from NASA API for the entire date range
    neo_data = fetch_neo_data_for_date_range(API_KEY, START_DATE, END_DATE)
    
    if neo_data and neo_data['near_earth_objects']:
        print(f"Successfully fetched data. Total element count: {neo_data['element_count']}")
        
        # Flatten the nested data structure
        flattened_data = flatten_neo_data(neo_data)
        
        # Save to CSV with the chosen mode
        success = save_to_csv(flattened_data, filename, mode)

        # Save sentry objects to a separate CSV
        save_sentry_objects(flattened_data, filename)
        
        if success:
            # Print summary
            print_summary(flattened_data)
            
            # Print a sample record
            if flattened_data:
                print("\nSample record:")
                sample = flattened_data[0].copy()
                # Convert boolean values to strings for better display
                for key, value in sample.items():
                    if isinstance(value, bool):
                        sample[key] = str(value)
                print(json.dumps(sample, indent=2))
    else:
        print("Failed to fetch data from NASA API.")

if __name__ == "__main__":
    main()