import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Import your plot functions directly
sys.path.append('.')  # Add current directory to path
from create_visuals import plot_daily_histogram, plot_diameter_comparison, plot_simple_scatter

def create_pdf_report(data, output_pdf="neo_report.pdf"):
    print(f"Creating PDF report: {output_pdf}")
    
    with PdfPages(output_pdf) as pdf:
        # 1. Histogram
        print("  Adding histogram...")
        fig1 = plot_daily_histogram(
            data, 
            num_bins=30,
            show_stats=True,
            save_plot=False,
            show_plot=False
        )
        if fig1:
            pdf.savefig(fig1, bbox_inches='tight')
            plt.close(fig1)
        
        # 2. Diameter comparison
        print("  Adding diameter comparison...")
        fig2 = plot_diameter_comparison(
            data,
            number=3,
            save_plot=False,
            show_plot=False
        )
        if fig2:
            pdf.savefig(fig2, bbox_inches='tight')
            plt.close(fig2)
        
        # 3. Scatter plots
        for metric in [1, 2, 3]:
            metric_names = {1: 'velocity', 2: 'distance', 3: 'period'}
            print(f"  Adding {metric_names.get(metric, 'scatter')} plot...")
            
            fig3 = plot_simple_scatter(
                data,
                metric_choice=metric,
                save_plot=False,
                show_plot=False
            )
            if fig3:
                pdf.savefig(fig3, bbox_inches='tight')
                plt.close(fig3)
    
    print(f"✓ PDF report saved: {output_pdf}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python make_pdf.py <data.csv> [output.pdf]")
        sys.exit(1)
    
    data_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "neo_report.pdf"
    
    # Load data
    data = pd.read_csv(data_file)
    
    # Create PDF
    create_pdf_report(data, output_file)

if __name__ == "__main__":
    main()