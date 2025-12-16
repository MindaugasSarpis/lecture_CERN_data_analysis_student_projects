import requests
import csv
import json
import os
import sys
from datetime import datetime

def check_existing_file(filename):
    """
    Check if file exists and give user options
    """
    if os.path.exists(filename):
        print(f"\n⚠️  File '{filename}' already exists!")
        print("What would you like to do?")
        print("1. Overwrite the existing file")
        print("2. Create a new file with a different name")
        print("3. Cancel the operation")
        
        while True:
            choice = input("Enter your choice (1-3): ").strip()
            if choice == '1':
                return 'overwrite'
            elif choice == '2':
                new_name = input("Enter new filename: ").strip()
                if not new_name.endswith('.csv'):
                    new_name += '.csv'
                return ('rename', new_name)
            elif choice == '3':
                return 'cancel'
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    else:
        return 'proceed'
    
def save_to_csv(data, filename):
    """
    Save flattened data to CSV file
    """
    if not data:
        print("No data to save.")
        return
    
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
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"Data successfully saved to {filename}")
        print(f"Total records: {len(data)}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def fetch_neo_data(api_key, start_date, end_date):
    """
    Fetch Near Earth Object data from NASA API
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
        print(f"Error fetching data: {e}")
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
    
    print(f"\nSummary:")
    print(f"Total NEOs: {len(data)}")
    print(f"Potentially hazardous: {hazardous_count}")
    print(f"Sentry objects: {sentry_count}")

def main():
    # Configuration
    API_KEY = "6ZpPKIgsSZP6dapx1Olb5Gf1OFL0pGLfDUQV2NVp"  
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <start_date>")
        print("Example: python script.py 2025-11-22")
        sys.exit(1)
    
    START_DATE = sys.argv[1]
    END_DATE = START_DATE

    try:
        datetime.strptime(START_DATE, '%Y-%m-%d')
        datetime.strptime(END_DATE, '%Y-%m-%d')
    except ValueError:
        print("Error: Dates must be in YYYY-MM-DD format")
        sys.exit(1)

    OUTPUT_FILENAME = os.path.join("data", f"neo_data_{START_DATE}.csv")
    
    # Check if file exists FIRST, before fetching any data
    file_action = check_existing_file(OUTPUT_FILENAME)
    
    if file_action == 'cancel':
        print("Operation cancelled.")
        return
    
    # Determine filename based on user choice
    if file_action == 'overwrite':
        filename = OUTPUT_FILENAME
        print("Overwriting existing file...")
    elif file_action[0] == 'rename':
        filename = file_action[1]
        print(f"Creating new file: {filename}")
    else:  # 'proceed'
        filename = OUTPUT_FILENAME
    
    print("Fetching NEO data from NASA API...")
    
    # Fetch data from NASA API
    neo_data = fetch_neo_data(API_KEY, START_DATE, END_DATE)
    
    if neo_data:
        print(f"Successfully fetched data. Element count: {neo_data['element_count']}")
        
        # Flatten the nested data structure
        flattened_data = flatten_neo_data(neo_data)
        
        # Save to CSV
        save_to_csv(flattened_data, filename)

        # Save sentry objects to a separate CSV
        save_sentry_objects(flattened_data, filename)
        
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