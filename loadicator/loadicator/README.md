# MV Del Monte - Loadicator

A Python-based stability calculator and GZ curve generator for the MV Del Monte, designed to verify vessel stability when the approved loading computer has failed.

## Features

- **GZ Curve Generation**: Calculate and plot complete GZ curves from 0° to 90° heel angles
- **Hydrostatic Calculations**: Interpolate displacement, KB, KM, GM from draft
- **IMO Compliance Checking**: Automatic verification against IMO Intact Stability Code requirements
- **Professional Reports**: Generate detailed text reports and PDF outputs
- **Visualization**: High-quality GZ curve plots with compliance indicators
- **Interactive & CLI Modes**: Use interactively or via command-line arguments

## Requirements

- Python 3.7 or higher
- pandas >= 1.3.0
- numpy >= 1.21.0
- matplotlib >= 3.4.0
- scipy >= 1.7.0

## Installation

1. Clone or download this repository
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Data Files Required

The following CSV files must be in the same directory as the scripts:

- `Hydrostatic Data.csv` - Vessel hydrostatic properties
- `KN Curves.csv` - Cross curves of stability

## Usage

### Interactive Mode (Recommended)

Simply run the loadicator without arguments:

```bash
python loadicator.py
```

You'll be prompted to enter:
- Draft at perpendiculars (m)
- KG - Vertical Center of Gravity (m)
- Output options (report, plot, PDF)

### Command-Line Mode

Calculate stability for specific values:

```bash
python loadicator.py --draft 10.0 --kg 8.5
```

Save outputs:

```bash
python loadicator.py --draft 10.0 --kg 8.5 --save-plot gz_curve.png --save-pdf report.pdf
```

Specify custom data directory:

```bash
python loadicator.py --data-dir /path/to/data --draft 10.0 --kg 8.5
```

### Command-Line Options

```
--draft DRAFT         Draft at perpendiculars (m)
--kg KG              Vertical center of gravity KG (m)
--data-dir DIR       Directory containing CSV data files
--save-plot FILE     Save GZ curve plot to file
--save-pdf FILE      Save complete PDF report to file
--interactive, -i    Run in interactive mode
--version            Show version information
```

## Input Parameters

### Draft at Perpendiculars
- **Range**: 2.00m to 13.02m
- **Description**: Mean draft of the vessel at the perpendiculars
- **Units**: Meters

### KG (Vertical Center of Gravity)
- **Range**: Must be positive, typically 1.0m to 15.0m
- **Description**: Height of the vessel's center of gravity above the keel
- **Units**: Meters

## Output

### Text Report

The loadicator generates a comprehensive text report including:

- **Input Data**: Draft, KG, calculation timestamp
- **Calculated Values**: Displacement, KB, KM, GM
- **Stability Parameters**: Maximum GZ, angle at max GZ, vanishing angle
- **GZ Curve Data**: Complete table of heel angles and GZ values
- **IMO Compliance Check**: Pass/fail status for all criteria

### GZ Curve Plot

Professional plot showing:
- GZ curve from 0° to 90°
- Maximum GZ point marked
- Vanishing angle indicated
- Shaded areas for IMO criteria (0-30°, 30-40°)
- Compliance status indicator
- Vessel particulars in title

### PDF Report

Multi-page PDF containing:
- Page 1: GZ curve plot
- Page 2: IMO compliance summary chart
- Metadata with vessel name and calculation details

## IMO Intact Stability Code Criteria

The loadicator automatically checks compliance with:

1. **GM ≥ 0.15 m** - Minimum metacentric height
2. **Area 0-30° ≥ 0.055 m·rad** - Area under GZ curve from 0° to 30°
3. **Area 0-40° ≥ 0.090 m·rad** - Area under GZ curve from 0° to 40°
4. **Area 30-40° ≥ 0.030 m·rad** - Area under GZ curve from 30° to 40°
5. **GZ at 30° ≥ 0.20 m** - Minimum GZ value at 30° heel
6. **Angle of max GZ ≥ 25°** - Maximum GZ must occur at or beyond 25°

## Example Calculations

### Light Ship Condition
```bash
python loadicator.py --draft 2.01 --kg 7.0
```

### Loaded Condition
```bash
python loadicator.py --draft 10.0 --kg 8.5
```

### Summer Draft Departure
```bash
python loadicator.py --draft 13.02 --kg 9.0 --save-pdf departure_stability.pdf
```

## Module Structure

The loadicator consists of five main modules:

### `data_loader.py`
- Loads and parses CSV data files
- Validates data integrity
- Provides data range information

### `interpolation.py`
- Linear interpolation for hydrostatic properties
- 2D interpolation for KN curves
- GZ curve calculation engine

### `calculator.py`
- Complete stability calculations
- IMO compliance checking
- Report generation

### `visualizer.py`
- GZ curve plotting
- Compliance summary charts
- PDF export functionality

### `loadicator.py`
- Main application interface
- Command-line argument parsing
- Interactive mode handler

## Testing Individual Modules

Each module can be tested independently:

```bash
# Test data loader
python data_loader.py

# Test interpolation
python interpolation.py

# Test calculator
python calculator.py

# Test visualizer
python visualizer.py
```

## Troubleshooting

### "Hydrostatic data not loaded"
- Ensure `Hydrostatic Data.csv` is in the correct directory
- Check file name spelling and capitalization
- Use `--data-dir` to specify custom location

### "Draft outside valid range"
- Valid range: 2.00m to 13.02m
- Check that draft is within vessel's design limits

### "Displacement outside valid range"
- This may occur with extreme draft/KG combinations
- Verify input values are realistic for the vessel

### Import errors
- Install all required packages: `pip install -r requirements.txt`
- Ensure Python version is 3.7 or higher

## Validation

The loadicator has been validated against:
- Manual calculations using tabulated data
- Known vessel stability characteristics
- IMO stability code requirements

**Note**: While this loadicator provides accurate calculations based on the vessel's stability data, it should be used as a backup tool. Always verify critical stability calculations with multiple methods when possible.

## Limitations

- Does not account for free surface effects
- Does not include trim corrections
- Does not calculate wind heeling moments
- Does not include grain heeling moments
- Assumes even keel condition

## Future Enhancements

Planned features for future versions:
- Free surface effect corrections
- Trim calculation and correction
- Wind heeling moment calculations
- Grain heeling moment calculations
- Loading condition management
- Web-based interface

## License

This software is provided for maritime safety purposes. Use at your own risk and always verify critical calculations.

## Support

For issues or questions, please refer to the documentation or contact the development team.

---

**Version**: 1.0  
**Last Updated**: January 2026  
**Vessel**: MV Del Monte  
**Purpose**: Emergency stability verification during loading computer failure

---

## Quick Start Guide

1. **Install Python packages**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run interactive mode**:
   ```bash
   python loadicator.py
   ```

3. **Enter your values**:
   - Draft: e.g., 10.0
   - KG: e.g., 8.5

4. **Review results**:
   - Check GM value (should be > 0.15m)
   - Verify IMO compliance status
   - Review GZ curve shape

5. **Save outputs** (optional):
   - Choose option to save plot and/or PDF
   - Files saved in current directory

**That's it!** You now have a verified GZ curve for Port State Control inspection.
