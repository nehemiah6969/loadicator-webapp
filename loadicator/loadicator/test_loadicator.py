#!/usr/bin/env python3
"""
Test script for MV Del Monte Loadicator
Runs basic tests to verify functionality
"""

def test_data_loading():
    """Test that data files load correctly"""
    print("\n" + "=" * 80)
    print("TEST 1: Data Loading")
    print("=" * 80)
    
    try:
        from data_loader import DataLoader
        
        loader = DataLoader()
        hydro = loader.load_hydrostatic_data()
        kn = loader.load_kn_curves()
        loader.validate_data()
        
        print("\n✓ TEST 1 PASSED: Data loaded successfully")
        return True
    except Exception as e:
        print(f"\n✗ TEST 1 FAILED: {e}")
        return False


def test_interpolation():
    """Test interpolation functions"""
    print("\n" + "=" * 80)
    print("TEST 2: Interpolation")
    print("=" * 80)
    
    try:
        from data_loader import DataLoader
        from interpolation import Interpolator
        
        loader = DataLoader()
        loader.load_hydrostatic_data()
        loader.load_kn_curves()
        
        interp = Interpolator(loader)
        
        # Test hydrostatic interpolation
        draft = 10.0
        displacement = interp.interpolate_hydrostatic(draft, 'Displacement')
        print(f"\nDraft {draft}m → Displacement: {displacement:.0f} tonnes")
        
        # Test KN interpolation
        kn = interp.interpolate_kn(50000, 30)
        print(f"Displacement 50000t, Heel 30° → KN: {kn:.3f}m")
        
        print("\n✓ TEST 2 PASSED: Interpolation working")
        return True
    except Exception as e:
        print(f"\n✗ TEST 2 FAILED: {e}")
        return False


def test_gz_calculation():
    """Test GZ curve calculation"""
    print("\n" + "=" * 80)
    print("TEST 3: GZ Curve Calculation")
    print("=" * 80)
    
    try:
        from data_loader import DataLoader
        from interpolation import Interpolator
        
        loader = DataLoader()
        loader.load_hydrostatic_data()
        loader.load_kn_curves()
        
        interp = Interpolator(loader)
        
        # Calculate GZ curve
        draft = 10.0
        kg = 8.5
        gz_curve = interp.calculate_gz_curve(draft, kg)
        
        print(f"\nDraft: {draft}m, KG: {kg}m")
        print(f"Displacement: {gz_curve['displacement']:.0f} tonnes")
        print(f"GM: {gz_curve['gm']:.3f}m")
        print(f"\nFirst 5 GZ values:")
        for i in range(min(5, len(gz_curve['heel_angles']))):
            angle = gz_curve['heel_angles'][i]
            gz = gz_curve['gz_values'][i]
            print(f"  {angle:3d}° : {gz:7.3f}m")
        
        # Find max GZ
        max_gz, angle_at_max = interp.find_max_gz(gz_curve)
        print(f"\nMax GZ: {max_gz:.3f}m at {angle_at_max:.1f}°")
        
        print("\n✓ TEST 3 PASSED: GZ calculation working")
        return True
    except Exception as e:
        print(f"\n✗ TEST 3 FAILED: {e}")
        return False


def test_stability_calculator():
    """Test complete stability calculation"""
    print("\n" + "=" * 80)
    print("TEST 4: Stability Calculator")
    print("=" * 80)
    
    try:
        from data_loader import DataLoader
        from interpolation import Interpolator
        from calculator import StabilityCalculator
        
        loader = DataLoader()
        loader.load_hydrostatic_data()
        loader.load_kn_curves()
        
        interp = Interpolator(loader)
        calc = StabilityCalculator(interp)
        
        # Calculate stability
        draft = 10.0
        kg = 8.5
        results = calc.calculate_stability(draft, kg)
        
        print(f"\nDraft: {draft}m, KG: {kg}m")
        print(f"Displacement: {results['stability']['displacement']:.0f} tonnes")
        print(f"GM: {results['stability']['gm']:.3f}m")
        print(f"Max GZ: {results['stability']['max_gz']:.3f}m")
        
        # Check compliance
        compliance = results['compliance']
        print(f"\nIMO Compliance: {compliance['overall']['status']}")
        
        passed_count = sum(1 for k, v in compliance.items() if k != 'overall' and v['pass'])
        total_count = len([k for k in compliance.keys() if k != 'overall'])
        print(f"Passed {passed_count}/{total_count} criteria")
        
        print("\n✓ TEST 4 PASSED: Stability calculator working")
        return True
    except Exception as e:
        print(f"\n✗ TEST 4 FAILED: {e}")
        return False


def test_report_generation():
    """Test report generation"""
    print("\n" + "=" * 80)
    print("TEST 5: Report Generation")
    print("=" * 80)
    
    try:
        from data_loader import DataLoader
        from interpolation import Interpolator
        from calculator import StabilityCalculator
        
        loader = DataLoader()
        loader.load_hydrostatic_data()
        loader.load_kn_curves()
        
        interp = Interpolator(loader)
        calc = StabilityCalculator(interp)
        
        # Calculate and generate report
        results = calc.calculate_stability(10.0, 8.5)
        report = calc.generate_report(results)
        
        print(f"\nReport generated: {len(report)} characters")
        print("First 200 characters:")
        print(report[:200] + "...")
        
        print("\n✓ TEST 5 PASSED: Report generation working")
        return True
    except Exception as e:
        print(f"\n✗ TEST 5 FAILED: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("MV DEL MONTE LOADICATOR - TEST SUITE")
    print("=" * 80)
    
    tests = [
        test_data_loading,
        test_interpolation,
        test_gz_calculation,
        test_stability_calculator,
        test_report_generation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total} tests")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED!")
        print("\nThe loadicator is ready to use.")
        print("Run: python3 loadicator.py")
    else:
        print("\n✗ SOME TESTS FAILED")
        print("\nPlease check the error messages above.")
        print("Make sure all required packages are installed:")
        print("  pip3 install pandas numpy matplotlib scipy")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()
