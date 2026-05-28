# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Part_1** is a data visualization project analyzing The Simpsons episode ratings and viewership over time. It answers five core analytical questions:
1. How have ratings evolved over time?
2. How have viewers evolved over time?
3. Is there a correlation between ratings and viewership?
4. Are viewers related to the weekday episodes aired?
5. Do seasons show relevant viewership patterns?

The project structure follows a linear workflow: **Data Cleaning → Analysis & Design → Web Visualization**.

## Project Structure (Part_1)

```
Part_1/
├── simpsons_episodes.csv              # Raw dataset from Kaggle
├── simpsons_episodes_clean.csv        # Cleaned dataset (output of data cleaning)
├── Vendrix_Alexis_data_cleaning.py    # Data cleaning pipeline
├── Vendrix_Alexis.ipynb               # Analysis notebook: design process & chart implementation
├── Vendrix_Alexis_streamlit.py        # Streamlit dashboard (deployed at streamlit.io)
├── Part_1_Instruction.md              # Project requirements
├── images/                            # Dashboard screenshots and chart previews
└── 20260330_CV_Vendrix_Alexis.zip     # Deliverable archive
```

## Key Workflows

### 1. Data Cleaning Pipeline

The data cleaning script (`Vendrix_Alexis_data_cleaning.py`) processes raw Kaggle data:

```bash
cd Part_1/
python3 Vendrix_Alexis_data_cleaning.py
```

**What it does:**
- **Column cleanup**: Removes `image_url`, `video_url`, `production_code`
- **Date parsing**: Converts `original_air_date` to datetime; extracts year, month, weekday, week number
- **Missing value handling**:
  - Removes Season 28 (incomplete data)
  - Imputes Season 8 viewer counts using linear regression on `number_in_season`
- **Feature engineering**:
  - Calculates `trend_slope` per season (linear regression slope of viewers across episodes) to show if a season gained/lost viewers
  - Creates `viewers_type` column to distinguish measurement methodology shift: "Household Viewers" (Seasons ≤11, Nielsen rating pre-1998) vs "Individual Viewers" (Seasons >11, modern measurement)
- **Type standardization**: Ensures season and episode numbers are integers

Output: `simpsons_episodes_clean.csv`

### 2. Analysis & Chart Development

The Jupyter notebook (`Vendrix_Alexis.ipynb`) documents:
- Design decisions for each chart (why boxplot vs line, why scatter for correlation, etc.)
- Implementation of 5 core visualizations + 1 composite heatmap
- Custom Altair theme registration (global styling)
- Step-by-step design process with iterations

**To run locally:**
```bash
cd Part_1/
jupyter notebook Vendrix_Alexis.ipynb
```

Key insight: Charts use a consistent "Background/Foreground" color strategy:
- Blue (#009DDC, #39989f) for data points/boxes (background)
- Pink (#F14A9C) for trend lines/annotations (foreground accent)

### 3. Streamlit Dashboard

The Streamlit app (`Vendrix_Alexis_streamlit.py`) renders the final dashboard:

```bash
cd Part_1/
streamlit run Vendrix_Alexis_streamlit.py
```

The app loads `simpsons_episodes_clean.csv` and displays all 5 visualizations + metadata on a single page.

**Live deployment**: https://2026upcdatavisualisationsimpsons.streamlit.app/

## Important Design Details

### Custom Altair Theme
Registered in both the notebook and Streamlit app:
```python
@alt.theme.register("simpsons", enable=True)
def simpsons_theme():
    return alt.theme.ThemeConfig(
        range={"category": ["#009DDC", "#F05E23", "#F14A9C", "#D1B271", "#4C76B6"]},
        # ... axis, title, and background styling
    )
```
This theme applies globally to all charts, eliminating per-chart formatting.

### Custom Streamlit Theme
Configured in `.streamlit/config.toml`:
- **base**: "light" (prevents dark mode from overriding yellow sidebar)
- **primaryColor**: "#F14A9C" (donut pink)
- **backgroundColor**: "#FFFEF9" (off-white)
- **secondaryBackgroundColor**: "#FED41D" (Simpsons yellow)
- **textColor**: "#333333" (dark gray)

### Data Measurement Shift
The dataset spans before and after Nielsen changed from "Household Viewers" to "Individual Viewers" around Season 12 (late 1990s). The `viewers_type` column explicitly tracks this:
- Seasons ≤11: Household Viewers (millions of households)
- Seasons >11: Individual Viewers (millions of people)

Charts acknowledge this with color separation (two tints of teal) and grouped trendlines.

### Axis Scaling
- **Ratings chart**: Y-axis domain limited to [4, 10] (ratings rarely drop below 4) to amplify visual variation
- **Boxplots**: Show min-max extent, not IQR, to reveal full variance
- **Opacity**: Circle plots use opacity=0.8 to show overlapping point density

## File Interdependencies

```
simpsons_episodes.csv (input)
    ↓
Vendrix_Alexis_data_cleaning.py (run once)
    ↓
simpsons_episodes_clean.csv (output)
    ↓
├→ Vendrix_Alexis.ipynb (reads & develops charts)
└→ Vendrix_Alexis_streamlit.py (reads & displays)
```

Always run data cleaning first if raw data changes. Both the notebook and Streamlit app expect the cleaned CSV to exist.

## Python Environment

- **Python 3.13.3**
- **Key dependencies**: streamlit (1.55.0), altair (6.0.0), pandas (2.3.3), scikit-learn (1.8.0), numpy (2.4.3)
- **Virtual environment**: `.venv/` (activated automatically in most IDEs)

## Common Tasks

| Task | Command |
|------|---------|
| Clean raw data | `cd Part_1 && python3 Vendrix_Alexis_data_cleaning.py` |
| Open analysis notebook | `cd Part_1 && jupyter notebook Vendrix_Alexis.ipynb` |
| Run Streamlit app locally | `cd Part_1 && streamlit run Vendrix_Alexis_streamlit.py` |
| Check installed packages | `pip list \| grep -E "streamlit\|altair\|pandas"` |

## Notes for Future Work

- **Image paths**: All image references in the notebook use relative paths (`images/DV_*.png`). The `images/` folder is now in Part_1 to keep the project self-contained.
- **CSV filenames**: Both scripts expect exactly `simpsons_episodes.csv` (input) and `simpsons_episodes_clean.csv` (output). Renaming requires code changes.
- **Streamlit deployment**: Uses Streamlit Cloud; app references are hardcoded in the notebook markdown. Update if redeployed.
- **Altair deprecation warnings**: The code uses newer `@alt.theme.register()` syntax (5.5.0+). Ignore legacy warnings from `alt.themes.register()`.
