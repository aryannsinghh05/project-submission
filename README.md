# project-submission-readme

# IoT Based Smart Home Automation System: Exploratory Data Analysis

## Overview
This project performs exploratory data analysis (EDA) on an expanded smart-home sensor dataset. A single Python script reads the dataset and generates a PDF report and an Excel workbook of results.

## Dataset
- **File:** `data/Dataset_expanded.csv` (5,000 records, 8 columns)
- **Data dictionary:** `data/Data_dictionary.csv`
- **Columns:** `timestamp`, `device_id`, `sensor_type`, `room`, `temperature_C`, `humidity_pct`, `value`, `alert_flag`
- **Note:** The expanded dataset includes synthetic generated records, so patterns in it are illustrative and not real-world sensor measurements.

## What the script does
- Runs data-quality checks (row count, missing cells, duplicates, timestamp parsing, value ranges)
- Computes numeric, room-wise and sensor-wise summaries
- Counts alert flags and calculates daily temperature and humidity trends
- Creates four charts: temperature distribution, average humidity by room, daily average temperature, and alert flag counts
- Generates a PDF report and an Excel workbook with the summary tables, two embedded charts, and the full dataset

## Project structure
```
smart-home-eda/
├── README.md
├── generate_eda_report.py
├── data/
│   ├── Dataset_expanded.csv
│   └── Data_dictionary.csv
├── outputs/
│   ├── EDA_ANALYSIS_REPORT.pdf
│   └── EDA_Analysis_Results.xlsx
└── docs/
    ├── Project Report.docx
    ├── Project Synopsis.docx
    └── source-code-python.pdf
```

## Requirements
- Python 3.9 or later
- pandas, matplotlib, openpyxl, reportlab

```
pip install pandas matplotlib openpyxl reportlab
```

## How to run
1. Clone or download this repository.
2. Open a terminal in the project folder.
3. Install the requirements (see above).
4. Make sure `INPUT_CSV` in `generate_eda_report.py` points to `data/Dataset_expanded.csv`.
5. Run:

```
python generate_eda_report.py
```

The script creates `EDA_ANALYSIS_REPORT.pdf`, `EDA_Analysis_Results.xlsx` and a `figures/` folder of chart images in the folder where it is run.

## Outputs
| File | Description |
|------|-------------|
| `EDA_ANALYSIS_REPORT.pdf` | Report with quality checks, charts and interpretation |
| `EDA_Analysis_Results.xlsx` | Workbook with summary tables, charts and the full dataset |

## Limitations
The charts describe the dataset only. They do not establish physical sensor accuracy or prove that a hardware prototype is operating.

## Author
Akshita, B.Tech Electrical and Computer Engineering, ABES Engineering College, Ghaziabad
