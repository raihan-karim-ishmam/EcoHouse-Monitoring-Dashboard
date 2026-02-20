import os
from datetime import datetime
from typing import Optional, List, Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

# Optional auto-refresh (nicer than manual reruns)
try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


CSV_PATH_DEFAULT = "data/live_data.csv"


def load_data(csv_path: str) -> pd.DataFrame:
    """Load the CSV and parse timestamp into UTC-aware datetime."""
    if not os.path.exists(csv_path):
        return pd.DataFrame(columns=["timestamp", "temperature_c", "power_w"])

    df = pd.read_csv(csv_path)
    if df.empty:
        return df

    # Make timestamp timezone-aware in UTC (important for freshness checks)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce", utc=True)
    df = df.dropna(subset=["timestamp"]).sort_values("timestamp")
    return df


def compute_insights(df: pd.DataFrame) -> List[Tuple[str, str, str]]:
    """
    Returns a list of insights as tuples:
      (text, level, icon)

    level can be: "ok", "info", "warn"
    """
    if len(df) < 3:
        return [("Waiting for more data points...", "info", "⏳")]

    # =========================================================
    # INSIGHT THRESHOLDS (EDIT THESE VALUES EASILY)
    # =========================================================
    TEMP_HIGH_C = 38      # If temperature >= this -> "High temperature"
    TEMP_LOW_C = 16       # If temperature <= this -> "Low temperature"

    POWER_HIGH_W = 2500   # If power >= this -> "High power usage"
    POWER_LOW_W = 150     # If power <= this -> "Very low power usage"

    SPIKE_W = 400         # Change sensitivity for spike/drop detection
    STALE_SECONDS = 30    # If latest reading older than this -> "Data delay"
    # =========================================================

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    temp = float(latest["temperature_c"])
    power = float(latest["power_w"])

    insights: List[Tuple[str, str, str]] = []

    # Temperature insights
    if temp >= TEMP_HIGH_C:
        insights.append((f"High temperature detected: {temp:.1f}°C", "warn", "🌡️"))
    elif temp <= TEMP_LOW_C:
        insights.append((f"Low temperature detected: {temp:.1f}°C", "warn", "🥶"))
    else:
        insights.append((f"Temperature normal: {temp:.1f}°C", "ok", "✅"))

    # Power insights
    if power >= POWER_HIGH_W:
        insights.append((f"High power usage: {power:.0f} W", "warn", "⚡"))
    elif power <= POWER_LOW_W:
        insights.append((f"Very low power usage: {power:.0f} W", "info", "🌙"))
    else:
        insights.append((f"Power stable: {power:.0f} W", "ok", "🔌"))

    # Spike/drop detection
    power_delta = power - float(prev["power_w"])
    if power_delta > SPIKE_W:
        insights.append((f"Load spike detected: +{power_delta:.0f} W since last update", "warn", "📈"))
    elif power_delta < -SPIKE_W:
        insights.append((f"Load drop detected: {power_delta:.0f} W since last update", "info", "📉"))

    # Live feed health (freshness)
    # This is what "Live feed healthy" means:
    # - If the timestamp of the latest row is recent (within STALE_SECONDS), data is flowing.
    # - If not, your generator/sensor feed might be stopped or delayed.
    now_utc = pd.Timestamp.now(tz="UTC")
    age_sec = (now_utc - latest["timestamp"]).total_seconds()

    if age_sec > STALE_SECONDS:
        insights.append((f"Data delay: last update {int(age_sec)}s ago", "warn", "🟠"))
    else:
        insights.append(("Live feed healthy", "ok", "🟢"))

    return insights


def kpi_card(label: str, value: str, delta: Optional[str] = None) -> None:
    """A nicer looking KPI card using lightweight HTML/CSS."""
    st.markdown(
        f"""
        <div style="
            padding: 14px 16px;
            border-radius: 16px;
            background: rgba(255,255,255,0.06);
            border: 1px solid rgba(255,255,255,0.10);
        ">
          <div style="font-size: 13px; opacity: 0.75;">{label}</div>
          <div style="font-size: 26px; font-weight: 700; margin-top: 6px;">{value}</div>
          <div style="font-size: 12px; opacity: 0.70; margin-top: 2px;">
            {delta if delta else ""}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_pill(text: str, level: str, icon: str) -> None:
    """
    Render one insight as an oval pill with a bigger icon.
    level: ok / info / warn
    """
    # Slight styling difference by level (without hardcoding loud colors)
    # We keep it subtle and readable.
    border_opacity = "0.14"
    bg_opacity = "0.06"
    if level == "warn":
        border_opacity = "0.22"
        bg_opacity = "0.08"

    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:12px;
            padding:12px 14px;
            border-radius:999px;
            border:1px solid rgba(255,255,255,{border_opacity});
            background: rgba(255,255,255,{bg_opacity});
            margin-bottom:10px;
        ">
          <div style="font-size:24px; line-height:1;">{icon}</div>
          <div style="font-size:14px; font-weight:650;">{text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="EcoHouse Monitoring Dashboard",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        .block-container { padding-top: 1.2rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🏡 EcoHouse Monitoring Dashboard")
    st.caption("Live demo using simulated real-time data (CSV append).")

    # Sidebar controls
    with st.sidebar:
        st.header("Settings")
        csv_path = st.text_input("CSV path", CSV_PATH_DEFAULT)

        window_points = st.slider(
            "Show last N points",
            min_value=20,
            max_value=400,
            value=120,
            step=10,
        )

        refresh_ms = st.slider(
            "Refresh interval (ms)",
            min_value=500,
            max_value=10000,
            value=1500,
            step=250,
        )

        st.divider()
        st.write("Run generator in another terminal:")
        st.code("python datagen.py --interval 1", language="bash")

    # Auto-refresh the page
    if st_autorefresh is not None:
        st_autorefresh(interval=refresh_ms, key="eco_refresh")
    else:
        st.info("Optional: pip install streamlit-autorefresh for smoother auto-refresh.")

    # Load data
    df = load_data(csv_path)
    if df.empty:
        st.warning("No data found yet. Start the data generator or check the CSV path.")
        return

    # View window (recent slice)
    df_view = df.tail(window_points).copy()

    latest = df_view.iloc[-1]
    prev = df_view.iloc[-2] if len(df_view) > 1 else latest

    temp = float(latest["temperature_c"])
    power = float(latest["power_w"])
    temp_delta = temp - float(prev["temperature_c"])
    power_delta = power - float(prev["power_w"])

    # KPI row
    col1, col2, col3, col4 = st.columns(4, gap="large")

    with col1:
        kpi_card("Temperature", f"{temp:.1f} °C", f"Δ {temp_delta:+.2f} °C vs last")
    with col2:
        kpi_card("Power", f"{power:.0f} W", f"Δ {power_delta:+.0f} W vs last")
    with col3:
        avg_power = df_view["power_w"].tail(10).mean()
        kpi_card("Avg Power (10)", f"{avg_power:.0f} W", "Rolling mean")
    with col4:
        ts = latest["timestamp"].to_pydatetime()
        kpi_card("Last Update (UTC)", ts.strftime("%H:%M:%S"), ts.strftime("%Y-%m-%d"))

    st.divider()

    left, right = st.columns([2.2, 1], gap="large")

    # Charts (left)
    with left:
        st.subheader("Live Trends")

        fig_power = px.line(df_view, x="timestamp", y="power_w", title="Power (W)")
        fig_power.update_layout(height=320, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_power, use_container_width=True)

        fig_temp = px.line(df_view, x="timestamp", y="temperature_c", title="Temperature (°C)")
        fig_temp.update_layout(height=320, margin=dict(l=10, r=10, t=50, b=10))
        st.plotly_chart(fig_temp, use_container_width=True)

    # Insights + table (right)
    with right:
        st.subheader("Insights")
        insights = compute_insights(df_view)

        # Render insights as big-icon pills
        for text, level, icon in insights:
            render_insight_pill(text, level, icon)

        st.divider()
        st.subheader("Recent Data (Newest First)")

        # Reverse so newest appears at the TOP
        recent_df = df_view.tail(10).iloc[::-1].reset_index(drop=True)
        st.dataframe(recent_df, use_container_width=True, hide_index=True)

    st.caption(f"Rendered at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC")


if __name__ == "__main__":
    main()
