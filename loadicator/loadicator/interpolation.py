"""
Interpolation Module for MV Del Monte Loadicator
Provides linear and 2D interpolation functions for hydrostatic and KN data
"""

import numpy as np
from scipy.interpolate import interp1d, interp2d


class Interpolator:
    """Handles interpolation of hydrostatic and KN curve data"""
    
    def __init__(self, data_loader):
        """
        Initialize interpolator with loaded data
        
        Args:
            data_loader: DataLoader instance with loaded data
        """
        self.data_loader = data_loader
        self.hydrostatic_data = data_loader.hydrostatic_data
        self.kn_curves = data_loader.kn_curves
        
    def interpolate_hydrostatic(self, draft, property_name):
        """
        Interpolate hydrostatic property at given draft
        
        Args:
            draft: Draft in meters
            property_name: Name of property to interpolate (e.g., 'Displacement', 'KB', 'TKM')
            
        Returns:
            Interpolated value
        """
        if self.hydrostatic_data is None:
            raise ValueError("Hydrostatic data not loaded")
        
        if property_name not in self.hydrostatic_data.columns:
            raise ValueError(f"Property '{property_name}' not found in hydrostatic data")
        
        # Get draft and property arrays
        drafts = self.hydrostatic_data['Draft'].values
        properties = self.hydrostatic_data[property_name].values
        
        # Check if draft is within range
        draft_min, draft_max = drafts.min(), drafts.max()
        if draft < draft_min or draft > draft_max:
            raise ValueError(f"Draft {draft:.2f}m is outside valid range [{draft_min:.2f}m, {draft_max:.2f}m]")
        
        # Linear interpolation
        interpolated_value = np.interp(draft, drafts, properties)
        
        return interpolated_value
    
    def interpolate_kn(self, displacement, heel_angle):
        """
        Interpolate KN value for given displacement and heel angle
        Uses 2D interpolation across displacement and heel angle
        
        Args:
            displacement: Displacement in tonnes
            heel_angle: Heel angle in degrees
            
        Returns:
            Interpolated KN value in meters
        """
        if self.kn_curves is None:
            raise ValueError("KN curves not loaded")
        
        # Get available heel angles
        available_angles = sorted(self.kn_curves.keys())
        
        # Check if heel angle is within range
        angle_min, angle_max = min(available_angles), max(available_angles)
        if heel_angle < 0 or heel_angle > angle_max:
            raise ValueError(f"Heel angle {heel_angle:.1f}° is outside valid range [0°, {angle_max:.1f}°]")
        
        # Special case: heel angle = 0
        if heel_angle == 0:
            return 0.0
        
        # Find the two closest heel angles
        if heel_angle in available_angles:
            # Exact match - interpolate only in displacement
            df = self.kn_curves[heel_angle]
            displacements = df['Displacement'].values
            kn_values = df['KN'].values
            
            # Check displacement range
            disp_min, disp_max = displacements.min(), displacements.max()
            if displacement < disp_min or displacement > disp_max:
                raise ValueError(f"Displacement {displacement:.0f}t is outside valid range [{disp_min:.0f}t, {disp_max:.0f}t]")
            
            kn = np.interp(displacement, displacements, kn_values)
            return kn
        
        else:
            # Need to interpolate between two heel angles
            # Find bounding angles
            lower_angle = max([a for a in available_angles if a < heel_angle])
            upper_angle = min([a for a in available_angles if a > heel_angle])
            
            # Get KN values at both angles
            df_lower = self.kn_curves[lower_angle]
            df_upper = self.kn_curves[upper_angle]
            
            displacements_lower = df_lower['Displacement'].values
            kn_lower_values = df_lower['KN'].values
            
            displacements_upper = df_upper['Displacement'].values
            kn_upper_values = df_upper['KN'].values
            
            # Check displacement range (use the more restrictive range)
            disp_min = max(displacements_lower.min(), displacements_upper.min())
            disp_max = min(displacements_lower.max(), displacements_upper.max())
            
            if displacement < disp_min or displacement > disp_max:
                raise ValueError(f"Displacement {displacement:.0f}t is outside valid range [{disp_min:.0f}t, {disp_max:.0f}t]")
            
            # Interpolate KN at both angles for the given displacement
            kn_lower = np.interp(displacement, displacements_lower, kn_lower_values)
            kn_upper = np.interp(displacement, displacements_upper, kn_upper_values)
            
            # Linear interpolation between the two angles
            kn = kn_lower + (heel_angle - lower_angle) * (kn_upper - kn_lower) / (upper_angle - lower_angle)
            
            return kn
    
    def get_all_hydrostatic_properties(self, draft):
        """
        Get all hydrostatic properties at given draft
        
        Args:
            draft: Draft in meters
            
        Returns:
            Dictionary with all hydrostatic properties
        """
        properties = {}
        
        # List of properties to interpolate
        property_names = ['Displacement', 'TPC', 'MTC', 'LCB', 'LCF', 'KB', 'TKM']
        
        for prop in property_names:
            if prop in self.hydrostatic_data.columns:
                properties[prop] = self.interpolate_hydrostatic(draft, prop)
        
        # Calculate KM
        if 'KB' in properties and 'TKM' in properties:
            properties['KM'] = properties['KB'] + properties['TKM']
        
        return properties
    
    def calculate_gz_curve(self, draft, kg, heel_angles=None):
        """
        Calculate GZ curve for given draft and KG
        
        Args:
            draft: Draft in meters
            kg: Vertical center of gravity (KG) in meters
            heel_angles: List of heel angles to calculate (default: 0 to 90 in 5° increments)
            
        Returns:
            Dictionary with heel angles and corresponding GZ values
        """
        if heel_angles is None:
            # Default heel angles: 0, 5, 10, 15, ..., 90
            heel_angles = list(range(0, 95, 5))
        
        # Get displacement at this draft
        displacement = self.interpolate_hydrostatic(draft, 'Displacement')
        
        # Get hydrostatic properties
        properties = self.get_all_hydrostatic_properties(draft)
        
        # Calculate GM
        km = properties['KM']
        gm = km - kg
        
        # Calculate GZ for each heel angle
        gz_curve = {
            'heel_angles': [],
            'gz_values': [],
            'kn_values': [],
            'displacement': displacement,
            'kg': kg,
            'km': km,
            'gm': gm,
            'kb': properties['KB']
        }
        
        for angle in heel_angles:
            # Get KN value
            if angle == 0:
                kn = 0.0
            else:
                try:
                    kn = self.interpolate_kn(displacement, angle)
                except ValueError:
                    # If angle is outside range, skip it
                    continue
            
            # Calculate GZ = KN - KG * sin(θ)
            gz = kn - kg * np.sin(np.radians(angle))
            
            gz_curve['heel_angles'].append(angle)
            gz_curve['gz_values'].append(gz)
            gz_curve['kn_values'].append(kn)
        
        return gz_curve
    
    def find_max_gz(self, gz_curve):
        """
        Find maximum GZ value and corresponding angle
        
        Args:
            gz_curve: GZ curve dictionary from calculate_gz_curve
            
        Returns:
            Tuple of (max_gz, angle_at_max_gz)
        """
        gz_values = gz_curve['gz_values']
        heel_angles = gz_curve['heel_angles']
        
        if not gz_values:
            return 0.0, 0.0
        
        max_gz = max(gz_values)
        max_idx = gz_values.index(max_gz)
        angle_at_max = heel_angles[max_idx]
        
        return max_gz, angle_at_max
    
    def find_vanishing_angle(self, gz_curve):
        """
        Find angle of vanishing stability (where GZ becomes negative)
        
        Args:
            gz_curve: GZ curve dictionary from calculate_gz_curve
            
        Returns:
            Angle of vanishing stability in degrees (or None if not found)
        """
        gz_values = gz_curve['gz_values']
        heel_angles = gz_curve['heel_angles']
        
        for i in range(len(gz_values) - 1):
            if gz_values[i] > 0 and gz_values[i + 1] <= 0:
                # Linear interpolation to find exact angle
                angle1, angle2 = heel_angles[i], heel_angles[i + 1]
                gz1, gz2 = gz_values[i], gz_values[i + 1]
                
                # Interpolate to find where GZ = 0
                vanishing_angle = angle1 - gz1 * (angle2 - angle1) / (gz2 - gz1)
                return vanishing_angle
        
        return None
    
    def calculate_gz_area(self, gz_curve, angle_start=0, angle_end=30):
        """
        Calculate area under GZ curve between two angles (for stability criteria)
        
        Args:
            gz_curve: GZ curve dictionary from calculate_gz_curve
            angle_start: Starting angle in degrees
            angle_end: Ending angle in degrees
            
        Returns:
            Area in meter-radians
        """
        gz_values = np.array(gz_curve['gz_values'])
        heel_angles = np.array(gz_curve['heel_angles'])
        
        # Filter to desired range
        mask = (heel_angles >= angle_start) & (heel_angles <= angle_end)
        angles_filtered = heel_angles[mask]
        gz_filtered = gz_values[mask]
        
        if len(angles_filtered) < 2:
            return 0.0
        
        # Convert angles to radians for integration
        angles_rad = np.radians(angles_filtered)
        
        # Trapezoidal integration
        area = np.trapz(gz_filtered, angles_rad)
        
        return area


if __name__ == "__main__":
    # Test the interpolator
    from data_loader import DataLoader
    
    print("=== Testing Interpolation Module ===\n")
    
    # Load data
    loader = DataLoader()
    loader.load_hydrostatic_data()
    loader.load_kn_curves()
    
    # Create interpolator
    interp = Interpolator(loader)
    
    # Test hydrostatic interpolation
    print("=== Test 1: Hydrostatic Interpolation ===")
    test_draft = 10.0
    displacement = interp.interpolate_hydrostatic(test_draft, 'Displacement')
    kb = interp.interpolate_hydrostatic(test_draft, 'KB')
    tkm = interp.interpolate_hydrostatic(test_draft, 'TKM')
    print(f"Draft: {test_draft:.2f}m")
    print(f"Displacement: {displacement:.0f} tonnes")
    print(f"KB: {kb:.3f}m")
    print(f"TKM: {tkm:.3f}m")
    print(f"KM: {kb + tkm:.3f}m")
    
    # Test KN interpolation
    print("\n=== Test 2: KN Interpolation ===")
    test_displacement = 50000
    test_angle = 30
    kn = interp.interpolate_kn(test_displacement, test_angle)
    print(f"Displacement: {test_displacement:.0f} tonnes")
    print(f"Heel Angle: {test_angle}°")
    print(f"KN: {kn:.3f}m")
    
    # Test GZ curve calculation
    print("\n=== Test 3: GZ Curve Calculation ===")
    test_draft = 10.0
    test_kg = 8.5
    gz_curve = interp.calculate_gz_curve(test_draft, test_kg)
    
    print(f"Draft: {test_draft:.2f}m")
    print(f"KG: {test_kg:.2f}m")
    print(f"Displacement: {gz_curve['displacement']:.0f} tonnes")
    print(f"GM: {gz_curve['gm']:.3f}m")
    print(f"\nGZ Values:")
    for angle, gz in zip(gz_curve['heel_angles'][:10], gz_curve['gz_values'][:10]):
        print(f"  {angle:3d}° : {gz:7.3f}m")
    
    # Find max GZ
    max_gz, angle_at_max = interp.find_max_gz(gz_curve)
    print(f"\nMax GZ: {max_gz:.3f}m at {angle_at_max:.1f}°")
    
    # Find vanishing angle
    vanishing = interp.find_vanishing_angle(gz_curve)
    if vanishing:
        print(f"Angle of vanishing stability: {vanishing:.1f}°")
    
    # Calculate area
    area_30 = interp.calculate_gz_area(gz_curve, 0, 30)
    print(f"Area 0-30°: {area_30:.4f} m·rad")
