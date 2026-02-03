"""
Visualization Module for MV Del Monte Loadicator
Creates GZ curve plots and exports to various formats
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from datetime import datetime
from io import BytesIO


class Visualizer:
    """Handles visualization of GZ curves and stability data"""
    
    def __init__(self):
        """Initialize visualizer with default settings"""
        self.figure_size = (12, 8)
        self.dpi = 100
        
    def plot_gz_curve(self, results, show_plot=True, save_path=None):
        """
        Plot GZ curve with stability information
        
        Args:
            results: Results dictionary from StabilityCalculator
            show_plot: Whether to display the plot
            save_path: Path to save the plot (optional)
            
        Returns:
            matplotlib figure object
        """
        gz_curve = results['gz_curve']
        heel_angles = gz_curve['heel_angles']
        gz_values = gz_curve['gz_values']
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figure_size, dpi=self.dpi)
        
        # Plot GZ curve
        ax.plot(heel_angles, gz_values, 'b-', linewidth=2.5, label='GZ Curve')
        ax.plot(heel_angles, gz_values, 'bo', markersize=5)
        
        # Add zero line
        ax.axhline(y=0, color='k', linestyle='-', linewidth=0.8, alpha=0.5)
        
        # Mark maximum GZ
        max_gz = results['stability']['max_gz']
        angle_at_max = results['stability']['angle_at_max_gz']
        ax.plot(angle_at_max, max_gz, 'ro', markersize=10, label=f'Max GZ: {max_gz:.3f}m at {angle_at_max:.1f}°')
        
        # Mark vanishing angle if exists
        if results['stability']['vanishing_angle']:
            vanishing = results['stability']['vanishing_angle']
            ax.axvline(x=vanishing, color='r', linestyle='--', linewidth=1.5, 
                      label=f'Vanishing Angle: {vanishing:.1f}°', alpha=0.7)
        
        # Shade areas for IMO criteria
        # Area 0-30°
        mask_30 = np.array(heel_angles) <= 30
        angles_30 = np.array(heel_angles)[mask_30]
        gz_30 = np.array(gz_values)[mask_30]
        ax.fill_between(angles_30, 0, gz_30, alpha=0.2, color='green', 
                        label=f'Area 0-30°: {results["areas"]["area_0_30"]:.4f} m·rad')
        
        # Area 30-40°
        mask_30_40 = (np.array(heel_angles) >= 30) & (np.array(heel_angles) <= 40)
        angles_30_40 = np.array(heel_angles)[mask_30_40]
        gz_30_40 = np.array(gz_values)[mask_30_40]
        ax.fill_between(angles_30_40, 0, gz_30_40, alpha=0.2, color='yellow',
                        label=f'Area 30-40°: {results["areas"]["area_30_40"]:.4f} m·rad')
        
        # Grid
        ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)
        ax.minorticks_on()
        ax.grid(True, which='minor', linestyle=':', linewidth=0.3, alpha=0.5)
        
        # Labels and title
        ax.set_xlabel('Heel Angle (degrees)', fontsize=12, fontweight='bold')
        ax.set_ylabel('GZ - Righting Lever (meters)', fontsize=12, fontweight='bold')
        
        title = f'GZ CURVE - MV DEL MONTE\n'
        title += f'Draft: {results["input"]["draft"]:.2f}m | '
        title += f'KG: {results["input"]["kg"]:.2f}m | '
        title += f'Displacement: {results["stability"]["displacement"]:,.0f}t | '
        title += f'GM: {results["stability"]["gm"]:.3f}m'
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        # Legend
        ax.legend(loc='best', fontsize=9, framealpha=0.9)
        
        # Set axis limits
        ax.set_xlim(0, max(heel_angles))
        
        # Adjust y-axis to show negative values if any
        y_min = min(0, min(gz_values) * 1.1)
        y_max = max(gz_values) * 1.1
        ax.set_ylim(y_min, y_max)
        
        # Add compliance status text box
        compliance_status = results['compliance']['overall']['status']
        compliance_color = 'green' if results['compliance']['overall']['pass'] else 'red'
        
        textstr = f'IMO Compliance: {compliance_status}'
        props = dict(boxstyle='round', facecolor=compliance_color, alpha=0.3)
        ax.text(0.02, 0.98, textstr, transform=ax.transAxes, fontsize=11,
                verticalalignment='top', bbox=props, fontweight='bold')
        
        # Add calculation timestamp
        timestamp = results['input']['calculation_time']
        ax.text(0.98, 0.02, f'Calculated: {timestamp}', transform=ax.transAxes,
                fontsize=8, verticalalignment='bottom', horizontalalignment='right',
                style='italic', alpha=0.7)
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Plot saved to: {save_path}")
        
        # Show if requested
        if show_plot:
            plt.show()
        
        return fig
    
    def plot_compliance_summary(self, results, show_plot=True, save_path=None):
        """
        Create a visual summary of IMO compliance criteria
        
        Args:
            results: Results dictionary from StabilityCalculator
            show_plot: Whether to display the plot
            save_path: Path to save the plot (optional)
            
        Returns:
            matplotlib figure object
        """
        compliance = results['compliance']
        
        # Prepare data
        criteria = []
        values = []
        limits = []
        statuses = []
        
        for key, criterion in compliance.items():
            if key == 'overall':
                continue
            
            criteria.append(criterion['requirement'].split('≥')[0].strip())
            values.append(criterion['value'])
            limits.append(criterion['limit'])
            statuses.append(criterion['pass'])
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)
        
        # Bar positions
        y_pos = np.arange(len(criteria))
        bar_height = 0.35
        
        # Plot bars
        colors = ['green' if status else 'red' for status in statuses]
        bars1 = ax.barh(y_pos - bar_height/2, values, bar_height, label='Actual Value', color=colors, alpha=0.7)
        bars2 = ax.barh(y_pos + bar_height/2, limits, bar_height, label='Required Minimum', 
                       color='blue', alpha=0.5, edgecolor='black', linewidth=1)
        
        # Labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(criteria, fontsize=9)
        ax.set_xlabel('Value', fontsize=11, fontweight='bold')
        ax.set_title('IMO Intact Stability Code - Compliance Summary\nMV DEL MONTE', 
                    fontsize=13, fontweight='bold', pad=15)
        
        # Legend
        ax.legend(loc='best', fontsize=9)
        
        # Grid
        ax.grid(True, axis='x', linestyle='--', linewidth=0.5, alpha=0.7)
        
        # Add value labels on bars
        for i, (bar, value, status) in enumerate(zip(bars1, values, statuses)):
            width = bar.get_width()
            label_x = width + max(values) * 0.02
            label = f'{value:.4f}'
            color = 'green' if status else 'red'
            ax.text(label_x, bar.get_y() + bar.get_height()/2, label,
                   ha='left', va='center', fontsize=8, fontweight='bold', color=color)
        
        # Overall status
        overall_status = compliance['overall']['status']
        status_color = 'green' if compliance['overall']['pass'] else 'red'
        
        textstr = f'Overall: {overall_status}'
        props = dict(boxstyle='round', facecolor=status_color, alpha=0.3)
        ax.text(0.98, 0.98, textstr, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', horizontalalignment='right', 
                bbox=props, fontweight='bold')
        
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Compliance summary saved to: {save_path}")
        
        # Show if requested
        if show_plot:
            plt.show()
        
        return fig
    
    def export_to_pdf(self, results, pdf_path):
        """
        Export complete stability report to PDF
        
        Args:
            results: Results dictionary from StabilityCalculator
            pdf_path: Path to save PDF file
        """
        with PdfPages(pdf_path) as pdf:
            # Page 1: GZ Curve
            fig1 = self.plot_gz_curve(results, show_plot=False)
            pdf.savefig(fig1, bbox_inches='tight')
            plt.close(fig1)
            
            # Page 2: Compliance Summary
            fig2 = self.plot_compliance_summary(results, show_plot=False)
            pdf.savefig(fig2, bbox_inches='tight')
            plt.close(fig2)
            
            # Set PDF metadata
            d = pdf.infodict()
            d['Title'] = 'MV Del Monte - Stability Calculation Report'
            d['Author'] = 'Loadicator v1.0'
            d['Subject'] = 'GZ Curve and Stability Analysis'
            d['Keywords'] = 'Stability, GZ Curve, IMO, Marine'
            d['CreationDate'] = datetime.now()
        
        print(f"✓ PDF report saved to: {pdf_path}")

    def export_to_pdf_bytes(self, results):
        """
        Export complete stability report to PDF in memory

        Args:
            results: Results dictionary from StabilityCalculator

        Returns:
            bytes: PDF content as bytes for download
        """
        buffer = BytesIO()
        with PdfPages(buffer) as pdf:
            # Page 1: GZ Curve
            fig1 = self.plot_gz_curve(results, show_plot=False)
            pdf.savefig(fig1, bbox_inches='tight')
            plt.close(fig1)

            # Page 2: Compliance Summary
            fig2 = self.plot_compliance_summary(results, show_plot=False)
            pdf.savefig(fig2, bbox_inches='tight')
            plt.close(fig2)

            # Set PDF metadata
            d = pdf.infodict()
            d['Title'] = 'MV Del Monte - Stability Calculation Report'
            d['Author'] = 'Loadicator v1.0'
            d['Subject'] = 'GZ Curve and Stability Analysis'
            d['Keywords'] = 'Stability, GZ Curve, IMO, Marine'
            d['CreationDate'] = datetime.now()

        buffer.seek(0)
        return buffer.getvalue()


if __name__ == "__main__":
    # Test the visualizer
    from data_loader import DataLoader
    from interpolation import Interpolator
    from calculator import StabilityCalculator
    
    print("=== Testing Visualization Module ===\n")
    
    # Load data
    loader = DataLoader()
    loader.load_hydrostatic_data()
    loader.load_kn_curves()
    
    # Create interpolator and calculator
    interp = Interpolator(loader)
    calc = StabilityCalculator(interp)
    
    # Calculate stability
    test_draft = 10.0
    test_kg = 8.5
    results = calc.calculate_stability(test_draft, test_kg)
    
    # Create visualizer
    viz = Visualizer()
    
    # Plot GZ curve
    print("Generating GZ curve plot...")
    viz.plot_gz_curve(results, show_plot=False, save_path='gz_curve_test.png')
    
    # Plot compliance summary
    print("Generating compliance summary...")
    viz.plot_compliance_summary(results, show_plot=False, save_path='compliance_test.png')
    
    # Export to PDF
    print("Exporting to PDF...")
    viz.export_to_pdf(results, 'stability_report_test.pdf')
    
    print("\n✓ All visualizations generated successfully!")
