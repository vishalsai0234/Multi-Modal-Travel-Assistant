"""
app.py — Multi-Modal Travel Assistant
Entry point: streamlit run app.py
"""
#import sys
#import os
#sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st
import plotly.graph_objects as go
import uuid

# ── Page config must be FIRST Streamlit call ──────────────────────────────
st.set_page_config(
    page_title="🌍 Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    .source-badge-local {
        background: #d4edda;
        color: #155724;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .source-badge-web {
        background: #cce5ff;
        color: #004085;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .summary-box {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        line-height: 1.7;
        color: #1a1a1a;
    }
    .weather-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 0.8rem;
        text-align: center;
        margin: 0.2rem;
    }
    .metric-label { font-size: 0.75rem; color: #888; }
    .metric-value { font-size: 1.1rem; font-weight: 700; color: #333; }
</style>
""", unsafe_allow_html=True)


# ── Load graph (cached so it only builds once) ─────────────────────────────
@st.cache_resource(show_spinner="🔧 Initializing AI workflow...")
def load_graph():
    from graph.builder import build_graph
    return build_graph(use_memory=True)


# ── Session state initialization ───────────────────────────────────────────
if "thread_id" not in st.session_state:
    # Each user session gets a unique thread ID for MemorySaver
    st.session_state.thread_id = str(uuid.uuid4())

if "last_city" not in st.session_state:
    st.session_state.last_city = None

if "last_result" not in st.session_state:
    st.session_state.last_result = None

if "history" not in st.session_state:
    st.session_state.history = []


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗺️ Travel Assistant")
    st.markdown("---")
    st.markdown("**How it works:**")
    st.markdown("""
    1. Enter any city name
    2. The agent checks local knowledge first
    3. Falls back to web search if needed
    4. Fetches weather + images **in parallel**
    5. Renders everything in a structured UI
    """)
    st.markdown("---")
    st.markdown("**Cities with rich local data:**")
    st.markdown("🗼 Paris  |  🗾 Tokyo  |  🗽 New York")
    st.markdown("---")
    st.markdown("**Try also:**")
    st.markdown("⛩️ Kyoto  |  🌆 Dubai  |  🌲 Snohomish")
    st.markdown("---")

    # Show conversation history in sidebar
    if st.session_state.history:
        st.markdown("**Recent searches:**")
        for item in st.session_state.history[-5:]:
            st.markdown(f"• {item['city']} ({item['source']})")

    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.last_city = None
        st.session_state.last_result = None
        st.session_state.history = []
        st.rerun()


# ── Main UI ────────────────────────────────────────────────────────────────
st.markdown('<div class="main-header">🌍 Multi-Modal Travel Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Powered by LangGraph · Intelligent routing · Parallel data fetching</div>', unsafe_allow_html=True)

# Input area
col_input, col_btn = st.columns([4, 1])
with col_input:
    user_query = st.text_input(
        label="Ask about any city",
        placeholder='e.g. "Tell me about Kyoto"  or just  "Dubai"',
        label_visibility="collapsed",
    )
with col_btn:
    search_clicked = st.button("🔍 Explore", use_container_width=True, type="primary")

# Follow-up detection for Human-in-the-Loop memory demo
follow_up_keywords = ["next week", "next month", "tomorrow", "weather only", "just weather"]
is_follow_up = any(kw in user_query.lower() for kw in follow_up_keywords)

if is_follow_up and st.session_state.last_city:
    st.info(f"💡 Follow-up detected — updating weather for **{st.session_state.last_city}** (city memory preserved)")


# ── Graph Execution ────────────────────────────────────────────────────────
def run_graph(query: str):
    """Invokes the LangGraph workflow with the user's query."""
    app = load_graph()

    initial_state = {
        "user_query": query,
        "city": "",
        "source": "",
        "city_summary": "",
        "weather_forecast": [],
        "image_urls": [],
        "error": "",
        "final_output": None,
    }

    config = {
        "configurable": {
            "thread_id": st.session_state.thread_id,
        }
    }

    result = app.invoke(initial_state, config=config)
    return result


# ── Handle search ──────────────────────────────────────────────────────────
if search_clicked and user_query.strip():

    # Handle follow-up: override query to use remembered city
    effective_query = user_query
    if is_follow_up and st.session_state.last_city:
        effective_query = st.session_state.last_city

    with st.spinner(f"🔍 Researching... (weather & images fetching in parallel)"):
        try:
            result = run_graph(effective_query)
            output = result.get("final_output")

            if output:
                st.session_state.last_result = output
                st.session_state.last_city = output["city"]
                st.session_state.history.append({
                    "city": output["city"],
                    "source": output["data_source"],
                })
            else:
                st.error("The agent returned no output. Please try again.")
                st.stop()

        except Exception as e:
            st.error(f"❌ Something went wrong: {str(e)}")
            st.info("Tip: Make sure all dependencies are installed: `pip install -r requirements.txt`")
            st.stop()

elif search_clicked and not user_query.strip():
    st.warning("Please enter a city name before searching.")


# ── Render Results ─────────────────────────────────────────────────────────
if st.session_state.last_result:
    output = st.session_state.last_result

    # Error banner (non-fatal — still show partial results)
    if output.get("error"):
        st.warning(f"⚠️ Note: {output['error']}")

    st.markdown("---")

    # City header with source badge
    source_class = "source-badge-local" if "Local" in output["data_source"] else "source-badge-web"
    st.markdown(
        f"## 📍 {output['city']}  "
        f'<span class="{source_class}">📂 {output["data_source"]}</span>',
        unsafe_allow_html=True,
    )

    # ── Section 1: City Summary ────────────────────────────────────────────
    with st.expander("📖 City Overview", expanded=True):
        st.markdown(
            f'<div class="summary-box">{output["city_summary"]}</div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Section 2: Image Gallery ───────────────────────────────────────────
    image_urls = output.get("image_urls", [])
    if image_urls:
        st.subheader("📸 Gallery")
        img_cols = st.columns(len(image_urls))
        for col, url in zip(img_cols, image_urls):
            try:
                col.image(url, use_container_width=True)
            except Exception:
                col.warning("Image unavailable")
    else:
        st.info("No images available for this city.")

    st.markdown("---")

    # ── Section 3: Weather Forecast ────────────────────────────────────────
    forecast = output.get("weather_forecast", [])
    if forecast:
        st.subheader("🌤️ 7-Day Weather Forecast")

        # Plotly interactive line chart
        days = [f"{d['day']}\n{d['date']}" for d in forecast]
        highs = [d["temp_high"] for d in forecast]
        lows = [d["temp_low"] for d in forecast]
        conditions = [d["condition"] for d in forecast]
        humidity = [d["humidity"] for d in forecast]

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=days,
            y=highs,
            name="High °C",
            mode="lines+markers",
            line=dict(color="#FF6B6B", width=3),
            marker=dict(size=8, symbol="circle"),
            hovertemplate="<b>%{x}</b><br>High: %{y}°C<extra></extra>",
        ))

        fig.add_trace(go.Scatter(
            x=days,
            y=lows,
            name="Low °C",
            mode="lines+markers",
            line=dict(color="#4ECDC4", width=3),
            marker=dict(size=8, symbol="circle"),
            fill="tonexty",
            fillcolor="rgba(102, 126, 234, 0.08)",
            hovertemplate="<b>%{x}</b><br>Low: %{y}°C<extra></extra>",
        ))

        fig.add_trace(go.Bar(
            x=days,
            y=humidity,
            name="Humidity %",
            yaxis="y2",
            opacity=0.3,
            marker_color="#667eea",
            hovertemplate="<b>%{x}</b><br>Humidity: %{y}%<extra></extra>",
        ))

        fig.update_layout(
            title=f"Weather Forecast for {output['city']}",
            xaxis_title="Day",
            yaxis_title="Temperature (°C)",
            yaxis2=dict(
                title="Humidity (%)",
                overlaying="y",
                side="right",
                range=[0, 150],
            ),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white",
            paper_bgcolor="white",
            hovermode="x unified",
            margin=dict(l=20, r=20, t=60, b=20),
        )
        fig.update_xaxes(showgrid=True, gridcolor="#f0f0f0")
        fig.update_yaxes(showgrid=True, gridcolor="#f0f0f0")

        st.plotly_chart(fig, use_container_width=True)

        # Weather cards row
        st.markdown("**Daily Breakdown:**")
        card_cols = st.columns(len(forecast))
        condition_icons = {
            "Sunny": "☀️", "Partly Cloudy": "⛅", "Cloudy": "☁️",
            "Rainy": "🌧️", "Overcast": "🌥️", "Humid": "💧",
            "Windy": "💨", "Clear": "🌙",
        }
        for col, day_data in zip(card_cols, forecast):
            icon = condition_icons.get(day_data["condition"], "🌡️")
            col.markdown(f"""
            <div class="weather-card">
                <div class="metric-label">{day_data['day'][:3]}</div>
                <div style="font-size:1.4rem">{icon}</div>
                <div class="metric-value">{day_data['temp_high']}°</div>
                <div class="metric-label">{day_data['temp_low']}°</div>
                <div class="metric-label" style="font-size:0.65rem">{day_data['condition']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("Weather data unavailable. The weather service may have timed out.")

    st.markdown("---")

    # ── Section 4: Raw JSON output (collapsible) ───────────────────────────
    with st.expander("🔧 Structured JSON Output (what the graph returns)", expanded=False):
        st.json(output)

    # ── Footer ─────────────────────────────────────────────────────────────
    st.markdown(
        f"<small>🧵 Session thread: `{st.session_state.thread_id[:8]}...` "
        f"| Source: **{output['data_source']}**</small>",
        unsafe_allow_html=True,
    )

else:
    # Landing state — show before any search
    st.markdown("""
    <div style="text-align:center; padding: 3rem; color: #aaa;">
        <div style="font-size:4rem">✈️</div>
        <div style="font-size:1.2rem; margin-top:1rem">
            Enter a city above to begin exploring
        </div>
        <div style="font-size:0.9rem; margin-top:0.5rem">
            Cities in our knowledge base: <strong>Paris, Tokyo, New York</strong><br>
            Any other city will trigger live web search
        </div>
    </div>
    """, unsafe_allow_html=True)
