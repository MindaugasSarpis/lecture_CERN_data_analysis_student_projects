import pandas as pd
import sys
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import numpy as np

def plot_daily_histogram(data, num_bins=30, show_stats=True, save_plot=True, show_plot=True):
    """
    Create a histogram showing number of NEOs for each day
    """
    try:
        if 'date' not in data.columns:
            print("Error: Data must contain a 'date' column")
            return
        
        # Convert string dates to datetime
        data['date_dt'] = pd.to_datetime(data['date'])
        min_date = data['date_dt'].min()
        max_date = data['date_dt'].max()
        
        # Determine binning strategy
        if num_bins == 'all':
            # ONE BAR PER DAY (no binning)
            daily_counts = data['date'].value_counts().sort_index()
            dates = [datetime.strptime(d, '%Y-%m-%d') for d in daily_counts.index]
            bin_centers = dates
            bin_type = "daily"
            use_bins = False
            
        elif isinstance(num_bins, int) and num_bins > 0:
            # SPECIFIED NUMBER OF BINS
            unique_days = len(data['date'].unique())
            
            if num_bins >= unique_days:
                # If bins >= unique days, use daily bars
                daily_counts = data['date'].value_counts().sort_index()
                dates = [datetime.strptime(d, '%Y-%m-%d') for d in daily_counts.index]
                bin_centers = dates
                bin_type = f"daily ({len(dates)} days)"
                use_bins = False
            else:
                # Create specified number of bins
                bin_edges = pd.date_range(start=min_date, end=max_date, periods=num_bins+1)
                
                # Calculate bin centers
                bin_centers = []
                for i in range(len(bin_edges)-1):
                    bin_start = bin_edges[i]
                    bin_end = bin_edges[i+1]
                    bin_center = bin_start + (bin_end - bin_start) / 2
                    bin_centers.append(bin_center)
                
                # Assign each NEO to a bin
                data['date_bin'] = pd.cut(data['date_dt'], bins=bin_edges, labels=bin_centers, include_lowest=True)
                
                # Count NEOs in each bin
                daily_counts = data['date_bin'].value_counts().sort_index()
                
                # Ensure we have all bins (even empty ones)
                all_bins = pd.Series(index=bin_centers, data=0)
                daily_counts = all_bins.add(daily_counts, fill_value=0)
                
                bin_type = f"{num_bins} bins"
                use_bins = True
        else:
            print(f"Error: num_bins must be 'all' or a positive integer, not '{num_bins}'")
            return
        
        # Calculate statistics
        max_count = daily_counts.max()
        min_count = daily_counts.min()
        avg_count = daily_counts.mean()
        total_objects = len(data)
        total_bars = len(daily_counts)
        median_count = daily_counts.median()
        std_count = daily_counts.std()
        
        if not use_bins:
            max_date_str = bin_centers[daily_counts.argmax()].strftime('%Y-%m-%d')
            min_date_str = bin_centers[daily_counts.argmin()].strftime('%Y-%m-%d')
        
        # Create the plot layout
        if show_stats:
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), 
                                          gridspec_kw={'height_ratios': [3, 1]})
        else:
            fig, ax1 = plt.subplots(1, 1, figsize=(14, 6))
            ax2 = None
        
        # Calculate bar width
        if len(bin_centers) > 1:
            if use_bins:
                bin_width_days = (max_date - min_date).days / num_bins
                bar_width = bin_width_days * 0.7
            else:
                bar_width = 0.8
        else:
            bar_width = 0.8
            
        # Plot bars
        bars = ax1.bar(bin_centers, daily_counts.values, 
                      width=bar_width,
                      color='steelblue',
                      edgecolor='navy',
                      linewidth=1,
                      alpha=0.8,
                      align='center')
        
        # Color bars based on count value
        for i, bar in enumerate(bars):
            intensity = daily_counts.values[i] / max_count if max_count > 0 else 0.5
            bar.set_color(plt.cm.Blues(0.3 + 0.7 * intensity))
            bar.set_edgecolor('darkblue')
        
        # Add value labels on top of bars (only if reasonable number)
        if len(bin_centers) <= 30:
            for i, (center, count) in enumerate(zip(bin_centers, daily_counts.values)):
                ax1.text(center, count + (max_count * 0.02), 
                        str(int(count)), 
                        ha='center', 
                        va='bottom',
                        fontsize=9,
                        fontweight='bold')
        
        # Add a horizontal line for the average
        ax1.axhline(y=avg_count, color='red', linestyle='--', linewidth=2, 
                   alpha=0.7, label=f'Average: {avg_count:.1f}')
        
        # Format top plot
        ax1.set_title(f'Daily Near Earth Objects - {bin_type.title()}', 
                     fontsize=16, fontweight='bold', pad=20)
        ax1.set_xlabel('Date', fontsize=12)
        ax1.set_ylabel('Number of NEOs', fontsize=12)
        
        # SMART DATE LABELING :P
        # Set date formatter
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        
        if use_bins:
            # For binned data, decide on tick frequency based on number of bins
            if num_bins <= 24:
                # Few bins: show one label per bin
                ax1.set_xticks(bin_centers)
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d\n%Y'))
                ax1.tick_params(axis='x', rotation=45)
            else:
                # Many bins: show only one label per month at start of month
                months = pd.date_range(start=min_date.replace(day=1), 
                          end=max_date.replace(day=1), 
                          freq='MS')
                month_ticks = [m for m in months if min_date <= m <= max_date]
    
                if len(month_ticks) > 1:
                    ax1.set_xticks(month_ticks)
                    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
                else:
                    # Only one month
                    quarters = pd.date_range(start=min_date, 
                                end=max_date, 
                                freq='QS')
                    quarter_ticks = [q for q in quarters if min_date <= q <= max_date]
        
                    if len(quarter_ticks) > 1:
                        ax1.set_xticks(quarter_ticks)
                        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
                    else:
                        step = max(1, len(bin_centers) // 8)  # Show ~8 labels
                        ax1.set_xticks(bin_centers[::step])
                        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    
                ax1.tick_params(axis='x', rotation=45)
        else:
            # For daily data (num_bins='all')
            if len(bin_centers) <= 90:  # Up to 3 months
                tick_indices = range(0, len(bin_centers), max(1, len(bin_centers)//12))
                tick_positions = [bin_centers[i] for i in tick_indices if i < len(bin_centers)]
                ax1.set_xticks(tick_positions)
                ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
            else:
                # Show monthly labels
                months = pd.date_range(start=min_date.replace(day=1), 
                                      end=max_date.replace(day=1), 
                                      freq='MS')
                month_ticks = [m for m in months if min_date <= m <= max_date]
                if len(month_ticks) > 1:
                    ax1.set_xticks(month_ticks)
                    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
            
            ax1.tick_params(axis='x', rotation=45)
        
        # Add grid and set limits
        ax1.grid(True, alpha=0.3, linestyle='--', axis='y')
        ax1.legend(loc='upper left')
        ax1.set_ylim(bottom=0, top=max_count * 1.15)
        
        # Set x-axis limits
        if use_bins and len(bin_centers) > 1:
            first_center = bin_centers[0]
            last_center = bin_centers[-1]
            bin_spacing = (last_center - first_center) / (len(bin_centers) - 1)
            ax1.set_xlim(left=first_center - bin_spacing/2, 
                        right=last_center + bin_spacing/2)
        
        # Summary statistics (if enabled)
        if show_stats and ax2:
            date_range_str = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            
            if use_bins:
                bin_size_days = (max_date - min_date).days / num_bins
                stats_text = f"""STATISTICS ({num_bins} bins, ~{bin_size_days:.0f} days/bin):
                • Total NEOs: {total_objects:,}
                • Date range: {date_range_str}
                • Bars shown: {total_bars}
                • Average per bin: {avg_count:.1f} ± {std_count:.1f}
                • Maximum bin: {max_count:.0f} objects
                • Minimum bin: {min_count:.0f} objects
                """
            else:
                stats_text = f"""STATISTICS (daily):
                • Total NEOs: {total_objects:,}
                • Date range: {date_range_str}
                • Days shown: {total_bars}
                • Average per day: {avg_count:.1f} ± {std_count:.1f}
                • Maximum: {max_count:.0f} objects on {max_date_str}
                • Minimum: {min_count:.0f} objects on {min_date_str}
                """
            
            ax2.axis('off')
            ax2.text(0.02, 0.5, stats_text, 
                    fontsize=10, 
                    fontfamily='monospace',
                    verticalalignment='center',
                    bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))
        
        plt.tight_layout()
        
        # Save plot if requested
        if save_plot:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            if num_bins == 'all':
                bin_info = "_daily"
            else:
                bin_info = f"_{num_bins}bins"
            stats_info = "_nostats" if not show_stats else ""
            plot_filename = f"neo_histogram{bin_info}{stats_info}_{timestamp}.png"
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            print(f"Histogram saved as: {plot_filename}")
        
        # Show plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()
            
        # Clean up temporary columns
        if 'date_dt' in data.columns:
            data.drop('date_dt', axis=1, inplace=True, errors='ignore')
        if 'date_bin' in data.columns:
            data.drop('date_bin', axis=1, inplace=True, errors='ignore')

        return fig
            
    except Exception as e:
        print(f"Error creating histogram: {e}")
        import traceback
        traceback.print_exc()

def plot_diameter_comparison(data, number, save_plot=True, show_plot=True):
    """
    Create a scatterplot showing diameter min, max, and their difference over time
    """
    try:
        # Check if required columns exist
        required_cols = ['estimated_diameter_min_km', 'estimated_diameter_max_km', 'date', 'name']
        missing_cols = [col for col in required_cols if col not in data.columns]
        
        if missing_cols:
            print(f"Error: Missing required columns: {missing_cols}")
            return
        
        # Ensure date is datetime and sort by date for proper ordering
        data = data.copy()
        data['date_dt'] = pd.to_datetime(data['date'])
        data = data.sort_values('date_dt')
        
        # Create a spaced x-axis: group by date, then assign positions within each date
        data['group_date'] = data['date_dt'].dt.date
        
        # Create spaced positions: date index + fraction based on position within same date
        date_groups = data.groupby('group_date')
        spaced_positions = []
        date_labels_positions = []  # Store date objects for later label calculation
        date_positions_dict = {}    # Map date to its integer position
        date_group_sizes = {}       # Track how many NEOs per date
        
        for i, (date, group) in enumerate(date_groups):
            group_size = len(group)
            date_labels_positions.append(date)
            date_positions_dict[date] = i
            date_group_sizes[date] = group_size
            
            if group_size == 1:
                spaced_positions.append(i)
            else:
                # Multiple NEOs on same date - dynamic spacing based on group size
                # More NEOs = wider spread
                if group_size <= 5:
                    spread_factor = 0.15  # Small groups
                elif group_size <= 15:
                    spread_factor = 0.25  # Medium groups
                elif group_size <= 30:
                    spread_factor = 0.35  # Large groups
                else:
                    spread_factor = 0.45  # Very large groups
                
                # Calculate spread width
                total_spread = spread_factor * (group_size - 1)
                
                for j in range(group_size):
                    # Position from -total_spread/2 to +total_spread/2
                    position = -total_spread/2 + (j * spread_factor)
                    spaced_positions.append(i + position)
        
        data['spaced_position'] = spaced_positions
        
        # Calculate the difference
        data['diameter_diff_km'] = data['estimated_diameter_max_km'] - data['estimated_diameter_min_km']
        
        # Create the plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 10), 
                                       gridspec_kw={'height_ratios': [2, 1]})
        
        # TOP PANEL: Diameter min and max over time (with spacing)
        scatter_min = ax1.scatter(data['spaced_position'], data['estimated_diameter_min_km'],
                                 color='blue', 
                                 s=30,  # Point size
                                 alpha=0.7,
                                 edgecolors='darkblue',
                                 linewidths=0.5,
                                 label='Min Diameter (km)')
        
        scatter_max = ax1.scatter(data['spaced_position'], data['estimated_diameter_max_km'],
                                 color='red', 
                                 s=30,
                                 alpha=0.7,
                                 edgecolors='darkred',
                                 linewidths=0.5,
                                 label='Max Diameter (km)')
        
        # Connect min and max for each NEO with vertical lines
        for idx, row in data.iterrows():
            ax1.plot([row['spaced_position'], row['spaced_position']],
                    [row['estimated_diameter_min_km'], row['estimated_diameter_max_km']],
                    color='black',
                    alpha=0.2,
                    linewidth=0.5)
        
        # Format top plot
        unique_dates_count = len(date_labels_positions)
        date_range_str = f"{date_labels_positions[0]} to {date_labels_positions[-1]}"
        
        # Calculate total NEOs and max NEOs per day
        total_neos = len(data)
        max_neos_per_day = max(date_group_sizes.values()) if date_group_sizes else 1
        
        ax1.set_title(f'NEO Estimated Diameters ({total_neos} objects, {unique_dates_count} days)\n'
                     f'Date range: {date_range_str}', 
                     fontsize=16, fontweight='bold', pad=20)
        ax1.set_ylabel('Diameter (km)', fontsize=12)
        

        # Use linear scale but adjust limits based on data distribution
        max_diameter = data['estimated_diameter_max_km'].max()
        min_diameter = data['estimated_diameter_min_km'].min()

        # Check if we should use log scale (ONLY if extreme range)
        if max_diameter > 0 and min_diameter > 0:
            range_ratio = max_diameter / min_diameter
    
            if range_ratio > 1000:  # Only use log for extreme ranges (1000:1 ratio)
                ax1.set_yscale('log')
                ax1.set_ylabel('Diameter (km) - Log Scale', fontsize=12)
                print(f"  Using log scale (range ratio: {range_ratio:.0f}:1)")
            else:
                # Use linear scale with adjusted limits
                # Set y-axis limits to show the data clearly
                upper_limit = max_diameter * 1.1  # 10% padding
                lower_limit = max(0, min_diameter * 0.9)  # 10% padding, never below 0
        
                # If there are very small values, consider starting from 0
                if min_diameter < (max_diameter * 0.01):  # If smallest is <1% of largest
                    lower_limit = 0  # Start from 0 for better visualization
            
                ax1.set_ylim(bottom=lower_limit, top=upper_limit)
        
                print(f"  Range ratio: {range_ratio:.0f}:1")
        
        ax1.grid(True, alpha=0.3, linestyle='--')
        ax1.legend(loc='upper left')
        
        # SMART X-AXIS LABELING!!!!!
        x_ticks = []
        x_labels = []
        x_label_description = ""
        
        if unique_dates_count <= 30:
            # SMALL DATASET: Show exact dates (every date or every few dates)
            x_label_description = "exact dates"
            
            if unique_dates_count <= 15:
                # Show all dates
                x_ticks = list(range(unique_dates_count))
                x_labels = [d.strftime('%m-%d') for d in date_labels_positions]
            else:
                # Show every other date for 16-30 dates
                step = 2 if unique_dates_count > 20 else 1
                x_ticks = list(range(0, unique_dates_count, step))
                x_labels = [date_labels_positions[i].strftime('%m-%d') for i in x_ticks]
                
                # Add year to first and last label if crossing year boundary
                if date_labels_positions[0].year != date_labels_positions[-1].year:
                    x_labels[0] = date_labels_positions[x_ticks[0]].strftime('%Y-%m-%d')
                    x_labels[-1] = date_labels_positions[x_ticks[-1]].strftime('%Y-%m-%d')
            
        else:
            # LARGE DATASET: Show monthly labels (max 12)
            x_label_description = "monthly labels"
            
            # Create monthly ticks (first day of each month)
            from datetime import datetime as dt
            start_date = date_labels_positions[0]
            end_date = date_labels_positions[-1]
            
            monthly_ticks = []
            monthly_labels = []
            
            current_month = dt(start_date.year, start_date.month, 1)
            end_month = dt(end_date.year, end_date.month, 1)
            
            while current_month <= end_month:
                # Find all dates in this month
                month_dates = [d for d in date_labels_positions 
                              if d.year == current_month.year and d.month == current_month.month]
                
                if month_dates:
                    # Use the middle date of this month for positioning
                    mid_idx = len(month_dates) // 2
                    target_date = month_dates[mid_idx]
                    
                    # Find the position index of this date
                    if target_date in date_positions_dict:
                        pos_idx = date_positions_dict[target_date]
                        monthly_ticks.append(pos_idx)
                        month_label = current_month.strftime('%b\n%Y') if current_month.month == 1 else current_month.strftime('%b')
                        monthly_labels.append(month_label)
                
                # Move to next month
                if current_month.month == 12:
                    current_month = dt(current_month.year + 1, 1, 1)
                else:
                    current_month = dt(current_month.year, current_month.month + 1, 1)
            
            # Limit to max 12 labels
            if len(monthly_ticks) > 12:
                step = max(1, len(monthly_ticks) // 12)
                monthly_ticks = monthly_ticks[::step]
                monthly_labels = monthly_labels[::step]
            
            x_ticks = monthly_ticks
            x_labels = monthly_labels
        
        # Apply the x-axis configuration
        ax1.set_xticks(x_ticks)
        ax1.set_xticklabels(x_labels)
        ax1.tick_params(axis='x', rotation=45)
        
        # Adjust x-axis label based on spacing
        if max_neos_per_day > 10:
            x_label_text = f'Date ({x_label_description})'
        else:
            x_label_text = f'Date ({x_label_description})'
        
        ax1.set_xlabel(x_label_text, fontsize=11)
        
        # Set x-axis limits with extra padding for spread dates
        max_spread = 0
        for date, group_size in date_group_sizes.items():
            if group_size > 1:
                if group_size <= 5:
                    spread = 0.15 * (group_size - 1) / 2
                elif group_size <= 15:
                    spread = 0.25 * (group_size - 1) / 2
                elif group_size <= 30:
                    spread = 0.35 * (group_size - 1) / 2
                else:
                    spread = 0.45 * (group_size - 1) / 2
                max_spread = max(max_spread, spread)
        
        ax1.set_xlim(left=-0.5 - max_spread, right=unique_dates_count-0.5 + max_spread)
        
        # Add vertical grid lines at tick positions
        for tick in x_ticks:
            ax1.axvline(x=tick, color='gray', alpha=0.2, linestyle='-', linewidth=0.5)
        
        # Difference over time (with same spacing)
        scatter_diff = ax2.scatter(data['spaced_position'], data['diameter_diff_km'],
                                  c=data['diameter_diff_km'],
                                  cmap='viridis',
                                  s=30,
                                  alpha=0.8,
                                  edgecolors='black',
                                  linewidths=0.3)
        
        # Add colorbar for difference values
        cbar = plt.colorbar(scatter_diff, ax=ax2)
        cbar.set_label('Difference (km)', fontsize=10)
        
        # Add horizontal line for average difference
        avg_diff = data['diameter_diff_km'].mean()
        ax2.axhline(y=avg_diff, color='red', linestyle='--', linewidth=1.5,
                   alpha=0.7, label=f'Average: {avg_diff:.3f} km')
        
        # Format bottom plot
        ax2.set_title('Diameter Uncertainty (Max - Min)', fontsize=14, fontweight='bold', pad=15)
        ax2.set_xlabel(x_label_text, fontsize=11)
        ax2.set_ylabel('Difference (km)', fontsize=12)
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.legend(loc='upper left')
        
        # Use same x-axis configuration as top panel
        ax2.set_xticks(x_ticks)
        ax2.set_xticklabels(x_labels)
        ax2.tick_params(axis='x', rotation=45)
        ax2.set_xlim(left=-0.5 - max_spread, right=unique_dates_count-0.5 + max_spread)
        
        # Add vertical grid lines at tick positions
        for tick in x_ticks:
            ax2.axvline(x=tick, color='gray', alpha=0.2, linestyle='-', linewidth=0.5)
        
        # Add annotations for peaks in difference - FOR BOTH PLOTS
        if len(data) > 10:
            top_diff_indices = data['diameter_diff_km'].nlargest(number).index
    
            for idx in top_diff_indices:
                pos_val = data.loc[idx, 'spaced_position']
                diff_val = data.loc[idx, 'diameter_diff_km']
                min_val = data.loc[idx, 'estimated_diameter_min_km']
                max_val = data.loc[idx, 'estimated_diameter_max_km']
                asteroid_name = data.loc[idx, 'name']
                date_val = data.loc[idx, 'date']
        
                if diff_val > avg_diff * 2:
                    # Adjust annotation position to avoid overlap
                    annotation_x_offset = 0
                    annotation_y_offset = 20
            
                    # If near the edge, adjust position
                    if pos_val < 2:
                        annotation_x_offset = 10
                    elif pos_val > unique_dates_count - 3:
                        annotation_x_offset = -10

                    # diameter plot
                    # Calculate position for top plot annotation (above the max diameter)
                    top_annotation_y_offset = 30  # More offset for top plot
            
                    # Different colors for top plot to distinguish from bottom plot
                    ax1.annotate(f'{asteroid_name}\nΔ: {diff_val:.2f} km',
                        xy=(pos_val, max_val),  # Anchor at max diameter point
                        xytext=(annotation_x_offset, top_annotation_y_offset),
                        textcoords='offset points',
                        arrowprops=dict(arrowstyle='->', color='darkblue', alpha=0.7),
                        fontsize=8,
                        fontweight='bold',
                        ha='center',
                        bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            
                    # Add a marker on the top plot to make it more visible
                    ax1.plot(pos_val, max_val, 'g*', markersize=8, alpha=0.8, 
                    markeredgecolor='darkgreen', markeredgewidth=1, zorder=5)
            
                    # difference plot
                    ax2.annotate(f'{asteroid_name}\n{diff_val:.2f} km\n({min_val:.1f}-{max_val:.1f})',
                        xy=(pos_val, diff_val),
                        xytext=(annotation_x_offset, annotation_y_offset),
                        textcoords='offset points',
                        arrowprops=dict(arrowstyle='->', color='darkred', alpha=0.7),
                        fontsize=8,
                        fontweight='bold',
                        ha='center',
                        bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
        
        plt.tight_layout()
        
        # Save plot if requested
        if save_plot:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dataset_type = "small" if unique_dates_count <= 30 else "large"
            plot_filename = f"neo_diameter_{dataset_type}_dataset_{timestamp}.png"
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            print(f"  Diameter plot ({dataset_type} dataset) saved as: {plot_filename}")
        
        # Show plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()

        return fig
            
    except Exception as e:
        print(f"Error creating diameter time series plot: {e}")
        import traceback
        traceback.print_exc()

def plot_simple_scatter(data, metric_choice, save_plot=True, show_plot=True):
    """
    Create a simple scatter plot for selected metric over time
    metric_choice: 1=velocity, 2=miss distance, 3=orbital period
    """
    try:
        # Map metric choices to columns and labels
        metric_map = {
            1: {
                'column': 'relative_velocity_km_s',
                'label': 'Relative Velocity (km/s)',
                'title': 'Relative Velocity over Time',
                'format': '{:.1f} km/s'
            },
            2: {
                'column': 'miss_distance_km',
                'label': 'Miss Distance (km)',
                'title': 'Miss Distance over Time',
                'format': '{:.0f} km'
            },
            3: {
                'column': 'orbital_period_days',
                'label': 'Orbital Period (days)',
                'title': 'Orbital Period over Time',
                'format': '{:.1f} days'
            }
        }
        
        metric_info = metric_map[metric_choice]
        metric_column = metric_info['column']
        
        # Check if required column exists
        if metric_column not in data.columns:
            print(f"Error: Column '{metric_column}' not found in data.")
            return
        
        # Ensure date is datetime and sort by date for proper ordering
        data = data.copy()
        data['date_dt'] = pd.to_datetime(data['date'])
        data = data.sort_values('date_dt')
        
        # Filter out NaN values in the metric column
        original_count = len(data)
        data = data.dropna(subset=[metric_column])
        filtered_count = original_count - len(data)
        
        if filtered_count > 0:
            print(f"  Note: Filtered out {filtered_count} records with missing {metric_info['label']}")
        
        if len(data) == 0:
            print(f"Error: No valid data points for {metric_info['label']}")
            return
        
        # Create a spaced x-axis: group by date, then assign positions within each date
        data['group_date'] = data['date_dt'].dt.date
        
        # Create spaced positions: date index + fraction based on position within same date
        date_groups = data.groupby('group_date')
        spaced_positions = []
        date_labels_positions = []  # Store date objects for later label calculation
        date_positions_dict = {}    # Map date to its integer position
        date_group_sizes = {}       # Track how many NEOs per date
        
        for i, (date, group) in enumerate(date_groups):
            group_size = len(group)
            date_labels_positions.append(date)
            date_positions_dict[date] = i
            date_group_sizes[date] = group_size
            
            if group_size == 1:
                spaced_positions.append(i)
            else:
                # Multiple NEOs on same date - dynamic spacing based on group size
                if group_size <= 5:
                    spread_factor = 0.15  # Small groups
                elif group_size <= 15:
                    spread_factor = 0.25  # Medium groups
                elif group_size <= 30:
                    spread_factor = 0.35  # Large groups
                else:
                    spread_factor = 0.45  # Very large groups
                
                # Calculate spread width
                total_spread = spread_factor * (group_size - 1)
                
                for j in range(group_size):
                    # Position from -total_spread/2 to +total_spread/2
                    position = -total_spread/2 + (j * spread_factor)
                    spaced_positions.append(i + position)
        
        data['spaced_position'] = spaced_positions
        
        # Create the plot
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Scatter plot with color based on metric value
        scatter = ax.scatter(data['spaced_position'], data[metric_column],
                            c=data[metric_column],  # Color by metric value
                            cmap='viridis',
                            s=50,  # Point size
                            alpha=0.8,
                            edgecolors='black',
                            linewidths=0.5,
                            zorder=3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label(metric_info['label'], fontsize=11)
        
        # Format plot
        unique_dates_count = len(date_labels_positions)
        date_range_str = f"{date_labels_positions[0]} to {date_labels_positions[-1]}"
        
        # Calculate total NEOs and max NEOs per day
        total_neos = len(data)
        max_neos_per_day = max(date_group_sizes.values()) if date_group_sizes else 1
        
        ax.set_title(f'{metric_info["title"]} ({total_neos} objects, {unique_dates_count} days)\n'
                    f'Date range: {date_range_str}', 
                    fontsize=16, fontweight='bold', pad=20)
        ax.set_ylabel(metric_info['label'], fontsize=12)
        
        # SMART X-AXIS LABELING!!!!!!!!!!
        x_ticks = []
        x_labels = []
        x_label_description = ""
        
        if unique_dates_count <= 30:
            # SMALL DATASET: Show exact dates (every date or every few dates)
            x_label_description = "exact dates"
            
            if unique_dates_count <= 15:
                # Show all dates
                x_ticks = list(range(unique_dates_count))
                x_labels = [d.strftime('%m-%d') for d in date_labels_positions]
            else:
                # Show every other date for 16-30 dates
                step = 2 if unique_dates_count > 20 else 1
                x_ticks = list(range(0, unique_dates_count, step))
                x_labels = [date_labels_positions[i].strftime('%m-%d') for i in x_ticks]
                
                # Add year to first and last label if crossing year boundary
                if date_labels_positions[0].year != date_labels_positions[-1].year:
                    x_labels[0] = date_labels_positions[x_ticks[0]].strftime('%Y-%m-%d')
                    x_labels[-1] = date_labels_positions[x_ticks[-1]].strftime('%Y-%m-%d')
            
        else:
            # LARGE DATASET: Show monthly labels
            x_label_description = "monthly labels"
            
            # Create monthly ticks (first day of each month)
            from datetime import datetime as dt
            start_date = date_labels_positions[0]
            end_date = date_labels_positions[-1]
            
            monthly_ticks = []
            monthly_labels = []
            
            current_month = dt(start_date.year, start_date.month, 1)
            end_month = dt(end_date.year, end_date.month, 1)
            
            while current_month <= end_month:
                # Find all dates in this month
                month_dates = [d for d in date_labels_positions 
                              if d.year == current_month.year and d.month == current_month.month]
                
                if month_dates:
                    # Use the middle date of this month for positioning
                    mid_idx = len(month_dates) // 2
                    target_date = month_dates[mid_idx]
                    
                    # Find the position index of this date
                    if target_date in date_positions_dict:
                        pos_idx = date_positions_dict[target_date]
                        monthly_ticks.append(pos_idx)
                        month_label = current_month.strftime('%b\n%Y') if current_month.month == 1 else current_month.strftime('%b')
                        monthly_labels.append(month_label)
                
                # Move to next month
                if current_month.month == 12:
                    current_month = dt(current_month.year + 1, 1, 1)
                else:
                    current_month = dt(current_month.year, current_month.month + 1, 1)
            
            # Limit to max 12 labels
            if len(monthly_ticks) > 12:
                step = max(1, len(monthly_ticks) // 12)
                monthly_ticks = monthly_ticks[::step]
                monthly_labels = monthly_labels[::step]
            
            x_ticks = monthly_ticks
            x_labels = monthly_labels
        
        # Apply the x-axis configuration
        ax.set_xticks(x_ticks)
        ax.set_xticklabels(x_labels)
        ax.tick_params(axis='x', rotation=45)
        
        x_label_text = f'Date ({x_label_description})'
        
        ax.set_xlabel(x_label_text, fontsize=11)
        
        # Set x-axis limits with extra padding for spread dates
        max_spread = 0
        for date, group_size in date_group_sizes.items():
            if group_size > 1:
                if group_size <= 5:
                    spread = 0.15 * (group_size - 1) / 2
                elif group_size <= 15:
                    spread = 0.25 * (group_size - 1) / 2
                elif group_size <= 30:
                    spread = 0.35 * (group_size - 1) / 2
                else:
                    spread = 0.45 * (group_size - 1) / 2
                max_spread = max(max_spread, spread)
        
        ax.set_xlim(left=-0.5 - max_spread, right=unique_dates_count-0.5 + max_spread)
        
        # Add vertical grid lines at tick positions
        for tick in x_ticks:
            ax.axvline(x=tick, color='gray', alpha=0.2, linestyle='-', linewidth=0.5)
        
        # Add horizontal grid lines
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        # Find lowest and highest values
        min_idx = data[metric_column].idxmin()
        max_idx = data[metric_column].idxmax()
        
        min_value = data.loc[min_idx, metric_column]
        max_value = data.loc[max_idx, metric_column]
        min_name = data.loc[min_idx, 'name']
        max_name = data.loc[max_idx, 'name']
        min_date = data.loc[min_idx, 'date_dt'].strftime('%Y-%m-%d')
        max_date = data.loc[max_idx, 'date_dt'].strftime('%Y-%m-%d')
        min_pos = data.loc[min_idx, 'spaced_position']
        max_pos = data.loc[max_idx, 'spaced_position']
        
        # Add annotations for lowest value
        ax.annotate(f'LOWEST: {min_name}\n{metric_info["format"].format(min_value)}\n{min_date}',
                   xy=(min_pos, min_value),
                   xytext=(-100, -40),  # Offset for annotation
                   textcoords='offset points',
                   arrowprops=dict(arrowstyle='->', color='blue', alpha=0.7),
                   fontsize=9,
                   fontweight='bold',
                   ha='center',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.9),
                   zorder=5)
        
        # Add marker for lowest point
        ax.plot(min_pos, min_value, 'bo', markersize=10, 
                markeredgecolor='darkblue', markeredgewidth=2, zorder=4)
        
        # Add annotations for highest value
        ax.annotate(f'HIGHEST: {max_name}\n{metric_info["format"].format(max_value)}\n{max_date}',
                   xy=(max_pos, max_value),
                   xytext=(100, 40),  # Offset for annotation
                   textcoords='offset points',
                   arrowprops=dict(arrowstyle='->', color='red', alpha=0.7),
                   fontsize=9,
                   fontweight='bold',
                   ha='center',
                   bbox=dict(boxstyle='round', facecolor='lightcoral', alpha=0.9),
                   zorder=5)
        
        # Add marker for highest point
        ax.plot(max_pos, max_value, 'ro', markersize=10, 
                markeredgecolor='darkred', markeredgewidth=2, zorder=4)
        
        # Add summary statistics box
        stats_text = f"""STATISTICS:
        • Total NEOs: {total_neos:,}
        • Date range: {date_range_str}
        • Minimum: {metric_info['format'].format(min_value)} ({min_name})
        • Maximum: {metric_info['format'].format(max_value)} ({max_name})
        • Average: {metric_info['format'].format(data[metric_column].mean())}
        • Std Dev: {metric_info['format'].format(data[metric_column].std())}
        """
        
        # Add text box with statistics
        ax.text(0.02, 0.98, stats_text,
               transform=ax.transAxes,
               fontsize=9,
               fontfamily='monospace',
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='lightgray', alpha=0.3))
        
        plt.tight_layout()
        
        # Save plot if requested
        if save_plot:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            metric_name = metric_info['title'].replace(' ', '_').lower()
            dataset_type = "small" if unique_dates_count <= 30 else "large"
            plot_filename = f"neo_{metric_name}_{dataset_type}_{timestamp}.png"
            plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
            print(f"  Simple scatter plot ({metric_info['title']}) saved as: {plot_filename}")
        
        # Show plot if requested
        if show_plot:
            plt.show()
        else:
            plt.close()

        return fig
            
    except Exception as e:
        print(f"Error creating simple scatter plot: {e}")
        import traceback
        traceback.print_exc()

def read_from_link(link):
    """
    Read CSV data from a Google Drive link
    """
    try:
        file_id = None
        
        # Format 1: https://drive.google.com/file/d/FILE_ID/view
        if '/file/d/' in link:
            parts = link.split('/file/d/')[1].split('/')
            file_id = parts[0]
        
        # Format 2: https://drive.google.com/open?id=FILE_ID
        elif 'id=' in link:
            file_id = link.split('id=')[1].split('&')[0]
        
        # Format 3: Direct ID 
        else:
            file_id = link
        
        if not file_id:
            raise ValueError(f"Could not extract file ID from: {link}")
        
        # Create direct download URL
        download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
        
        # Download and read CSV
        print(f"Downloading from Google Drive...")
        df = pd.read_csv(download_url)
        return df
        
    except Exception as e:
        print(f"Error reading from link: {e}")
        return None

def read_from_file(filepath):
    """
    Read CSV data from a local file
    """
    try:
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"Error: File not found: {filepath}")
            return None
        
        # Read CSV file
        df = pd.read_csv(filepath)
        return df
        
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
def main():
    # Check minimum arguments
    if len(sys.argv) < 4:
        print("Usage:")
        print("  Basic: python extract_data.py <mode> <source> <plot_type>")
        print("  Full:  python extract_data.py <mode> <source> <plot_type> [parameter] [hide]")
        print("")
        print("Arguments:")
        print("  mode: 1 (Google Drive link) or 2 (local file)")
        print("  source: URL or file path")
        print("  plot_type: 'hist' (number of objects) or 'scatter' (diameter comparison) or 'simple' (other metrics)")
        print("  parameter: for 'hist': number of bins or 'all' (default: 30)")
        print("             for 'scatter': number of largest differences to show (default: 3)")
        print("             for 'simple': metric choice 1-4 (default: 1)")
        print("                 1: Relative Velocity")
        print("                 2: Miss Distance")
        print("                 3: Orbital Period")
        print("  hide: 'hide' to hide statistics for histogram")
        print("")
        print("Examples:")
        print("  python extract_data.py 1 <link> hist                     # Default histogram")
        print("  python extract_data.py 2 data.csv hist all               # Daily histogram")
        print("  python extract_data.py 2 data.csv hist 7 hide            # 7 bins, no stats")
        print("  python extract_data.py 1 <link> scatter                  # Scatter plot, top 3 differences")
        print("  python extract_data.py 2 data.csv scatter 5              # Scatter plot, top 5 differences")
        print("  python extract_data.py 2 data.csv simple 1               # Simple scatter: velocity")
        print("  python extract_data.py 2 data.csv simple 2               # Simple scatter: miss distance")
        print("  python extract_data.py 2 data.csv hist 12                # 12 bins histogram")
        sys.exit(1)
    
    # Parse required arguments
    mode = sys.argv[1]
    source = sys.argv[2]
    plot_type = sys.argv[3].lower()
    
    # Validate plot_type
    if plot_type not in ['hist', 'scatter', 'simple']:
        print(f"Error: plot_type must be 'hist', 'scatter', or 'simple', not '{plot_type}'")
        sys.exit(1)
    
    # Default parameters
    parameter = None
    hide_stats = False
    
    # Parse optional arguments
    if len(sys.argv) >= 5:
        arg4 = sys.argv[4]
        
        if plot_type == 'hist':
            # For histogram, parameter is bins
            if arg4.lower() == 'all':
                parameter = 'all'
            elif arg4.isdigit() and int(arg4) > 0:
                parameter = int(arg4)
            else:
                print(f"Error: For histogram, parameter must be 'all' or positive integer, not '{arg4}'")
                sys.exit(1)
        elif plot_type == 'scatter':
            # For scatter plot, parameter is number of differences to show
            if arg4.isdigit() and int(arg4) > 0:
                parameter = int(arg4)
            else:
                print(f"Error: For scatter plot, parameter must be positive integer, not '{arg4}'")
                sys.exit(1)
        elif plot_type == 'simple':
            # For simple scatter, parameter is metric choice 1-3
            if arg4.isdigit() and 1 <= int(arg4) <= 3:
                parameter = int(arg4)
            else:
                print(f"Error: For simple scatter, parameter must be 1-3, not '{arg4}'")
                print("  1: Relative Velocity")
                print("  2: Miss Distance")
                print("  3: Orbital Period")
                sys.exit(1)
    
    if len(sys.argv) >= 6:
        arg5 = sys.argv[5].lower()
        if arg5 == 'hide':
            hide_stats = True
        else:
            print(f"Warning: Unknown fifth argument '{arg5}', ignoring. Use 'hide' to hide statistics.")
    
    # Set defaults if parameter not provided
    if parameter is None:
        if plot_type == 'hist':
            parameter = 30  # Default bins
        elif plot_type == 'scatter':
            parameter = 3   # Default top differences to show
        elif plot_type == 'simple':
            parameter = 1   # Default to velocity
    
    # Load data
    if mode == '1':
        data = read_from_link(source)
    elif mode == '2':
        data = read_from_file(source)
    else:
        print(f"Error: First argument must be 1 or 2, not '{mode}'")
        sys.exit(1)
    
    if data is not None:
        print(f"\n  Data loaded successfully!")
        print(f"  Records: {len(data)}")
        print(f"  Plot type: {plot_type}")
        
        if plot_type == 'simple':
            metric_names = {
                1: 'Relative Velocity',
                2: 'Miss Distance',
                3: 'Orbital Period'
            }
            print(f"  Metric: {metric_names[parameter]} (option {parameter})")
        else:
            print(f"  Parameter: {parameter}")
            
        if plot_type == 'hist':
            print(f"  Show stats: {not hide_stats}")
        
        # Execute the appropriate plot function
        if plot_type == 'hist':
            plot_daily_histogram(data, 
                                num_bins=parameter, 
                                show_stats=not hide_stats,
                                save_plot=False, 
                                show_plot=True)
        elif plot_type == 'scatter':
            print(f"  Showing top {parameter} largest differences")
            plot_diameter_comparison(data, 
                                    parameter,
                                    save_plot=False, 
                                    show_plot=True)
        elif plot_type == 'simple':
            plot_simple_scatter(data,
                               metric_choice=parameter,
                               save_plot=False,
                               show_plot=True)
    else:
        print("Failed to load data.")
            

if __name__ == "__main__":
    main()