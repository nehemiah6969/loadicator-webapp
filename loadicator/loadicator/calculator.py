"""
Stability Calculator Module for MV Del Monte Loadicator
Performs stability calculations and IMO compliance checks
"""

import numpy as np
from datetime import datetime


class StabilityCalculator:
    """Performs stability calculations and compliance checks"""
    
    def __init__(self, interpolator):
        """
        Initialize calculator with interpolator
        
        Args:
            interpolator: Interpolator instance with loaded data
        """
        self.interpolator = interpolator
        
    def calculate_stability(self, draft, kg):
        """
        Calculate complete stability analysis for given draft and KG
        
        Args:
            draft: Draft in meters
            kg: Vertical center of gravity (KG) in meters
            
        Returns:
            Dictionary with all stability parameters and GZ curve
        """
        # Get hydrostatic properties
        properties = self.interpolator.get_all_hydrostatic_properties(draft)
        
        # Calculate GZ curve
        gz_curve = self.interpolator.calculate_gz_curve(draft, kg)
        
        # Find key stability parameters
        max_gz, angle_at_max_gz = self.interpolator.find_max_gz(gz_curve)
        vanishing_angle = self.interpolator.find_vanishing_angle(gz_curve)
        
        # Calculate areas under GZ curve (for IMO criteria)
        area_0_30 = self.interpolator.calculate_gz_area(gz_curve, 0, 30)
        area_0_40 = self.interpolator.calculate_gz_area(gz_curve, 0, 40)
        area_30_40 = self.interpolator.calculate_gz_area(gz_curve, 30, 40)
        
        # Get GZ at 30 degrees
        gz_at_30 = self._get_gz_at_angle(gz_curve, 30)
        
        # Compile results
        results = {
            'input': {
                'draft': draft,
                'kg': kg,
                'calculation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            'hydrostatic': properties,
            'stability': {
                'displacement': properties['Displacement'],
                'kb': properties['KB'],
                'km': properties['KM'],
                'gm': properties['KM'] - kg,
                'max_gz': max_gz,
                'angle_at_max_gz': angle_at_max_gz,
                'vanishing_angle': vanishing_angle,
                'gz_at_30': gz_at_30
            },
            'areas': {
                'area_0_30': area_0_30,
                'area_0_40': area_0_40,
                'area_30_40': area_30_40
            },
            'gz_curve': gz_curve,
            'compliance': self.check_imo_compliance(gz_curve, properties['KM'] - kg)
        }
        
        return results
    
    def _get_gz_at_angle(self, gz_curve, target_angle):
        """Get GZ value at specific angle (with interpolation if needed)"""
        heel_angles = gz_curve['heel_angles']
        gz_values = gz_curve['gz_values']
        
        if target_angle in heel_angles:
            idx = heel_angles.index(target_angle)
            return gz_values[idx]
        
        # Interpolate
        return np.interp(target_angle, heel_angles, gz_values)
    
    def check_imo_compliance(self, gz_curve, gm):
        """
        Check compliance with IMO Intact Stability Code
        
        Args:
            gz_curve: GZ curve dictionary
            gm: Metacentric height (GM) in meters
            
        Returns:
            Dictionary with compliance status for each criterion
        """
        # Calculate required values
        max_gz, angle_at_max_gz = self.interpolator.find_max_gz(gz_curve)
        gz_at_30 = self._get_gz_at_angle(gz_curve, 30)
        area_0_30 = self.interpolator.calculate_gz_area(gz_curve, 0, 30)
        area_0_40 = self.interpolator.calculate_gz_area(gz_curve, 0, 40)
        area_30_40 = self.interpolator.calculate_gz_area(gz_curve, 30, 40)
        
        # IMO Intact Stability Code Requirements
        compliance = {
            'gm_criterion': {
                'requirement': 'GM ≥ 0.15 m',
                'value': gm,
                'limit': 0.15,
                'pass': gm >= 0.15,
                'status': 'PASS' if gm >= 0.15 else 'FAIL'
            },
            'area_0_30_criterion': {
                'requirement': 'Area 0-30° ≥ 0.055 m·rad',
                'value': area_0_30,
                'limit': 0.055,
                'pass': area_0_30 >= 0.055,
                'status': 'PASS' if area_0_30 >= 0.055 else 'FAIL'
            },
            'area_0_40_criterion': {
                'requirement': 'Area 0-40° ≥ 0.090 m·rad',
                'value': area_0_40,
                'limit': 0.090,
                'pass': area_0_40 >= 0.090,
                'status': 'PASS' if area_0_40 >= 0.090 else 'FAIL'
            },
            'area_30_40_criterion': {
                'requirement': 'Area 30-40° ≥ 0.030 m·rad',
                'value': area_30_40,
                'limit': 0.030,
                'pass': area_30_40 >= 0.030,
                'status': 'PASS' if area_30_40 >= 0.030 else 'FAIL'
            },
            'gz_30_criterion': {
                'requirement': 'GZ at 30° ≥ 0.20 m',
                'value': gz_at_30,
                'limit': 0.20,
                'pass': gz_at_30 >= 0.20,
                'status': 'PASS' if gz_at_30 >= 0.20 else 'FAIL'
            },
            'max_gz_angle_criterion': {
                'requirement': 'Angle of max GZ ≥ 25°',
                'value': angle_at_max_gz,
                'limit': 25.0,
                'pass': angle_at_max_gz >= 25.0,
                'status': 'PASS' if angle_at_max_gz >= 25.0 else 'FAIL'
            }
        }
        
        # Overall compliance
        all_pass = all(criterion['pass'] for criterion in compliance.values())
        compliance['overall'] = {
            'status': 'COMPLIANT' if all_pass else 'NON-COMPLIANT',
            'pass': all_pass
        }
        
        return compliance
    
    def generate_report(self, results):
        """
        Generate text report of stability calculation
        
        Args:
            results: Results dictionary from calculate_stability
            
        Returns:
            Formatted text report
        """
        report = []
        report.append("=" * 80)
        report.append("STABILITY CALCULATION REPORT")
        report.append("MV DEL MONTE - LOADICATOR")
        report.append("=" * 80)
        report.append("")
        
        # Input data
        report.append("INPUT DATA:")
        report.append(f"  Draft at Perpendiculars: {results['input']['draft']:.2f} m")
        report.append(f"  KG (Vertical Center of Gravity): {results['input']['kg']:.2f} m")
        report.append(f"  Calculation Time: {results['input']['calculation_time']}")
        report.append("")
        
        # Calculated values
        report.append("CALCULATED VALUES:")
        report.append(f"  Displacement (Δ): {results['stability']['displacement']:,.0f} tonnes")
        report.append(f"  KB (Center of Buoyancy): {results['stability']['kb']:.3f} m")
        report.append(f"  KM (Transverse Metacenter): {results['stability']['km']:.3f} m")
        report.append(f"  GM (Metacentric Height): {results['stability']['gm']:.3f} m")
        report.append("")
        
        # Stability parameters
        report.append("STABILITY PARAMETERS:")
        report.append(f"  Maximum GZ: {results['stability']['max_gz']:.3f} m")
        report.append(f"  Angle at Maximum GZ: {results['stability']['angle_at_max_gz']:.1f}°")
        if results['stability']['vanishing_angle']:
            report.append(f"  Angle of Vanishing Stability: {results['stability']['vanishing_angle']:.1f}°")
        report.append(f"  GZ at 30°: {results['stability']['gz_at_30']:.3f} m")
        report.append("")
        
        # Areas under GZ curve
        report.append("AREAS UNDER GZ CURVE:")
        report.append(f"  Area 0-30°: {results['areas']['area_0_30']:.4f} m·rad")
        report.append(f"  Area 0-40°: {results['areas']['area_0_40']:.4f} m·rad")
        report.append(f"  Area 30-40°: {results['areas']['area_30_40']:.4f} m·rad")
        report.append("")
        
        # GZ curve data
        report.append("GZ CURVE DATA:")
        report.append("  Heel Angle (°) | KN (m)  | GZ (m)")
        report.append("  " + "-" * 40)
        
        gz_curve = results['gz_curve']
        for angle, kn, gz in zip(gz_curve['heel_angles'], gz_curve['kn_values'], gz_curve['gz_values']):
            report.append(f"       {angle:3d}       | {kn:7.3f} | {gz:7.3f}")
        
        report.append("")
        
        # IMO Compliance
        report.append("=" * 80)
        report.append("IMO INTACT STABILITY CODE COMPLIANCE CHECK")
        report.append("=" * 80)
        report.append("")
        
        compliance = results['compliance']
        
        for key, criterion in compliance.items():
            if key == 'overall':
                continue
            
            report.append(f"  {criterion['requirement']}")
            report.append(f"    Value: {criterion['value']:.4f}")
            report.append(f"    Status: {criterion['status']}")
            report.append("")
        
        # Overall compliance
        report.append("-" * 80)
        report.append(f"OVERALL COMPLIANCE: {compliance['overall']['status']}")
        report.append("-" * 80)
        report.append("")
        
        if compliance['overall']['pass']:
            report.append("✓ The vessel meets all IMO Intact Stability Code requirements.")
        else:
            report.append("✗ The vessel does NOT meet all IMO Intact Stability Code requirements.")
            report.append("  Please review failed criteria and adjust loading condition.")
        
        report.append("")
        report.append("=" * 80)
        report.append("END OF REPORT")
        report.append("=" * 80)
        
        return "\n".join(report)


if __name__ == "__main__":
    # Test the calculator
    from data_loader import DataLoader
    from interpolation import Interpolator
    
    print("=== Testing Stability Calculator ===\n")
    
    # Load data
    loader = DataLoader()
    loader.load_hydrostatic_data()
    loader.load_kn_curves()
    
    # Create interpolator and calculator
    interp = Interpolator(loader)
    calc = StabilityCalculator(interp)
    
    # Test calculation
    print("=== Test Case: Loaded Condition ===")
    test_draft = 10.0
    test_kg = 8.5
    
    results = calc.calculate_stability(test_draft, test_kg)
    
    # Generate and print report
    report = calc.generate_report(results)
    print(report)
