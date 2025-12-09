import plotly.graph_objs as go
import pandas as pd
import fastf1
import fastf1.plotting
from utils.data_helper import format_lap_time

def create_session_plot(session, drivers):
    """
    Plots Lap Time vs Lap Number for selected drivers.
    - Uses Official Team Colors.
    - Highlights the fastest lap for EACH driver with a star.
    """
    fig = go.Figure()
    
    # Ensure FastF1 plotting features are enabled
    fastf1.plotting.setup_mpl(misc_mpl_mods=False)
    
    for driver in drivers:
        try:
            # Get driver data
            driver_laps = session.laps.pick_driver(driver)
            if driver_laps.empty:
                continue
            
            # 1. GET TEAM COLOR
            try:
                drv_info = session.get_driver(driver)
                # Try getting team color via plotting helper
                color = fastf1.plotting.get_team_color(drv_info['TeamName'], session=session)
            except:
                # Fallback
                try:
                    color = '#' + session.get_driver(driver)['TeamColor']
                except:
                    color = '#FFFFFF'
            
            # Validate color
            if not color or pd.isna(color): 
                color = '#FFFFFF'

            # 2. FILTER DATA (Remove extreme outliers for better zoom)
            threshold = driver_laps['LapTime'].quantile(0.97)
            clean_laps = driver_laps[driver_laps['LapTime'] < threshold]
            
            # 3. IDENTIFY FASTEST LAP (Per Driver)
            fastest_lap_idx = clean_laps['LapTime'].idxmin()
            
            y_data = clean_laps['LapTime'].dt.total_seconds()
            
            # Custom Hover Text
            hover_text = [
                f"Driver: {driver}<br>"
                f"Lap: {row['LapNumber']}<br>"
                f"Time: {format_lap_time(row['LapTime'])}<br>"
                f"Compound: {row['Compound']}<br>"
                f"Tyre Life: {row['TyreLife']}"
                for index, row in clean_laps.iterrows()
            ]

            # 4. PLOT MAIN LINE
            fig.add_trace(go.Scatter(
                x=clean_laps['LapNumber'],
                y=y_data,
                mode='lines+markers',
                name=driver,
                text=hover_text,
                hoverinfo='text',
                line=dict(color=color, width=2),
                marker=dict(size=6, color=color)
            ))
            
            # 5. HIGHLIGHT FASTEST LAP (Star Marker)
            if not pd.isna(fastest_lap_idx):
                fastest_row = clean_laps.loc[fastest_lap_idx]
                fig.add_trace(go.Scatter(
                    x=[fastest_row['LapNumber']],
                    y=[fastest_row['LapTime'].total_seconds()],
                    mode='markers',
                    name=f"{driver} Best",
                    marker=dict(
                        symbol='star', 
                        size=15, 
                        color='white', 
                        line=dict(width=2, color=color)
                    ),
                    showlegend=False,
                    hoverinfo='skip'
                ))
                
        except Exception as e:
            print(f"Error plotting driver {driver}: {e}")
            continue

    fig.update_layout(
        title="Lap Time History (Official Team Colors)",
        xaxis_title="Lap Number",
        yaxis_title="Lap Time (s)",
        template="plotly_dark",
        hovermode="x unified",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_lap_info_table(session, drivers):
    """
    Creates data for the Dash DataTable.
    """
    data = []
    
    # Calculate overall fastest lap of the session (Purple)
    try:
        all_selected = session.laps.pick_drivers(drivers)
        overall_fastest_time = all_selected['LapTime'].min()
    except:
        overall_fastest_time = None

    for driver in drivers:
        laps = session.laps.pick_driver(driver)
        if laps.empty: continue
            
        # Identify personal best (Green)
        personal_best_time = laps['LapTime'].min()
        
        for idx, row in laps.iterrows():
            # Determine status
            status = ""
            if row['LapTime'] == overall_fastest_time:
                status = "PURPLE"
            elif row['LapTime'] == personal_best_time:
                status = "GREEN"

            unique_id = f"{session.event.year}-{session.event.EventName}-{session.name}-{driver}-{int(row['LapNumber'])}"
            
            data.append({
                'id': unique_id,
                'Driver': driver,
                'Lap': int(row['LapNumber']),
                'Time': format_lap_time(row['LapTime']),
                'Compound': row['Compound'],
                'TyreLife': row['TyreLife'],
                'Status': status,  # <--- FIXED: Renamed from 'IsFastest' to 'Status'
                'seconds': row['LapTime'].total_seconds() if not pd.isnull(row['LapTime']) else 9999
            })
            
    # Sort by Driver then Lap
    df = pd.DataFrame(data)
    if not df.empty:
        df = df.sort_values(by=['Driver', 'Lap'])
        return df.to_dict('records')
    return []