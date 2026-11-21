import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import BarChart, LineChart, Reference
from openpyxl.utils import get_column_letter
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, KeepTogether

INPUT_CSV = "Dataset_expanded.csv"
OUTPUT_PDF = "EDA_ANALYSIS_REPORT.pdf"
OUTPUT_XLSX = "EDA_Analysis_Results.xlsx"
FIG_DIR = "figures"
HEADER_COLOR = "#5B2C83"

os.makedirs(FIG_DIR, exist_ok=True)

df = pd.read_csv(INPUT_CSV)
df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
timestamp_failures = int(df["timestamp"].isna().sum())

quality = pd.Series(
    {
        "Rows": float(len(df)),
        "Columns": float(df.shape[1]),
        "Missing cells": float(df.isna().sum().sum()),
        "Duplicate rows": float(df.duplicated().sum()),
        "Timestamp parse failures": float(timestamp_failures),
        "Temperature min (°C)": float(df["temperature_C"].min()),
        "Temperature max (°C)": float(df["temperature_C"].max()),
        "Humidity min (%)": float(df["humidity_pct"].min()),
        "Humidity max (%)": float(df["humidity_pct"].max()),
    }
)
quality_df = quality.reset_index()
quality_df.columns = ["Check", "Result"]

numeric_summary = df[["temperature_C", "humidity_pct", "value", "alert_flag"]].describe().T.reset_index()
numeric_summary = numeric_summary.rename(columns={"index": "column"})

room_summary = (
    df.groupby("room")
    .agg(
        records=("room", "size"),
        avg_temperature_C=("temperature_C", "mean"),
        avg_humidity_pct=("humidity_pct", "mean"),
        avg_value=("value", "mean"),
        alerts=("alert_flag", "sum"),
    )
    .round(2)
    .reset_index()
)

sensor_summary = (
    df.groupby("sensor_type")
    .agg(
        records=("sensor_type", "size"),
        avg_temperature_C=("temperature_C", "mean"),
        avg_humidity_pct=("humidity_pct", "mean"),
        avg_value=("value", "mean"),
        alerts=("alert_flag", "sum"),
    )
    .round(2)
    .reset_index()
)

alert_counts = df["alert_flag"].value_counts().sort_index().reset_index()
alert_counts.columns = ["alert_flag", "records"]

daily = (
    df.set_index("timestamp")
    .resample("D")
    .agg(avg_temperature_C=("temperature_C", "mean"), avg_humidity_pct=("humidity_pct", "mean"), records=("temperature_C", "size"))
    .round(2)
    .reset_index()
)
daily["timestamp"] = daily["timestamp"].dt.date
daily = daily.rename(columns={"timestamp": "date"})

fig1 = os.path.join(FIG_DIR, "fig1_temperature_distribution.png")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(df["temperature_C"], bins=20, edgecolor="black")
ax.set_title("Temperature Distribution")
ax.set_xlabel("Temperature (°C)")
ax.set_ylabel("Frequency")
fig.tight_layout()
fig.savefig(fig1, dpi=150)
plt.close(fig)

fig2 = os.path.join(FIG_DIR, "fig2_humidity_by_room.png")
room_humidity = df.groupby("room")["humidity_pct"].mean()
fig, ax = plt.subplots(figsize=(8, 3.6))
room_humidity.plot(kind="bar", ax=ax, edgecolor="black")
ax.set_title("Average Humidity by Room")
ax.set_xlabel("Room")
ax.set_ylabel("Humidity (%)")
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
fig.tight_layout()
fig.savefig(fig2, dpi=150)
plt.close(fig)

fig3 = os.path.join(FIG_DIR, "fig3_daily_temperature.png")
daily_plot = df.set_index("timestamp")["temperature_C"].resample("D").mean()
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.plot(daily_plot.index, daily_plot.values, marker="o")
ax.set_title("Daily Average Temperature")
ax.set_xlabel("Date")
ax.set_ylabel("Temperature (°C)")
fig.tight_layout()
fig.savefig(fig3, dpi=150)
plt.close(fig)

fig4 = os.path.join(FIG_DIR, "fig4_alert_counts.png")
alert_plot = df["alert_flag"].value_counts().sort_index()
fig, ax = plt.subplots(figsize=(8, 4.2))
alert_plot.plot(kind="bar", ax=ax, edgecolor="black")
ax.set_title("Alert Flag Counts")
ax.set_xlabel("Alert Flag")
ax.set_ylabel("Records")
plt.setp(ax.get_xticklabels(), rotation=0)
fig.tight_layout()
fig.savefig(fig4, dpi=150)
plt.close(fig)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=20, spaceAfter=14)
subtitle_style = ParagraphStyle("ReportSubtitle", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=13, spaceAfter=10)
h1_style = ParagraphStyle("H1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=18, spaceBefore=12, spaceAfter=8)
body_style = ParagraphStyle("Body", parent=styles["BodyText"], fontName="Helvetica", fontSize=10, leading=13)
caption_style = ParagraphStyle("Caption", parent=body_style, fontSize=8, spaceBefore=4, spaceAfter=12)

def scaled_image(path, width_mm):
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(path).getSize()
    width = width_mm * mm
    return Image(path, width=width, height=width * ih / iw)

table_rows = [["Check", "Result"]] + [[row.Check, str(row.Result)] for row in quality_df.itertuples()]
check_table = Table(table_rows, colWidths=[75 * mm, 75 * mm], hAlign="CENTER")
check_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(HEADER_COLOR)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]
    )
)

story = [
    Paragraph("Exploratory Data Analysis (EDA) Report", title_style),
    Paragraph("IoT Based Smart Home Automation System | Embedded IoT", subtitle_style),
    Paragraph("1. Purpose", h1_style),
    Paragraph(
        "This upload-friendly report summarises exploratory analysis of the expanded smart-home sensor dataset. "
        "The accompanying Excel workbook contains detailed tables and the full dataset.",
        body_style,
    ),
    Paragraph("2. Dataset overview and quality checks", h1_style),
    check_table,
    Paragraph("3. Visualisations", h1_style),
    KeepTogether([scaled_image(fig1, 150), Paragraph("Figure 1. Distribution of temperature readings.", caption_style)]),
    KeepTogether([scaled_image(fig2, 150), Paragraph("Figure 2. Average humidity by room.", caption_style)]),
    KeepTogether([scaled_image(fig3, 150), Paragraph("Figure 3. Daily average temperature trend.", caption_style)]),
    KeepTogether([scaled_image(fig4, 150), Paragraph("Figure 4. Counts for each alert flag value.", caption_style)]),
    Paragraph("4. Interpretation", h1_style),
    Paragraph(
        "The temperature distribution shows the spread of recorded values. The room comparison helps inspect humidity "
        "differences. The daily trend illustrates changes over time, and alert counts summarise the alert labels. "
        "These charts describe the dataset; they do not establish physical sensor accuracy or prove that a prototype is operating.",
        body_style,
    ),
    Paragraph("5. Reproducibility and limitations", h1_style),
    Paragraph(
        "The expanded dataset includes synthetic generated records. Treat patterns in generated records as illustrative, "
        "not real-world measurements. Original source records were retained, so any original values outside requested "
        "ranges may remain unchanged. Confirm prototype status and results before submission.",
        body_style,
    ),
    Paragraph("6. Related deliverable", h1_style),
    Paragraph(
        "EDA_Analysis_Results.xlsx contains data-quality checks, numeric summaries, room summaries, alert counts, "
        "daily trends, two embedded Excel charts, and the full dataset.",
        body_style,
    ),
]

doc = SimpleDocTemplate(
    OUTPUT_PDF,
    pagesize=A4,
    leftMargin=20 * mm,
    rightMargin=20 * mm,
    topMargin=20 * mm,
    bottomMargin=20 * mm,
    title="Exploratory Data Analysis (EDA) Report",
)
doc.build(story)

wb = Workbook()
header_font = Font(name="Arial", bold=True, color="FFFFFF")
header_fill = PatternFill("solid", fgColor=HEADER_COLOR.lstrip("#"))
body_font = Font(name="Arial")
thin = Side(style="thin", color="BFBFBF")
border = Border(left=thin, right=thin, top=thin, bottom=thin)

def write_frame(ws, frame, start_row=1, start_col=1):
    for j, col in enumerate(frame.columns, start=start_col):
        cell = ws.cell(row=start_row, column=j, value=str(col))
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = border
    for i, row in enumerate(frame.itertuples(index=False), start=start_row + 1):
        for j, value in enumerate(row, start=start_col):
            if hasattr(value, "item"):
                value = value.item()
            cell = ws.cell(row=i, column=j, value=value)
            cell.font = body_font
            cell.border = border
    for j, col in enumerate(frame.columns, start=start_col):
        values = [str(col)] + [str(v) for v in frame.iloc[:, j - start_col].head(200)]
        ws.column_dimensions[get_column_letter(j)].width = min(max(len(v) for v in values) + 3, 45)
    ws.freeze_panes = ws.cell(row=start_row + 1, column=start_col)

ws = wb.active
ws.title = "Data_Quality"
write_frame(ws, quality_df)

ws = wb.create_sheet("Numeric_Summary")
write_frame(ws, numeric_summary.round(4))

ws = wb.create_sheet("Room_Summary")
write_frame(ws, room_summary)
chart_room = BarChart()
chart_room.type = "col"
chart_room.title = "Average Humidity by Room"
chart_room.y_axis.title = "Humidity (%)"
chart_room.x_axis.title = "Room"
chart_room.add_data(Reference(ws, min_col=3 + 0, min_row=1, max_row=len(room_summary) + 1), titles_from_data=True)
chart_room.set_categories(Reference(ws, min_col=1, min_row=2, max_row=len(room_summary) + 1))
chart_room.legend = None
chart_room.roundedCorners = False
chart_room.x_axis.delete = False
chart_room.y_axis.delete = False
chart_room.height = 8
chart_room.width = 16
ws.add_chart(chart_room, "H2")

ws = wb.create_sheet("Sensor_Summary")
write_frame(ws, sensor_summary)

ws = wb.create_sheet("Alert_Counts")
write_frame(ws, alert_counts)

ws = wb.create_sheet("Daily_Trend")
write_frame(ws, daily)
for r in range(2, len(daily) + 2):
    ws.cell(row=r, column=1).number_format = "yyyy-mm-dd"
chart_daily = LineChart()
chart_daily.title = "Daily Average Temperature"
chart_daily.y_axis.title = "Temperature (°C)"
chart_daily.x_axis.title = "Date"
chart_daily.add_data(Reference(ws, min_col=2, min_row=1, max_row=len(daily) + 1), titles_from_data=True)
chart_daily.set_categories(Reference(ws, min_col=1, min_row=2, max_row=len(daily) + 1))
chart_daily.legend = None
chart_daily.roundedCorners = False
chart_daily.x_axis.delete = False
chart_daily.y_axis.delete = False
chart_daily.x_axis.number_format = "yyyy-mm-dd"
chart_daily.x_axis.tickLblSkip = 14
chart_daily.height = 8
chart_daily.width = 20
ws.add_chart(chart_daily, "G2")

ws = wb.create_sheet("Full_Dataset")
full = df.copy()
full["timestamp"] = full["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
write_frame(ws, full)

wb.save(OUTPUT_XLSX)
