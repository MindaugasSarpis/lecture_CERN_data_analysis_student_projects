import plotly.graph_objs as go
from plotly.subplots import make_subplots
import pandas as pd
from utils.data_helper import calculate_delta

def create_telemetry_plot(laps_data_list):
    """
    laps_data_list: List of dicts containing:
      { 'driver': str, 'lap_object': fastf1.Lap, 'color': str, 'session_name': str }
    """
    
    if not laps_data_list:
        return go.Figure()

    # Define Subplots
    fig = make_subplots(
        rows=7, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[2, 1, 1, 1, 1, 1, 0.5], # Speed is bigger
        subplot_titles=("Speed (km/h)", "Delta (s)", "Throttle (%)", "Brake", "RPM", "Gear", "DRS")
    )
    
    # Use the LAST selected lap as the reference for Delta
    reference_lap_data = laps_data_list[-1] 
    ref_lap_obj = reference_lap_data['lap_object']
    
    for item in laps_data_list:
        driver = item['driver']
        lap = item['lap_object']
        color = item['color']
        label = f"{driver} (Lap {int(lap['LapNumber'])}) - {item['session_name']}"
        
        try:
            # Get Telemetry
            tel = lap.get_car_data().add_distance()
            
            # 1. Speed
            fig.add_trace(go.Scatter(
                x=tel['Distance'], y=tel['Speed'],
                mode='lines', name=label, line=dict(color=color),
                legendgroup=label
            ), row=1, col=1)
            
            # 2. Delta (Only if not the reference, or plot flat line)
            if item == reference_lap_data:
                 fig.add_trace(go.Scatter(
                    x=tel['Distance'], y=[0]*len(tel),
                    mode='lines', showlegend=False, line=dict(color=color, dash='dash')
                ), row=2, col=1)
            else:
                dist_grid, delta_vals = calculate_delta(ref_lap_obj, lap)
                if dist_grid is not None:
                     fig.add_trace(go.Scatter(
                        x=dist_grid, y=delta_vals,
                        mode='lines', showlegend=False, line=dict(color=color)
                    ), row=2, col=1)
            
            # 3. Throttle
            fig.add_trace(go.Scatter(
                x=tel['Distance'], y=tel['Throttle'],
                mode='lines', name=label, showlegend=False, line=dict(color=color),
                legendgroup=label
            ), row=3, col=1)

            # 4. Brake (Boolean or Pressure if available)
            # FastF1 'Brake' is usually boolean.
            fig.add_trace(go.Scatter(
                x=tel['Distance'], y=tel['Brake'].astype(int),
                mode='lines', name=label, showlegend=False, fill='tozeroy', line=dict(color=color),
                legendgroup=label
            ), row=4, col=1)

            # 5. RPM
            fig.add_trace(go.Scatter(
                x=tel['Distance'], y=tel['RPM'],
                mode='lines', name=label, showlegend=False, line=dict(color=color),
                legendgroup=label
            ), row=5, col=1)
            
            # 6. Gear
            fig.add_trace(go.Scatter(
                x=tel['Distance'], y=tel['nGear'],
                mode='lines', name=label, showlegend=False, line=dict(color=color),
                legendgroup=label
            ), row=6, col=1)
            
            # 7. DRS
            if 'DRS' in tel.columns:
                 fig.add_trace(go.Scatter(
                    x=tel['Distance'], y=tel['DRS'],
                    mode='lines', name=label, showlegend=False, line=dict(color=color),
                    legendgroup=label
                ), row=7, col=1)

        except Exception as e:
            print(f"Failed to plot telemetry for {label}: {e}")

    # Layout updates
    fig.update_layout(
        template="plotly_dark",
        height=1200, # Tall plot
        hovermode="x unified",
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    # Update y-axes labels
    fig.update_yaxes(title_text="km/h", row=1, col=1)
    fig.update_yaxes(title_text="Sec", row=2, col=1)
    fig.update_yaxes(title_text="%", row=3, col=1)
    fig.update_yaxes(title_text="On/Off", row=4, col=1)
    fig.update_yaxes(title_text="RPM", row=5, col=1)
    fig.update_yaxes(title_text="Gear", row=6, col=1)
    fig.update_yaxes(title_text="Status", row=7, col=1)
    fig.update_xaxes(title_text="Distance (m)", row=7, col=1)

    return fig