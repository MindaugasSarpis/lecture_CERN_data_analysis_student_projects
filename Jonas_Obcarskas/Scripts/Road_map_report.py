import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

import networkx as nx
import osmnx as ox
import folium
import concurrent.futures
from tqdm.auto import tqdm
from branca.colormap import LinearColormap

from geopy.distance import great_circle
from shapely.geometry import LineString
import math

import requests
from dataclasses import dataclass, asdict
import json
from time import sleep
import webbrowser
import os

HEADERS = {
    "User-Agent": "road-conditions-script/1.0 jonasobc@email.com"
}

# Global maximum badness score (keep in sync with scoring function)
BADNESS_MAX = 10
# ------------------Input Points ------------------
points = []
first_point = input("Enter the starting point address: ")
points.append(first_point)
while True:
    nxt = input("Enter next point address (or '.' to finish): ")
    if nxt.strip() == '.':
        break
    if nxt.strip() == '':
        continue
    points.append(nxt)

# Geocode all provided points
coords_list = [ox.geocode(p) for p in points]

start_point_name = points[0]
end_point_name = points[-1]
start_coords = coords_list[0]
end_coords = coords_list[-1]

print("Geocoded points:")
for name, coord in zip(points, coords_list):
    print(f" - {name}: {coord}")


dist_coverage = 20000  # meters

waypoints = []
total_distance = 0.0
total_segments = 0

for idx in range(len(coords_list) - 1):
    a = coords_list[idx]
    b = coords_list[idx + 1]
    seg_dist = great_circle(a, b).meters
    total_distance += seg_dist

    num_segments = max(1, math.ceil(seg_dist / dist_coverage))
    total_segments += num_segments

    line = LineString([
        (a[1], a[0]),
        (b[1], b[0])
    ])

    for i in range(num_segments + 1):
        fraction = i / num_segments
        point = line.interpolate(fraction, normalized=True)
        waypoints.append((point.y, point.x))

print(f"Total path direct distance (sum of segments): {total_distance:.2f} meters")
print(f"dist_coverage: {dist_coverage} meters")
print(f"Total waypoint segments generated: {total_segments}")

# ------------------ Download and Combine Graphs ------------------
graphs = []

def download_and_simplify_graph(waypoint, dist_coverage, network_type):
    graph = ox.graph_from_point(waypoint, dist=dist_coverage, network_type=network_type)
    return graph

with concurrent.futures.ThreadPoolExecutor() as executor:
    graphs = list(tqdm(executor.map(lambda wp: download_and_simplify_graph(wp, dist_coverage, 'drive'), waypoints), total=len(waypoints), desc="Downloading and simplifying graphs"))

combined_graph = nx.compose_all(graphs)
print("All individual graphs generated and combined into a single graph.")

combined_graph = ox.add_edge_speeds(combined_graph) #....................................
combined_graph = ox.add_edge_travel_times(combined_graph) #....................................

# ------------------  Find Nearest Nodes and Calculate Shortest Path ------------------
# For multiple points, compute shortest path between each consecutive pair and concatenate
full_route_nodes = []
total_travel_time = 0.0
for i in range(len(coords_list) - 1):
    a = coords_list[i]
    b = coords_list[i+1]
    origin_node = ox.distance.nearest_nodes(combined_graph, a[1], a[0])
    dest_node = ox.distance.nearest_nodes(combined_graph, b[1], b[0])

    print(f"Computing segment {i+1}: {points[i]} -> {points[i+1]}")
    try:
        path = nx.shortest_path(combined_graph, origin_node, dest_node, weight='travel_time', method='dijkstra')
        path_len = nx.shortest_path_length(combined_graph, origin_node, dest_node, weight='travel_time', method='dijkstra')
    except nx.NetworkXNoPath:
        print(f"Warning: no path found between '{points[i]}' and '{points[i+1]}'. Skipping segment.")
        continue

    # concatenate without duplicating connecting node
    if full_route_nodes and path[0] == full_route_nodes[-1]:
        full_route_nodes.extend(path[1:])
    else:
        full_route_nodes.extend(path)

    total_travel_time += path_len

route_combined = full_route_nodes
route_travel_time_combined_s = total_travel_time
print(f"Total travel time (combined segments): {route_travel_time_combined_s:.2f} (units)")

# ------------------ 5. Weather Data Models and Logic ------------------
@dataclass
class WeatherData:
    temperature_c: float
    precipitation_mm_h: float
    visibility_m: int

@dataclass
class RoadConditions:
    snow_on_roads: bool
    water_on_roads: bool
    foggy: bool
    very_rainy: bool
    rainy: bool
    icy: bool

def evaluate_road_conditions(w: WeatherData) -> RoadConditions:
    # Be more sensitive: raise freezing threshold, use graded precipitation thresholds
    is_freezing = w.temperature_c <= 1.0  # slightly above 0°C to catch near-freezing conditions
    precip = w.precipitation_mm_h

    # Precipitation tiers (mm/h)
    very_rainy_condition = precip >= 5.0
    water_on_roads_condition = precip >= 1.0
    light_precip_condition = precip >= 0.1

    # Rain vs snow/ice
    rainy_condition = (not is_freezing) and light_precip_condition
    snow_on_roads_condition = is_freezing and light_precip_condition
    
    # Icy is flagged when temperature is around freezing and there is at least light moisture
    icy_condition = (w.temperature_c <= 2.0) and (precip > 0)

    # More sensitive fog threshold
    foggy_condition = w.visibility_m < 3000

    return RoadConditions(
        snow_on_roads = snow_on_roads_condition,
        water_on_roads = water_on_roads_condition,
        foggy = foggy_condition,
        very_rainy = very_rainy_condition,
        rainy = rainy_condition,
        icy = icy_condition
    )

def get_weather_metno(lat: float, lon: float) -> WeatherData:
    url = "https://api.met.no/weatherapi/locationforecast/2.0/compact"
    params = {"lat": lat, "lon": lon}

    r = requests.get(url, params=params, headers=HEADERS, timeout=10)
    r.raise_for_status()
    data = r.json()

    now = data["properties"]["timeseries"][0]["data"]
    instant = now["instant"]["details"]
    next_1h = now.get("next_1_hours", {}).get("details", {})

    return WeatherData(
        temperature_c = instant["air_temperature"],
        precipitation_mm_h = next_1h.get("precipitation_amount", 0.0),
        visibility_m = instant.get("visibility", 10000)
    )

def check_waypoints(waypoints):
    results = []

    for lat, lon in waypoints:
        weather = get_weather_metno(lat, lon)
        conditions = evaluate_road_conditions(weather)

        results.append({
            "lat": lat,
            "lon": lon,
            "conditions": conditions
        })

        sleep(0.5)

    return results

print('Weather conditions for waypoints:')
results = check_waypoints(waypoints)
for r in results:
    print(r)
print('Weather data collection complete.')

# ------------------ 6. Define Badness Score and Color Functions ------------------
def get_badness_score(rc) -> int:
    # Use more sensitive weights to reflect severity
    score = 0
    if rc.snow_on_roads:
        score += 6
    if rc.icy:
        score += 5
    if rc.very_rainy:
        score += 4
    if rc.water_on_roads:
        score += 3
    if rc.rainy:
        score += 2
    if rc.foggy:
        score += 1
    return score

def get_color_from_score(badness_score: int) -> str:
    # Normalize score to [0, 1]
    normalized_score = min(max(badness_score, 0), BADNESS_MAX) / BADNESS_MAX

    cmap = plt.get_cmap('RdYlGn_r')
    rgba = cmap(normalized_score)

    # Convert RGBA (0-1 floats) to hex string
    return mcolors.to_hex(rgba)

# ------------------ 7. Visualize Route with Weather-Based Coloring ------------------
# Center the map on the average of all provided coordinates
lat_sum = sum(c[0] for c in coords_list)
lon_sum = sum(c[1] for c in coords_list)
center_point = (
    lat_sum / len(coords_list),
    lon_sum / len(coords_list)
)

m = folium.Map(
    location=center_point,
    zoom_start=11,
    tiles='cartodbpositron',
    zoom_control=True,
    scrollWheelZoom=True,
    dragging=True
)

folium.Marker(
    location=start_coords,
    popup=start_point_name,
    icon=folium.Icon(color='green')
).add_to(m)

# Add intermediate point markers (if any)
for mid_name, mid_coord in zip(points[1:-1], coords_list[1:-1]):
    folium.Marker(
        location=mid_coord,
        popup=mid_name,
        icon=folium.Icon(color='blue', icon='info-sign')
    ).add_to(m)

folium.Marker(
    location=end_coords,
    popup=end_point_name,
    icon=folium.Icon(color='red')
).add_to(m)

route_coordinates = []
for node_id in route_combined:
    node = combined_graph.nodes[node_id]
    route_coordinates.append((node['y'], node['x']))

waypoint_conditions_map = {wp: res['conditions'] for wp, res in zip(waypoints, results)}

for i in range(len(route_coordinates) - 1):
    segment_start = route_coordinates[i]
    segment_end = route_coordinates[i+1]

    segment_midpoint_lat = (segment_start[0] + segment_end[0]) / 2
    segment_midpoint_lon = (segment_start[1] + segment_end[1]) / 2
    segment_midpoint = (segment_midpoint_lat, segment_midpoint_lon)

    nearest_waypoint = None
    min_distance = float('inf')

    for wp in waypoints:
        dist = great_circle(segment_midpoint, wp).meters
        if dist < min_distance:
            min_distance = dist
            nearest_waypoint = wp

    conditions = waypoint_conditions_map.get(nearest_waypoint, RoadConditions(False, False, False, False, False, False))

    badness_score = get_badness_score(conditions)
    segment_color = get_color_from_score(badness_score)

    folium.PolyLine(
        locations=[segment_start, segment_end],
        color=segment_color,
        weight=5,
        opacity=0.9
    ).add_to(m)

# Add a continuous legend/colorbar that matches the RdYlGn_r colormap used above
cmap = plt.get_cmap('RdYlGn_r')
# sample colormap across the range [0, BADNESS_MAX]
color_steps = [mcolors.to_hex(cmap(i / BADNESS_MAX)) for i in range(BADNESS_MAX + 1)]
colormap = LinearColormap(colors=color_steps, vmin=0, vmax=BADNESS_MAX, caption='Road badness (0 green → high red)')
colormap.add_to(m)

# Fit map bounds to the full route
m.fit_bounds(folium.PolyLine(locations=route_coordinates).get_bounds())

# ------------------ 8. Save the Interactive Map ------------------
# Sanitize city names for filename
start_clean = ''.join(c for c in start_point_name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')
end_clean = ''.join(c for c in end_point_name if c.isalnum() or c in (' ', '-', '_')).rstrip().replace(' ', '_')

# Determine base directory (script dir) and ensure Results folder exists
base_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
results_dir = os.path.normpath(os.path.join(base_dir, '..', 'Results'))
os.makedirs(results_dir, exist_ok=True)

filename = os.path.join(results_dir, f"weather_route_map_{start_clean}-{end_clean}.html")
m.save(filename)

weather_results = os.path.join(results_dir, f"weather_results_{start_clean}-{end_clean}.json")
# Serialize waypoint weather results to JSON
weather_output = []
for r in results:
    cond = r.get('conditions')
    # convert dataclass to dict for JSON serialization
    cond_dict = asdict(cond) if cond is not None else None
    weather_output.append({
        'lat': r.get('lat'),
        'lon': r.get('lon'),
        'conditions': cond_dict
    })

with open(weather_results, 'w', encoding='utf-8') as f:
    json.dump(weather_output, f, indent=2, ensure_ascii=False)

print(f"Interactive map saved to '{filename}'")

# Open the map in the default browser
file_path = os.path.abspath(filename)
webbrowser.open(f'file://{file_path}')
print("Opening map in browser...")