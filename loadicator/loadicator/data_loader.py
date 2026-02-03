"""
Data Loader Module for MV Del Monte Loadicator
Loads and parses hydrostatic data and KN curves from CSV files or embedded data
"""

import pandas as pd
import numpy as np
from pathlib import Path
from io import StringIO


class DataLoader:
    """Handles loading and parsing of vessel stability data"""

    def __init__(self, data_dir=".", use_embedded=False):
        """
        Initialize data loader

        Args:
            data_dir: Directory containing the CSV files (ignored if use_embedded=True)
            use_embedded: If True, load data from embedded_data.py instead of files
        """
        self.data_dir = Path(data_dir)
        self.use_embedded = use_embedded
        self.hydrostatic_data = None
        self.kn_curves = None
        
    def load_hydrostatic_data(self, filename="Hydrostatic Data.csv"):
        """
        Load hydrostatic data from CSV file or embedded data

        Args:
            filename: Name of the hydrostatic data CSV file (ignored if use_embedded=True)

        Returns:
            pandas DataFrame with hydrostatic properties
        """
        if self.use_embedded:
            import embedded_data
            df = pd.read_csv(StringIO(embedded_data.HYDROSTATIC_DATA))
        else:
            filepath = self.data_dir / filename
            df = pd.read_csv(filepath)
        
        # Clean column names (remove special characters)
        df.columns = df.columns.str.strip()
        
        # Rename columns for easier access
        column_mapping = {
            'Draft (m)': 'Draft',
            'Δ(tonne)': 'Displacement',
            'Diff': 'Diff',
            'TPC (tonnes)': 'TPC',
            'MTC (t ‐ m)': 'MTC',
            'LCB (m)': 'LCB',
            'LCF (m)': 'LCF',
            'KB (m)': 'KB',
            'TKM (m)': 'TKM'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Remove any duplicate rows
        df = df.drop_duplicates(subset=['Draft'])
        
        # Sort by draft
        df = df.sort_values('Draft').reset_index(drop=True)
        
        self.hydrostatic_data = df
        
        print(f"✓ Loaded hydrostatic data: {len(df)} data points")
        print(f"  Draft range: {df['Draft'].min():.2f}m to {df['Draft'].max():.2f}m")
        print(f"  Displacement range: {df['Displacement'].min():.0f} to {df['Displacement'].max():.0f} tonnes")
        
        return df
    
    def load_kn_curves(self, filename="KN Curves.csv"):
        """
        Load KN curves (cross curves of stability) from CSV file or embedded data

        Args:
            filename: Name of the KN curves CSV file (ignored if use_embedded=True)

        Returns:
            Dictionary with heel angles as keys and DataFrames as values
        """
        if self.use_embedded:
            import embedded_data
            df = pd.read_csv(StringIO(embedded_data.KN_CURVES_DATA))
        else:
            filepath = self.data_dir / filename
            df = pd.read_csv(filepath)
        
        # Parse the header to get heel angles
        # Format: "5 degrees", "10 degrees", etc.
        header = df.columns.tolist()
        
        # Extract heel angles from header
        heel_angles = []
        for i in range(0, len(header), 2):
            if i < len(header):
                col_name = header[i]
                # Extract number from column name (e.g., "5 degrees" -> 5)
                try:
                    angle = float(col_name.split()[0])
                    heel_angles.append(angle)
                except:
                    pass
        
        # Parse data into dictionary of DataFrames
        kn_curves = {}
        
        for idx, angle in enumerate(heel_angles):
            x_col = idx * 2
            y_col = idx * 2 + 1
            
            if y_col < len(header):
                # Extract X (displacement) and Y (KN) columns
                x_data = df.iloc[:, x_col].dropna()
                y_data = df.iloc[:, y_col].dropna()
                
                # Ensure same length
                min_len = min(len(x_data), len(y_data))
                x_data = x_data.iloc[:min_len]
                y_data = y_data.iloc[:min_len]
                
                # Create DataFrame for this heel angle
                angle_df = pd.DataFrame({
                    'Displacement': pd.to_numeric(x_data.values, errors='coerce'),
                    'KN': pd.to_numeric(y_data.values, errors='coerce')
                })
                
                # Remove any rows with invalid data
                angle_df = angle_df.dropna()
                
                # Sort by displacement
                angle_df = angle_df.sort_values('Displacement').reset_index(drop=True)
                
                kn_curves[angle] = angle_df
        
        self.kn_curves = kn_curves
        
        print(f"✓ Loaded KN curves: {len(kn_curves)} heel angles")
        print(f"  Heel angles: {sorted(kn_curves.keys())}°")
        
        # Print displacement range for first angle
        if kn_curves:
            first_angle = sorted(kn_curves.keys())[0]
            first_df = kn_curves[first_angle]
            print(f"  Displacement range: {first_df['Displacement'].min():.0f} to {first_df['Displacement'].max():.0f} tonnes")
        
        return kn_curves
    
    def get_draft_range(self):
        """Get the valid draft range from hydrostatic data"""
        if self.hydrostatic_data is None:
            return None, None
        return self.hydrostatic_data['Draft'].min(), self.hydrostatic_data['Draft'].max()
    
    def get_displacement_range(self):
        """Get the valid displacement range from KN curves"""
        if self.kn_curves is None:
            return None, None
        
        # Get range from first heel angle
        first_angle = sorted(self.kn_curves.keys())[0]
        df = self.kn_curves[first_angle]
        return df['Displacement'].min(), df['Displacement'].max()
    
    def validate_data(self):
        """Validate that all required data is loaded"""
        if self.hydrostatic_data is None:
            raise ValueError("Hydrostatic data not loaded")
        
        if self.kn_curves is None:
            raise ValueError("KN curves not loaded")
        
        # Check for required columns in hydrostatic data
        required_cols = ['Draft', 'Displacement', 'KB', 'TKM']
        missing_cols = [col for col in required_cols if col not in self.hydrostatic_data.columns]
        
        if missing_cols:
            raise ValueError(f"Missing columns in hydrostatic data: {missing_cols}")
        
        print("✓ Data validation passed")
        return True


if __name__ == "__main__":
    # Test the data loader
    loader = DataLoader()
    
    print("\n=== Loading Hydrostatic Data ===")
    hydro = loader.load_hydrostatic_data()
    
    print("\n=== Loading KN Curves ===")
    kn = loader.load_kn_curves()
    
    print("\n=== Validating Data ===")
    loader.validate_data()
    
    print("\n=== Data Summary ===")
    draft_min, draft_max = loader.get_draft_range()
    print(f"Valid draft range: {draft_min:.2f}m to {draft_max:.2f}m")
    
    disp_min, disp_max = loader.get_displacement_range()
    print(f"Valid displacement range: {disp_min:.0f} to {disp_max:.0f} tonnes")
