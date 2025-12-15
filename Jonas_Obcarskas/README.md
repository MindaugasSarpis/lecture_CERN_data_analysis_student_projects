**Running the script**

Follow the prompts:

- Enter the starting address.
- Enter additional intermediate addresses one at a time.
- Enter `.` to finish and start processing.

**Outputs**

- The interactive map HTML will be saved to `../Results/weather_route_map_<start>-<end>.html` (relative to `Scripts/`).
- Weather and condition data are written to `../Results/weather_results_<start>-<end>.json`.

**Configuration and tuning**

- `dist_coverage` (in `Road_map_report.py`) controls how large each downloaded OSM graph is (default 20000 m). Increase it if the graph doesn't cover long segments.
- `BADNESS_MAX` and the scoring function determine the color scale (green→red). Adjust weights in `get_badness_score` to tune sensitivity.

**Troubleshooting**

- If geocoding fails for an address, check the spelling or try a more specific address (city, street).
