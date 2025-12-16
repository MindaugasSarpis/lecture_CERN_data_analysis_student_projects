import dash
from dash import dcc, html, Input, Output, State, dash_table, callback_context
import dash_bootstrap_components as dbc
import fastf1
import pandas as pd
import numpy as np

from utils.data_helper import get_session_data, get_weather_info
from components.session_view import create_session_plot, create_lap_info_table
from components.telemetry_view import create_telemetry_plot

# --- App Initialization ---
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG], suppress_callback_exceptions=True)
server = app.server

# --- Global Config ---
YEARS = list(range(2025, 2017, -1))
SESSIONS = ['FP1', 'FP2', 'FP3', 'Q', 'S', 'SQ', 'R']

# --- Layout ---
app.layout = dbc.Container([
    dcc.Store(id='selected-laps-store', storage_type='session', data=[]),
    dcc.Store(id='table-base-style-store', storage_type='memory'),
    
    dbc.Row([
        dbc.Col(html.H2("F1 Data Analysis & Telemetry", className="text-center my-3"), width=12)
    ]),

    dbc.Tabs([
        # --- TAB 1: Session View ---
        dbc.Tab(label="Session View", tab_id="tab-session", children=[
            dbc.Card([
                dbc.CardBody([
                    dbc.Row([
                        dbc.Col(dcc.Dropdown(id='year-dd', options=[{'label': y, 'value': y} for y in YEARS], value=2024, clearable=False, placeholder="Year"), width=2),
                        dbc.Col(dcc.Dropdown(id='gp-dd', placeholder="Grand Prix"), width=3),
                        dbc.Col(dcc.Dropdown(id='session-dd', options=[{'label': s, 'value': s} for s in SESSIONS], value='R', clearable=False, placeholder="Session"), width=2),
                        dbc.Col(dcc.Dropdown(id='drivers-dd', multi=True, placeholder="Select Drivers"), width=3),
                        dbc.Col(dbc.Button("Load Session", id='load-btn', color="primary", className="w-100"), width=2),
                    ], className="mb-3"),
                    
                    dbc.Row([
                        dbc.Col(html.Div(id='weather-info', className="text-info mb-2"), width=12)
                    ]),
                    
                    dcc.Loading(dcc.Graph(id='session-plot'), type="graph"),
                    
                    html.Hr(),
                    html.H5("Lap Details (Click cell to Select | Purple = Session Best | Green = Personal Best)"),
                    dash_table.DataTable(
                        id='laps-table',
                        columns=[],
                        data=[],
                        style_table={'overflowX': 'auto'},
                        style_cell={
                            'backgroundColor': '#222', 'color': 'white', 'textAlign': 'center',
                            'minWidth': '100px', 'width': '100px', 'maxWidth': '100px',
                        },
                        # Basic conditional styling (will be augmented by callback)
                        style_data_conditional=[],
                        active_cell=None
                    )
                ])
            ])
        ]),

        # --- TAB 2: Telemetry View ---
        dbc.Tab(label="Telemetry View", tab_id="tab-telemetry", children=[
            dbc.Card([
                dbc.CardBody([
                    html.H5("Selected Laps for Comparison"),
                    html.Div(id='selected-laps-list', className="mb-3"),
                    dbc.Button("Clear All Selections", id='clear-sel-btn', color="danger", size="sm", className="mb-3"),
                    
                    dcc.Loading(dcc.Graph(id='telemetry-plot', style={'height': '1200px'}), type="graph")
                ])
            ])
        ])
    ], id='tabs', active_tab='tab-session'),

], fluid=True)


# --- Callbacks ---

@app.callback(
    Output('gp-dd', 'options'),
    Input('year-dd', 'value')
)
def update_gp_options(year):
    try:
        schedule = fastf1.get_event_schedule(year)
        events = schedule[schedule['EventName'].notna()]
        return [{'label': f"R{row['RoundNumber']}: {row['EventName']}", 'value': row['EventName']} for _, row in events.iterrows()]
    except:
        return []

@app.callback(
    Output('drivers-dd', 'options'),
    Input('load-btn', 'n_clicks'),
    State('year-dd', 'value'),
    State('gp-dd', 'value'),
    State('session-dd', 'value'),
    prevent_initial_call=True
)
def update_drivers(n_clicks, year, gp, session_type):
    if not n_clicks or not gp: return []
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load(laps=False, telemetry=False, weather=False, messages=False)
        drivers = session.drivers
        options = []
        for d in drivers:
            try:
                info = session.get_driver(d)
                options.append({'label': f"{info['Abbreviation']} ({d})", 'value': info['Abbreviation']})
            except: pass
        return options
    except: return []

# --- Main Render Callback ---
@app.callback(
    [Output('session-plot', 'figure'),
     Output('laps-table', 'data'),
     Output('laps-table', 'columns'),
     Output('weather-info', 'children'),
     Output('table-base-style-store', 'data')],
    Input('load-btn', 'n_clicks'),
    State('year-dd', 'value'),
    State('gp-dd', 'value'),
    State('session-dd', 'value'),
    State('drivers-dd', 'value'),
    prevent_initial_call=True
)
def render_session_view(n_clicks, year, gp, session_type, drivers):
    if not drivers: return {}, [], [], "Select drivers.", []
    
    session = get_session_data(year, gp, session_type)
    if not session: return {}, [], [], "Error loading session.", []
    
    # 1. Create Plot
    fig = create_session_plot(session, drivers)
    
    # 2. Create Table Data
    raw_data = create_lap_info_table(session, drivers) # List of dicts
    if not raw_data: return fig, [], [], "", []

    df = pd.DataFrame(raw_data)

    # 3. Create Pivot Table for Display
    # We combine Time + Compound into one string for the cell
    df['Display'] = df.apply(lambda x: f"{x['Time']} ({x['Compound'][0]})" if pd.notna(x['Compound']) else x['Time'], axis=1)
    
    # Pivot: Index=Lap, Columns=Driver
    pivot_df = df.pivot(index='Lap', columns='Driver', values='Display')
    pivot_df.reset_index(inplace=True)
    pivot_df.fillna('-', inplace=True)
    
    # 4. Prepare Columns
    columns = [{'name': 'Lap', 'id': 'Lap'}] + [{'name': d, 'id': d} for d in drivers]
    data = pivot_df.to_dict('records')

    # 5. Calculate Styles (Purple/Green highlights)
    style_conditions = []
    
    # We need to map the "Status" back to the pivot table cells.
    # We iterate through the raw df to find which (Driver, Lap) pairs are PURPLE or GREEN
    for _, row in df.iterrows():
        if row['Status'] == 'PURPLE':
            style_conditions.append({
                'if': {'filter_query': f"{{Lap}} = {row['Lap']}", 'column_id': row['Driver']},
                'backgroundColor': '#6A00FF', # Purple
                'color': 'white',
                'fontWeight': 'bold'
            })
        elif row['Status'] == 'GREEN':
             style_conditions.append({
                'if': {'filter_query': f"{{Lap}} = {row['Lap']}", 'column_id': row['Driver']},
                'color': '#00FF00', # Green text for personal best
                'fontWeight': 'bold'
            })

    return fig, data, columns, get_weather_info(session), style_conditions

# --- Lap Selection & Caching ---
@app.callback(
    Output('selected-laps-store', 'data'),
    Input('laps-table', 'active_cell'),
    Input('clear-sel-btn', 'n_clicks'),
    State('laps-table', 'data'),
    State('selected-laps-store', 'data'),
    State('year-dd', 'value'),
    State('gp-dd', 'value'),
    State('session-dd', 'value'),
    prevent_initial_call=True
)
def manage_selected_laps(active_cell, clear_clicks, table_data, current_store, year, gp, ses):
    ctx = callback_context
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if trigger_id == 'clear-sel-btn':
        return []

    if active_cell and table_data:
        # Determine Driver and Lap from the clicked cell
        row = table_data[active_cell['row']]
        driver = active_cell['column_id']
        lap_number = row['Lap']
        
        # Validation: Ignore clicks on "Lap" column or empty cells
        if driver == 'Lap' or row[driver] == '-':
            return current_store

        lap_time_display = row[driver]
        
        # Unique ID for cache
        item_id = f"{year}-{gp}-{ses}-{driver}-{lap_number}"
        
        # Check if already exists
        if any(x['id'] == item_id for x in current_store):
            return current_store

        # Fetch Official Team Color
        # We load a lightweight session to get driver info
        try:
            session = fastf1.get_session(year, gp, ses)
            session.load(laps=False, telemetry=False, weather=False, messages=False)
            drv_info = session.get_driver(driver)
            team_color = '#' + drv_info.get('TeamColor', 'FFFFFF')
            team_name = drv_info.get('TeamName', 'Unknown')
        except:
            team_color = '#FFFFFF'
            team_name = 'Unknown'
        
        # Logic: If a teammate is already selected, use White (or a secondary color) to distinguish
        # Check if any existing selected lap has the same team
        teammate_exists = any(x['team'] == team_name for x in current_store)
        
        final_color = team_color
        if teammate_exists:
             final_color = '#FFFFFF' # Force white for contrast against teammate

        current_store.append({
            'id': item_id,
            'year': year, 'gp': gp, 'session': ses,
            'driver': driver, 'lap_number': lap_number,
            'lap_time': lap_time_display,
            'color': final_color,
            'team': team_name
        })
            
    return current_store

# --- Apply Styles to Table based on Selection ---
@app.callback(
    Output('laps-table', 'style_data_conditional'),
    Input('selected-laps-store', 'data'),
    Input('table-base-style-store', 'data')
)
def update_table_styles(selected_laps, base_styles):
    # Start with the base styles (Purple/Green highlights)
    styles = base_styles.copy() if base_styles else []
    
    # Add styles for currently selected laps (Border/Background)
    for item in selected_laps:
        styles.append({
            'if': {
                'filter_query': f"{{Lap}} = {item['lap_number']}",
                'column_id': item['driver']
            },
            'border': f'3px solid {item["color"]}',
            'backgroundColor': '#333' # Slight highlight to show selection
        })
    return styles

# --- Telemetry View ---
@app.callback(
    [Output('telemetry-plot', 'figure'),
     Output('selected-laps-list', 'children')],
    Input('tabs', 'active_tab'),
    Input('selected-laps-store', 'data'),
    prevent_initial_call=True
)
def update_telemetry_view(active_tab, stored_laps):
    if active_tab != 'tab-telemetry':
        return dash.no_update, dash.no_update
        
    if not stored_laps:
        return {}, "No laps selected."

    # Badge List
    badges = []
    for item in stored_laps:
        # Determine text color for badge
        txt_col = 'black' if item['color'].upper() in ['#FFFFFF', '#FFF'] else 'white'
        badges.append(dbc.Badge(
            f"{item['driver']} {item['gp']} L{item['lap_number']}",
            style={'backgroundColor': item['color'], 'color': txt_col, 'fontSize': '14px'},
            className="me-2 p-2"
        ))

    # Plot Data Preparation
    laps_to_plot = []
    for item in stored_laps:
        try:
            # Full load for telemetry
            session = fastf1.get_session(item['year'], item['gp'], item['session'])
            session.load(laps=True, telemetry=True, weather=False, messages=False)
            
            d_laps = session.laps.pick_driver(item['driver'])
            lap_obj = d_laps[d_laps['LapNumber'] == item['lap_number']].iloc[0]
            
            laps_to_plot.append({
                'driver': item['driver'],
                'lap_object': lap_obj,
                'color': item['color'],
                'session_name': f"{item['year']} {item['gp']}"
            })
        except Exception as e:
            print(f"Error plotting {item['driver']}: {e}")

    fig = create_telemetry_plot(laps_to_plot)
    return fig, badges

if __name__ == '__main__':
    app.run(debug=True, port=8034)