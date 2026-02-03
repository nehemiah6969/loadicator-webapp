# Quick Start Guide - MV Del Monte Loadicator

## Installation Steps

### 1. Install Required Python Packages

Run this command in your terminal:

```bash
pip3 install pandas numpy matplotlib scipy
```

Or use the requirements file:

```bash
pip3 install -r requirements.txt
```

### 2. Verify Installation

Test that the data loads correctly:

```bash
python3 data_loader.py
```

You should see:
```
✓ Loaded hydrostatic data: 1225 data points
✓ Loaded KN curves: 13 heel angles
✓ Data validation passed
```

### 3. Run Your First Calculation

**Interactive Mode** (Easiest):
```bash
python3 loadicator.py
```

Then enter:
- Draft: `10.0`
- KG: `8.5`

**Command Line Mode**:
```bash
python3 loadicator.py --draft 10.0 --kg 8.5
```

**Save Outputs**:
```bash
python3 loadicator.py --draft 10.0 --kg 8.5 --save-plot gz_curve.png --save-pdf stability_report.pdf
```

## Example Test Cases

### Test Case 1: Light Ship
```bash
python3 loadicator.py --draft 2.01 --kg 7.0
```
Expected: Displacement ~10,553 tonnes

### Test Case 2: Loaded Condition
```bash
python3 loadicator.py --draft 10.0 --kg 8.5
```
Expected: Displacement ~58,171 tonnes, positive GM

### Test Case 3: Summer Draft
```bash
python3 loadicator.py --draft 13.02 --kg 9.0
```
Expected: Displacement ~77,165 tonnes (summer displacement)

## Understanding the Output

### Key Values to Check:

1. **GM (Metacentric Height)**: Should be > 0.15m
   - If negative: Vessel is unstable!
   - If < 0.15m: Does not meet IMO requirements

2. **Maximum GZ**: Typically 0.5m to 1.5m for cargo vessels
   - Higher is better for stability

3. **Angle at Max GZ**: Should be ≥ 25°
   - Indicates good stability range

4. **IMO Compliance**: All criteria should show "PASS"
   - If any show "FAIL", adjust loading condition

### GZ Curve Shape:

A good GZ curve should:
- Start at zero (0° heel)
- Rise steadily to a peak (typically 30-40°)
- Remain positive until high angles (60°+)
- Have adequate area under the curve

## Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"
**Solution**: Install packages with `pip3 install pandas numpy matplotlib scipy`

### "Draft outside valid range"
**Solution**: Use draft between 2.00m and 13.02m

### "Displacement outside valid range"
**Solution**: Check that your draft and KG values are realistic for the vessel

### Plot window doesn't appear
**Solution**: Use `--save-plot` to save to file instead of displaying

## For Port State Control Inspection

Generate a complete PDF report:

```bash
python3 loadicator.py --draft [YOUR_DRAFT] --kg [YOUR_KG] --save-pdf PSC_Stability_Report.pdf
```

The PDF will contain:
- GZ curve plot with vessel particulars
- IMO compliance summary
- All required stability parameters

## Need Help?

Run with `--help` to see all options:
```bash
python3 loadicator.py --help
```

---

**Remember**: This is an emergency backup tool. Always verify critical calculations when possible!
