#!/usr/bin/env python3
"""
MV Del Monte Loadicator - Main Application
Command-line interface for stability calculations and GZ curve generation
"""

import sys
import argparse
from pathlib import Path

from data_loader import DataLoader
from interpolation import Interpolator
from calculator import StabilityCalculator
from visualizer import Visualizer


class Loadicator:
    """Main loadicator application"""
    
    def __init__(self, data_dir="."):
        """
        Initialize loadicator
        
        Args:
            data_dir: Directory containing CSV data files
        """
        self.data_dir = Path(data_dir)
        self.loader = None
        self.interpolator = None
        self.calculator = None
        self.visualizer = None
        self.initialized = False
        
    def initialize(self):
        """Load data and initialize all modules"""
        print("\n" + "=" * 80)
        print("MV DEL MONTE - LOADICATOR v1.0")
        print("Stability Calculator and GZ Curve Generator")
        print("=" * 80 + "\n")
        
        try:
            # Load data
            print("Loading vessel data...")
            self.loader = DataLoader(self.data_dir)
            self.loader.load_hydrostatic_data()
            self.loader.load_kn_curves()
            self.loader.validate_data()
            
            # Initialize modules
            self.interpolator = Interpolator(self.loader)
            self.calculator = StabilityCalculator(self.interpolator)
            self.visualizer = Visualizer()
            
            self.initialized = True
            
            print("\n✓ Loadicator initialized successfully!\n")
            
            # Display valid ranges
            draft_min, draft_max = self.loader.get_draft_range()
            print(f"Valid draft range: {draft_min:.2f}m to {draft_max:.2f}m")
            
        except Exception as e:
            print(f"\n✗ Error initializing loadicator: {e}")
            sys.exit(1)
    
    def calculate(self, draft, kg, output_format='text', save_plot=None, save_pdf=None):
        """
        Perform stability calculation
        
        Args:
            draft: Draft at perpendiculars (m)
            kg: Vertical center of gravity (m)
            output_format: Output format ('text', 'json', or 'both')
            save_plot: Path to save plot image (optional)
            save_pdf: Path to save PDF report (optional)
            
        Returns:
            Results dictionary
        """
        if not self.initialized:
            raise RuntimeError("Loadicator not initialized. Call initialize() first.")
        
        print("\n" + "=" * 80)
        print("CALCULATING STABILITY...")
        print("=" * 80)
        
        try:
            # Validate inputs
            draft_min, draft_max = self.loader.get_draft_range()
            if draft < draft_min or draft > draft_max:
                raise ValueError(f"Draft {draft:.2f}m is outside valid range [{draft_min:.2f}m, {draft_max:.2f}m]")
            
            if kg <= 0:
                raise ValueError(f"KG must be positive (got {kg:.2f}m)")
            
            # Perform calculation
            results = self.calculator.calculate_stability(draft, kg)
            
            # Display results
            if output_format in ['text', 'both']:
                report = self.calculator.generate_report(results)
                print("\n" + report)
            
            # Save plot if requested
            if save_plot:
                print(f"\nGenerating plot: {save_plot}")
                self.visualizer.plot_gz_curve(results, show_plot=False, save_path=save_plot)
            
            # Save PDF if requested
            if save_pdf:
                print(f"\nGenerating PDF report: {save_pdf}")
                self.visualizer.export_to_pdf(results, save_pdf)
            
            return results
            
        except Exception as e:
            print(f"\n✗ Error during calculation: {e}")
            raise
    
    def interactive_mode(self):
        """Run loadicator in interactive mode"""
        if not self.initialized:
            self.initialize()
        
        print("\n" + "=" * 80)
        print("INTERACTIVE MODE")
        print("=" * 80)
        print("\nEnter 'q' or 'quit' to exit\n")
        
        while True:
            try:
                # Get draft
                draft_input = input("Enter draft at perpendiculars (m): ").strip()
                if draft_input.lower() in ['q', 'quit', 'exit']:
                    print("\nExiting loadicator. Fair winds and following seas!")
                    break
                
                try:
                    draft = float(draft_input)
                except ValueError:
                    print("✗ Invalid draft. Please enter a number.")
                    continue
                
                # Get KG
                kg_input = input("Enter KG - Vertical Center of Gravity (m): ").strip()
                if kg_input.lower() in ['q', 'quit', 'exit']:
                    print("\nExiting loadicator. Fair winds and following seas!")
                    break
                
                try:
                    kg = float(kg_input)
                except ValueError:
                    print("✗ Invalid KG. Please enter a number.")
                    continue
                
                # Ask about outputs
                print("\nOutput options:")
                print("  1. Display report only")
                print("  2. Display report + save plot")
                print("  3. Display report + save PDF")
                print("  4. Display report + save plot + save PDF")
                
                output_choice = input("Select option (1-4) [default: 1]: ").strip() or "1"
                
                save_plot = None
                save_pdf = None
                
                if output_choice in ['2', '4']:
                    save_plot = f"gz_curve_draft{draft:.2f}_kg{kg:.2f}.png"
                
                if output_choice in ['3', '4']:
                    save_pdf = f"stability_report_draft{draft:.2f}_kg{kg:.2f}.pdf"
                
                # Perform calculation
                self.calculate(draft, kg, save_plot=save_plot, save_pdf=save_pdf)
                
                # Ask if user wants to continue
                print("\n" + "-" * 80)
                continue_input = input("\nCalculate another condition? (y/n) [y]: ").strip().lower()
                if continue_input in ['n', 'no']:
                    print("\nExiting loadicator. Fair winds and following seas!")
                    break
                
                print("\n")
                
            except KeyboardInterrupt:
                print("\n\nExiting loadicator. Fair winds and following seas!")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}\n")
                continue


def main():
    """Main entry point for command-line interface"""
    parser = argparse.ArgumentParser(
        description='MV Del Monte Loadicator - Stability Calculator and GZ Curve Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python loadicator.py
  
  # Calculate with specific values
  python loadicator.py --draft 10.0 --kg 8.5
  
  # Calculate and save outputs
  python loadicator.py --draft 10.0 --kg 8.5 --save-plot gz_curve.png --save-pdf report.pdf
  
  # Specify data directory
  python loadicator.py --data-dir /path/to/data --draft 10.0 --kg 8.5
        """
    )
    
    parser.add_argument('--draft', type=float, help='Draft at perpendiculars (m)')
    parser.add_argument('--kg', type=float, help='Vertical center of gravity KG (m)')
    parser.add_argument('--data-dir', default='.', help='Directory containing CSV data files (default: current directory)')
    parser.add_argument('--save-plot', help='Save GZ curve plot to file (e.g., gz_curve.png)')
    parser.add_argument('--save-pdf', help='Save complete PDF report to file (e.g., report.pdf)')
    parser.add_argument('--interactive', '-i', action='store_true', help='Run in interactive mode')
    parser.add_argument('--version', action='version', version='Loadicator v1.0')
    
    args = parser.parse_args()
    
    # Create loadicator instance
    loadicator = Loadicator(data_dir=args.data_dir)
    
    # Determine mode
    if args.interactive or (args.draft is None and args.kg is None):
        # Interactive mode
        loadicator.interactive_mode()
    else:
        # Command-line mode
        if args.draft is None or args.kg is None:
            parser.error("Both --draft and --kg are required for non-interactive mode")
        
        # Initialize and calculate
        loadicator.initialize()
        loadicator.calculate(
            draft=args.draft,
            kg=args.kg,
            save_plot=args.save_plot,
            save_pdf=args.save_pdf
        )


if __name__ == "__main__":
    main()
