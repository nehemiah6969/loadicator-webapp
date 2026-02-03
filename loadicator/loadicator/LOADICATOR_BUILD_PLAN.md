# MV Del Monte Loadicator - Detailed Build Plan

## Executive Summary
This document outlines the comprehensive plan to build a working Loadicator (stability calculator) for the MV Del Monte to verify the vessel's stability and generate GZ curves for Port State Control inspection.

---

## 1. Data Analysis & Understanding

### 1.1 Available Data Files

#### **Ship Particulars.md**
- Vessel identification and key dimensions
- Length between perpendiculars: 216.00m
- Summer Load Draft: 13.02m
- Summer Displacement: 77,165 tonnes
- Light Displacement: 10,553 tonnes
- Draft mark corrections for forward, midships, and aft positions

#### **Hydrostatic Data.csv**
- **Range**: Draft from 2.00m to 13.02m (1,225 data points)
- **Columns**:
  - Draft (m): Mean draft at perpendiculars
  - Δ (tonne): Displacement in tonnes
  - Diff: Difference between consecutive displacements
  - TPC (tonnes): Tonnes Per Centimeter immersion
  - MTC (t-m): Moment to Change trim by 1cm
  - LCB (m): Longitudinal Center of Buoyancy (forward of midships)
  - LCF (m): Longitudinal Center of Flotation (forward of midships)
  - KB (m): Height of Center of Buoyancy above keel
  - TKM (m): Transverse metacentric radius

#### **KN Curves.csv**
- **Cross curves of stability** at various heel angles
- **Heel angles**: 5°, 10°, 12°, 15°, 20°, 25°, 30°, 35°, 40°, 50°, 60°, 75°, 90°
- **Data format**: X-Y pairs where:
  - X = Displacement (tonnes)
  - Y = KN value (meters)
- **Displacement range**: Approximately 4,000 to 110,000 tonnes
- Each heel angle has multiple displacement-KN data points for interpolation

---

## 2. Stability Theory & Calculations

### 2.1 Key Stability Concepts

**GZ (Righting Lever)**:
```
GZ = KN - KG × sin(θ)
```
Where:
- GZ = Righting lever (m)
- KN = Cross curve value from stability data (m)
- KG = Vertical Center of Gravity above keel (m)
- θ = Heel angle (degrees)

**Metacentric Height (GM)**:
```
GM = KM - KG
where KM = KB + BM
```
For transverse stability:
```
BM = TKM (from hydrostatic data)
KM = KB + TKM
```

### 2.2 Calculation Workflow

1. **Input Parameters**:
   - Draft at perpendiculars (m)
   - KG (Vertical Center of Gravity) (m)

2. **Interpolate Hydrostatic Properties**:
   - From draft → Displacement (Δ)
   - From draft → KB, TKM
   - Calculate KM = KB + TKM
   - Calculate GM = KM - KG

3. **Generate GZ Curve**:
   - For each heel angle (0° to 90°):
     - Interpolate KN value from cross curves using displacement
     - Calculate GZ = KN - KG × sin(θ)
     - Store (θ, GZ) pairs

4. **Output Results**:
   - Displacement value
   - Tabulated GZ values at standard heel angles
   - Graphical GZ curve

---

## 3. Technical Implementation Plan

### 3.1 Platform Selection

**Option A: Excel-based Loadicator** (Recommended for immediate use)
- **Pros**: Familiar interface, portable, no installation required
- **Cons**: Limited automation, manual data entry

**Option B: Python-based Loadicator** (Recommended for flexibility)
- **Pros**: Automated calculations, better visualization, extensible
- **Cons**: Requires Python installation

**Recommendation**: Build both versions
- Excel for quick reference and backup
- Python for advanced features and automation

### 3.2 Data Structure & Storage

#### Excel Implementation:
- **Sheet 1**: Input Form
- **Sheet 2**: Hydrostatic Data (imported from CSV)
- **Sheet 3**: KN Curves Data (imported from CSV)
- **Sheet 4**: Calculations & Results
- **Sheet 5**: GZ Curve Chart

#### Python Implementation:
- Store CSV files in project directory
- Use pandas for data manipulation
- Use numpy for interpolation
- Use matplotlib for visualization

---

## 4. Detailed Feature Specifications

### 4.1 Input Module

**Required Inputs**:
1. **Draft at Perpendiculars** (m)
   - Range: 2.00m to 13.02m
   - Validation: Must be within hydrostatic data range
   - Precision: 0.01m

2. **KG - Vertical Center of Gravity** (m)
   - Range: Typically 1.0m to 15.0m
   - Validation: Must be physically reasonable
   - Precision: 0.01m

**Optional Inputs** (for future enhancement):
- Draft corrections (forward, aft, midships)
- Trim calculation
- Free surface corrections

### 4.2 Interpolation Module

**Linear Interpolation Requirements**:

1. **Hydrostatic Data Interpolation**:
   - Input: Draft value
   - Output: Displacement, KB, TKM, LCB, LCF, TPC, MTC
   - Method: Linear interpolation between adjacent draft values

2. **KN Curves Interpolation**:
   - Input: Displacement and heel angle
   - Output: KN value
   - Method: 2D interpolation
     - First: Interpolate within each heel angle for given displacement
     - Second: If exact heel angle not available, interpolate between angles

**Interpolation Formula** (Linear):
```
y = y₁ + (x - x₁) × (y₂ - y₁) / (x₂ - x₁)
```

### 4.3 Calculation Module

**Core Calculations**:

1. **From Draft → Displacement**:
   ```
   Δ = interpolate(Draft, Hydrostatic_Data)
   ```

2. **From Draft → KB and TKM**:
   ```
   KB = interpolate(Draft, Hydrostatic_Data)
   TKM = interpolate(Draft, Hydrostatic_Data)
   ```

3. **Calculate KM**:
   ```
   KM = KB + TKM
   ```

4. **Calculate GM**:
   ```
   GM = KM - KG
   ```

5. **For each heel angle θ**:
   ```
   KN(θ) = interpolate(Displacement, θ, KN_Curves_Data)
   GZ(θ) = KN(θ) - KG × sin(θ)
   ```

6. **Standard heel angles to calculate**:
   - 0°, 5°, 10°, 15°, 20°, 25°, 30°, 35°, 40°, 45°, 50°, 60°, 70°, 75°, 80°, 90°

### 4.4 Output Module

**Tabular Output**:
```
STABILITY CALCULATION RESULTS
Vessel: MV Del Monte
Date: [Current Date]
-----------------------------------
INPUT DATA:
Draft at Perpendiculars: X.XX m
KG (Vertical Center of Gravity): X.XX m

CALCULATED VALUES:
Displacement (Δ): XXXXX tonnes
KB (Center of Buoyancy): X.XX m
KM (Transverse Metacenter): X.XX m
GM (Metacentric Height): X.XX m

GZ CURVE DATA:
Heel Angle (°) | KN (m) | GZ (m)
---------------|--------|--------
0              | X.XX   | X.XX
5              | X.XX   | X.XX
10             | X.XX   | X.XX
...
90             | X.XX   | X.XX
```

**Graphical Output**:
- X-axis: Heel Angle (degrees) from 0° to 90°
- Y-axis: GZ (Righting Lever) in meters
- Grid lines for easy reading
- Title: "GZ Curve - MV Del Monte"
- Legend showing Draft and KG values

### 4.5 Validation Module

**Data Validation Checks**:

1. **Input Validation**:
   - Draft within range [2.00m, 13.02m]
   - KG > 0 and KG < KM (for positive stability)
   - GM > 0 (positive initial stability)

2. **Calculation Validation**:
   - Displacement matches expected range
   - GZ curve has positive area (stable vessel)
   - Maximum GZ occurs at reasonable angle (typically 30-40°)

3. **Warning Flags**:
   - GM < 0.15m (critically low stability)
   - Maximum GZ < 0.20m (insufficient stability)
   - Angle of vanishing stability < 40° (poor stability range)

---

## 5. Implementation Steps

### Phase 1: Data Preparation (Day 1)
1. ✓ Review and understand all data files
2. Clean and validate CSV data
3. Identify data ranges and limitations
4. Document data structure

### Phase 2: Excel Implementation (Day 1-2)
1. Create Excel workbook structure
2. Import CSV data into appropriate sheets
3. Build input form with data validation
4. Implement VLOOKUP/INDEX-MATCH for interpolation
5. Create calculation formulas for GZ curve
6. Design output table
7. Create GZ curve chart
8. Test with known values
9. Add user instructions

### Phase 3: Python Implementation (Day 2-3)
1. Set up Python environment (pandas, numpy, matplotlib)
2. Create data loading functions
3. Implement interpolation functions
4. Build calculation engine
5. Create visualization module
6. Design user interface (CLI or GUI)
7. Add input validation
8. Implement error handling
9. Create output formatting
10. Test thoroughly

### Phase 4: Verification & Testing (Day 3)
1. Test with multiple draft/KG combinations
2. Verify calculations against manual calculations
3. Check interpolation accuracy
4. Validate GZ curve shapes
5. Test edge cases (minimum/maximum drafts)
6. Document test results

### Phase 5: Documentation (Day 3-4)
1. User manual for Excel version
2. User manual for Python version
3. Calculation methodology document
4. Validation test report
5. Quick reference guide

---

## 6. Excel-Specific Implementation Details

### 6.1 Workbook Structure

**Sheet 1: INPUT**
- Cell B2: Draft (m) - with data validation
- Cell B3: KG (m) - with data validation
- Cell B5: Calculate button (macro or formula trigger)

**Sheet 2: HYDROSTATIC_DATA**
- Import from "Hydrostatic Data.csv"
- Columns: Draft, Displacement, Diff, TPC, MTC, LCB, LCF, KB, TKM

**Sheet 3: KN_CURVES**
- Import from "KN Curves.csv"
- Separate columns for each heel angle
- Format: Displacement | KN_5deg | KN_10deg | ... | KN_90deg

**Sheet 4: CALCULATIONS**
- Intermediate calculations
- Interpolated values
- GZ calculations for each heel angle

**Sheet 5: RESULTS**
- Summary output table
- GZ curve chart
- Stability assessment

### 6.2 Key Excel Formulas

**Interpolation Formula** (for Displacement from Draft):
```excel
=INDEX(HYDROSTATIC_DATA!B:B, MATCH(INPUT!B2, HYDROSTATIC_DATA!A:A, 1)) + 
 (INPUT!B2 - INDEX(HYDROSTATIC_DATA!A:A, MATCH(INPUT!B2, HYDROSTATIC_DATA!A:A, 1))) * 
 (INDEX(HYDROSTATIC_DATA!B:B, MATCH(INPUT!B2, HYDROSTATIC_DATA!A:A, 1)+1) - 
  INDEX(HYDROSTATIC_DATA!B:B, MATCH(INPUT!B2, HYDROSTATIC_DATA!A:A, 1))) / 
 (INDEX(HYDROSTATIC_DATA!A:A, MATCH(INPUT!B2, HYDROSTATIC_DATA!A:A, 1)+1) - 
  INDEX(HYDROSTATIC_DATA!A:A, MATCH(INPUT!B2, HYDROSTATIC_DATA!A:A, 1)))
```

**GZ Calculation**:
```excel
=KN_value - INPUT!B3 * SIN(RADIANS(heel_angle))
```

### 6.3 Chart Configuration

- Chart Type: XY Scatter with Smooth Lines
- X-axis: Heel Angle (0-90°)
- Y-axis: GZ (meters)
- Gridlines: Major horizontal and vertical
- Data labels: Optional at key points

---

## 7. Python-Specific Implementation Details

### 7.1 Project Structure
```
loadicator/
│
├── data/
│   ├── Hydrostatic Data.csv
│   ├── KN Curves.csv
│   └── Ship Particulars.md
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── interpolation.py
│   ├── calculator.py
│   ├── visualizer.py
│   └── main.py
│
├── tests/
│   └── test_calculations.py
│
├── requirements.txt
└── README.md
```

### 7.2 Key Python Modules

**data_loader.py**:
- Load CSV files into pandas DataFrames
- Parse and validate data
- Handle missing values

**interpolation.py**:
- Linear interpolation functions
- 2D interpolation for KN curves
- Extrapolation handling

**calculator.py**:
- Main calculation engine
- GZ curve generation
- Stability parameters calculation

**visualizer.py**:
- Matplotlib plotting functions
- GZ curve visualization
- Export to PDF/PNG

**main.py**:
- User interface (CLI or GUI)
- Input handling
- Output formatting

### 7.3 Key Python Libraries
```
pandas>=1.3.0
numpy>=1.21.0
matplotlib>=3.4.0
scipy>=1.7.0
```

---

## 8. Validation & Testing Strategy

### 8.1 Test Cases

**Test Case 1: Light Ship Condition**
- Draft: 2.01m
- KG: 7.0m
- Expected Displacement: ~10,553 tonnes
- Expected: Positive GM, stable GZ curve

**Test Case 2: Loaded Condition**
- Draft: 10.00m
- KG: 8.5m
- Expected Displacement: ~58,171 tonnes
- Expected: Positive GM, typical cargo ship GZ curve

**Test Case 3: Summer Draft**
- Draft: 13.02m
- KG: 9.0m
- Expected Displacement: ~77,165 tonnes
- Expected: Adequate stability for departure

**Test Case 4: Edge Cases**
- Minimum draft (2.00m)
- Maximum draft (13.02m)
- High KG scenarios
- Low KG scenarios

### 8.2 Validation Criteria

1. **Displacement Accuracy**: ±0.5% of tabulated value
2. **Interpolation Accuracy**: Smooth curves, no discontinuities
3. **GZ Curve Shape**: Physically realistic (rise, peak, decline)
4. **GM Calculation**: Matches manual calculation
5. **Stability Criteria**: Meets IMO intact stability requirements

---

## 9. Deliverables

### 9.1 Excel Loadicator
- Single Excel file (.xlsx)
- All data embedded
- User-friendly interface
- Automated calculations
- Professional output format

### 9.2 Python Loadicator
- Complete Python package
- Source code with comments
- Requirements file
- User documentation
- Test suite

### 9.3 Documentation
- Build plan (this document)
- User manual
- Technical reference
- Validation report
- Quick start guide

---

## 10. Future Enhancements

### 10.1 Phase 2 Features
1. Trim correction calculations
2. Free surface effect corrections
3. Wind heeling moment calculations
4. Grain heeling moment calculations
5. Loading condition management
6. Multiple loading scenarios comparison

### 10.2 Phase 3 Features
1. Web-based interface
2. Mobile app version
3. Database integration
4. Automated report generation
5. Regulatory compliance checking
6. Historical data tracking

---

## 11. Regulatory Compliance

### 11.1 IMO Intact Stability Code Requirements

The loadicator should verify:
1. **Area under GZ curve**:
   - Area 0-30°: ≥ 0.055 m·rad
   - Area 0-40° or flooding angle: ≥ 0.090 m·rad
   - Area 30-40°: ≥ 0.030 m·rad

2. **Righting lever GZ**:
   - GZ ≥ 0.20 m at angle ≥ 30°

3. **Maximum GZ**:
   - Occurs at angle ≥ 25°

4. **Initial metacentric height GM**:
   - GM ≥ 0.15 m

### 11.2 Output Compliance Statement
The loadicator should include a compliance check section indicating whether the vessel meets these criteria.

---

## 12. Risk Assessment & Mitigation

### 12.1 Potential Risks

1. **Data Interpolation Errors**:
   - Risk: Inaccurate GZ values
   - Mitigation: Validate against known values, use proven interpolation methods

2. **User Input Errors**:
   - Risk: Invalid draft or KG values
   - Mitigation: Input validation, range checking, warning messages

3. **Calculation Errors**:
   - Risk: Incorrect stability assessment
   - Mitigation: Thorough testing, peer review, comparison with approved software

4. **Data File Corruption**:
   - Risk: Loss of vessel data
   - Mitigation: Backup copies, data validation on load

### 12.2 Quality Assurance

1. Independent verification of calculations
2. Comparison with vessel's approved loadicator (when available)
3. Testing by qualified marine personnel
4. Documentation of all assumptions and limitations

---

## 13. Timeline & Milestones

| Phase | Duration | Milestone |
|-------|----------|-----------|
| Data Analysis | 0.5 days | Data structure documented |
| Excel Development | 1.5 days | Working Excel loadicator |
| Python Development | 2 days | Working Python loadicator |
| Testing & Validation | 1 day | All test cases passed |
| Documentation | 1 day | Complete user manuals |
| **Total** | **6 days** | **Fully functional loadicator** |

---

## 14. Success Criteria

The loadicator will be considered successful when:

1. ✓ Accepts draft and KG as inputs
2. ✓ Calculates displacement accurately
3. ✓ Generates complete GZ curve (0-90°)
4. ✓ Produces clear graphical output
5. ✓ Provides tabulated results
6. ✓ Validates input data
7. ✓ Handles edge cases gracefully
8. ✓ Produces professional output suitable for PSC inspection
9. ✓ Calculations verified against manual methods
10. ✓ User documentation complete

---

## 15. Conclusion

This loadicator will provide the MV Del Monte with a reliable tool for stability verification during the loading computer failure. The dual implementation (Excel and Python) ensures both immediate usability and long-term flexibility. The systematic approach to data interpolation and calculation ensures accuracy and compliance with maritime stability requirements.

**Next Steps**: 
1. Await approval to proceed with code implementation
2. Begin with Excel version for immediate deployment
3. Follow with Python version for enhanced capabilities
4. Conduct thorough testing before operational use

---

**Document Version**: 1.0  
**Date**: January 12, 2026  
**Prepared for**: MV Del Monte - 2nd Officer  
**Status**: Ready for Implementation
