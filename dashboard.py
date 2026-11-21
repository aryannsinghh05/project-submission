import os
import json
from pathlib import Path
from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Smart Home IoT Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

INDIGO = "#4f46e5"
SKY = "#0ea5e9"
TEAL = "#14b8a6"
AMBER = "#f59e0b"
RED = "#ef4444"
INK = "#0f172a"

st.markdown(f"""
<style>
    .stApp {{background: linear-gradient(180deg, #eef2ff 0%, #f8fafc 340px);}}
    .block-container {{padding-top: 1.2rem; padding-bottom: 2.5rem; max-width: 1280px;}}
    footer {{visibility: hidden;}}
    [data-testid="stSidebar"] {{background: #ffffff; border-right: 1px solid #e2e8f0;}}
    .hero {{
        background: linear-gradient(120deg, {INDIGO} 0%, {SKY} 62%, {TEAL} 100%);
        border-radius: 20px; padding: 28px 34px; margin-bottom: 18px;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.25);
    }}
    .hero h1 {{color: #ffffff !important; margin: 0; font-size: 2.1rem; padding: 0;}}
    .hero p {{color: #e0f2fe !important; margin: 6px 0 14px 0; font-size: 1rem;}}
    .badge {{
        display: inline-block; background: rgba(255,255,255,0.18); color: #ffffff;
        padding: 5px 13px; border-radius: 999px; font-size: 0.82rem; margin-right: 8px;
        border: 1px solid rgba(255,255,255,0.3);
    }}
    .kpi-grid {{display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin: 6px 0 18px 0;}}
    @media (max-width: 960px) {{.kpi-grid {{grid-template-columns: repeat(2, 1fr);}}}}
    .kpi {{
        background: #ffffff; border-radius: 16px; padding: 16px 18px;
        border-left: 6px solid var(--c); box-shadow: 0 4px 16px rgba(15, 23, 42, 0.07);
    }}
    .kpi .label {{color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.04em;}}
    .kpi .value {{color: {INK}; font-size: 1.9rem; font-weight: 700; margin-top: 4px;}}
    .section-title {{color: {INK}; font-size: 1.05rem; font-weight: 700; margin: 2px 0 8px 2px;}}
    div[data-testid="stVerticalBlockBorderWrapper"] {{border-radius: 16px;}}
    .stTabs [data-baseweb="tab-list"] {{gap: 8px; border-bottom: none;}}
    .stTabs [data-baseweb="tab"] {{
        background: #ffffff; border-radius: 999px; padding: 8px 20px;
        border: 1px solid #e2e8f0; height: auto;
    }}
    .stTabs [aria-selected="true"] {{background: {INDIGO}; color: #ffffff;}}
    .stTabs [aria-selected="true"] p {{color: #ffffff;}}
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{display: none;}}
    .small-note {{color: #64748b; font-size: 0.88rem;}}
    div[data-testid="stAlert"] {{border-radius: 12px;}}
</style>
""", unsafe_allow_html=True)

EXPECTED = [
    "timestamp", "device_id", "sensor_type", "room",
    "temperature_C", "humidity_pct", "value", "alert_flag"
]
BASE_DIR = Path(__file__).parent
DEFAULT_FILE = BASE_DIR / "Dataset expanded.csv"
if not DEFAULT_FILE.exists():
    for candidate in sorted(BASE_DIR.glob("*.csv")):
        name = candidate.name.lower()
        if "dataset" in name and "dictionary" not in name:
            DEFAULT_FILE = candidate
            break

@st.cache_data
def read_csv(file_obj_or_path):
    return pd.read_csv(file_obj_or_path)

def normalize_data(raw):
    missing = [c for c in EXPECTED if c not in raw.columns]
    if missing:
        raise ValueError("Dataset is missing required columns: " + ", ".join(missing))
    df = raw[EXPECTED].copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    for col in ["temperature_C", "humidity_pct", "value", "alert_flag"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["alert_flag"] = df["alert_flag"].fillna(0).astype(int)
    df["room"] = df["room"].fillna("Unknown").astype(str)
    df["device_id"] = df["device_id"].fillna("Unknown").astype(str)
    df["sensor_type"] = df["sensor_type"].fillna("Unknown").astype(str)
    df = df.dropna(subset=["timestamp"])
    return df.sort_values("timestamp")

def style(fig, x_title=None, y_title=None, height=340):
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK),
        margin=dict(l=8, r=8, t=10, b=8),
        height=height,
    )
    if x_title is not None:
        fig.update_layout(xaxis_title=x_title, yaxis_title=y_title)
        fig.update_xaxes(gridcolor="#eef2f7")
        fig.update_yaxes(gridcolor="#eef2f7")
    return fig

def card(title):
    box = st.container(border=True)
    box.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    return box

with st.sidebar:
    st.header("Dashboard controls")
    uploaded = st.file_uploader("Upload sensor dataset (CSV)", type=["csv"])
    st.caption("Expected schema: the eight columns in your project data dictionary.")
    if uploaded is not None:
        raw = read_csv(uploaded)
        source_label = uploaded.name
    elif DEFAULT_FILE.exists():
        raw = read_csv(str(DEFAULT_FILE))
        source_label = DEFAULT_FILE.name
    else:
        raw = None
        source_label = "No dataset loaded"

if raw is None:
    st.title("🏠 Smart Home IoT Monitoring")
    st.warning("Upload Dataset expanded.csv from the sidebar to begin.")
    st.stop()

try:
    data = normalize_data(raw)
except Exception as exc:
    st.error(str(exc))
    st.stop()

min_date = data["timestamp"].min().date()
max_date = data["timestamp"].max().date()

st.markdown(f"""
<div class="hero">
    <h1>🏠 Smart Home IoT Monitoring</h1>
    <p>IoT Based Smart Home Automation System | Embedded IoT</p>
    <span class="badge">📄 {source_label}</span>
    <span class="badge">🗓️ {min_date:%d %b %Y} – {max_date:%d %b %Y}</span>
    <span class="badge">📊 {len(data):,} records loaded</span>
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("<div class='section-title'>🔎 Filters</div>", unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns([1.3, 1.3, 1.3, 1])
    rooms = sorted(data["room"].dropna().unique().tolist())
    sensors = sorted(data["sensor_type"].dropna().unique().tolist())
    devices = sorted(data["device_id"].dropna().unique().tolist())
    selected_rooms = f1.multiselect("Room", rooms, default=rooms)
    selected_sensors = f2.multiselect("Sensor type", sensors, default=sensors)
    selected_devices = f3.multiselect("Device ID", devices, default=devices)
    date_range = f4.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.info("Select both a start date and an end date in the filter bar.")
    st.stop()

start_date, end_date = date_range
mask = (
    data["room"].isin(selected_rooms)
    & data["sensor_type"].isin(selected_sensors)
    & data["device_id"].isin(selected_devices)
    & (data["timestamp"].dt.date >= start_date)
    & (data["timestamp"].dt.date <= end_date)
)
fdf = data[mask]

if fdf.empty:
    st.warning("No records match the selected filters. Adjust the filters above.")
    st.stop()

alerts = int(fdf["alert_flag"].sum())
kpis = [
    ("Records", f"{len(fdf):,}", INDIGO),
    ("Avg temperature (°C)", f"{fdf['temperature_C'].mean():.1f}", AMBER),
    ("Avg humidity (%)", f"{fdf['humidity_pct'].mean():.1f}", SKY),
    ("Alerts", f"{alerts:,}", RED),
    ("Alert rate", f"{alerts / len(fdf) * 100:.2f}%", TEAL),
]
cards_html = "".join(
    f"<div class='kpi' style='--c:{c}'><div class='label'>{l}</div><div class='value'>{v}</div></div>"
    for l, v, c in kpis
)
st.markdown(f"<div class='kpi-grid'>{cards_html}</div>", unsafe_allow_html=True)

tab_overview, tab_alerts, tab_data = st.tabs(["📈 Overview", "🚨 Alerts", "🗂️ Data"])

with tab_overview:
    left, right = st.columns([2, 1])
    with left:
        with card("Temperature distribution"):
            fig = px.histogram(fdf, x="temperature_C", nbins=20, color_discrete_sequence=[INDIGO])
            fig.update_traces(marker_line_color="white", marker_line_width=1)
            st.plotly_chart(style(fig, "Temperature (°C)", "Frequency"))
    with right:
        with card("Alert flag counts"):
            counts = fdf["alert_flag"].value_counts().sort_index().reset_index()
            counts.columns = ["alert_flag", "records"]
            counts["label"] = counts["alert_flag"].map({0: "0 (no alert)", 1: "1 (alert)"})
            fig = px.pie(counts, names="label", values="records", hole=0.55,
                         color="label",
                         color_discrete_map={"0 (no alert)": INDIGO, "1 (alert)": RED})
            fig.update_traces(textinfo="value+percent")
            fig.update_layout(legend=dict(orientation="h", y=-0.05))
            st.plotly_chart(style(fig))

    left, right = st.columns([1, 2])
    with left:
        with card("Average humidity by room"):
            room_hum = fdf.groupby("room", as_index=False)["humidity_pct"].mean().round(2)
            fig = px.bar(room_hum, y="room", x="humidity_pct", orientation="h", text="humidity_pct",
                         color="room",
                         color_discrete_sequence=[SKY, TEAL, INDIGO, AMBER, "#8b5cf6", "#ec4899"])
            fig.update_traces(textposition="outside")
            fig.update_layout(showlegend=False)
            st.plotly_chart(style(fig, "Humidity (%)", "Room"))
    with right:
        with card("Daily average temperature"):
            daily = fdf.set_index("timestamp")["temperature_C"].resample("D").mean().dropna().reset_index()
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=daily["timestamp"], y=daily["temperature_C"].round(2),
                mode="lines+markers", name="Temperature (°C)",
                line=dict(color=TEAL, width=2.5), marker=dict(size=5),
                fill="tozeroy", fillcolor="rgba(20, 184, 166, 0.12)",
            ))
            fig.update_yaxes(rangemode="normal")
            st.plotly_chart(style(fig, "Date", "Temperature (°C)"))

with tab_alerts:
    alert_df = fdf[fdf["alert_flag"] == 1]
    if alert_df.empty:
        st.info("No alerts in the current selection.")
    else:
        left, right = st.columns(2)
        with left:
            with card("Alerts by sensor type"):
                by_sensor = alert_df.groupby("sensor_type", as_index=False).size().rename(columns={"size": "alerts"})
                fig = px.bar(by_sensor, x="sensor_type", y="alerts", text="alerts", color_discrete_sequence=[RED])
                fig.update_traces(textposition="outside")
                st.plotly_chart(style(fig, "Sensor type", "Alerts"))
        with right:
            with card("Alerts by room"):
                by_room = alert_df.groupby("room", as_index=False).size().rename(columns={"size": "alerts"})
                fig = px.bar(by_room, x="room", y="alerts", text="alerts", color_discrete_sequence=[AMBER])
                fig.update_traces(textposition="outside")
                st.plotly_chart(style(fig, "Room", "Alerts"))
        with card("Most recent alerts"):
            st.dataframe(alert_df.sort_values("timestamp", ascending=False).head(25), hide_index=True)

with tab_data:
    with card("Filtered dataset"):
        st.dataframe(fdf, hide_index=True)
        st.download_button(
            "⬇️ Download filtered data (CSV)",
            fdf.to_csv(index=False).encode("utf-8"),
            file_name="filtered_smart_home_data.csv",
            mime="text/csv",
        )

st.markdown(
    "<span class='small-note'>The expanded dataset includes synthetic generated records. Charts describe the "
    "dataset only and do not establish physical sensor accuracy or prove that a prototype is operating.</span>",
    unsafe_allow_html=True,
)
