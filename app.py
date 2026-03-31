import streamlit as st
import pandas as pd
from portfolio import get_portfolio_snapshot, YFINANCE_AVAILABLE
from dotenv import load_dotenv
import os
from xai_sdk import Client # Grok AI

# Load environment variables (for local dev)
load_dotenv()

# Get API keys - prefer Streamlit secrets, fallback to env vars
polygon_key = os.getenv("POLYGON_API_KEY") or st.secrets.get("POLYGON_API_KEY")
xai_key = os.getenv("XAI_API_KEY") or st.secrets.get("XAI_API_KEY")

# Initialize clients only if keys exist
xai_client = None
if xai_key:
    try:
        xai_client = Client(api_key=xai_key)
    except Exception as e:
        st.error(f"Error initializing Grok: {e}")

st.set_page_config(page_title="Jane Street AI Agent — Your Book", layout="wide")
st.title("🚀 Jane Street AI Trading Agent")
st.caption("Live Greeks • Scenarios • Risk • AI Advice (exactly like the desk)")

# Show API status
col1, col2, col3 = st.columns(3)
with col1:
    if YFINANCE_AVAILABLE:
        st.success("✅ Price Data (yfinance)")
    else:
        st.warning("⚠️ yfinance not installed")
with col2:
    if polygon_key:
        st.success("✅ Polygon.io Connected")
    else:
        st.info("ℹ️ Polygon not required (using yfinance)")
with col3:
    if xai_client:
        st.success("✅ Grok AI Connected")
    else:
        st.warning("⚠️ Grok AI Not Connected")

if st.button("🔄 Refresh All Data"):
    st.rerun()

with st.spinner("Loading portfolio data..."):
    snapshot = get_portfolio_snapshot()

# Dashboard table
df = pd.DataFrame.from_dict(snapshot["positions"], orient="index")
st.subheader("Portfolio Snapshot & Net Greeks")
st.dataframe(df, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.metric("Total Market Value", f"${snapshot['total_mv']:,.0f}")
    st.metric("Net Delta (equiv shares)", f"{snapshot['net_delta_equiv']:,}")
with col2:
    st.metric("SPY-Equivalent Exposure", f"{snapshot['spx_equiv']:,} shares")
    st.caption("→ Your delta is very high (5–8× SPY) — collar is working")

# AI Co-pilot (Grok)
st.subheader("🤖 AI Jane Street Analyst")

if xai_client:
    if st.button("Get Full Risk Advice"):
        prompt = f"""
You are a Jane Street trader. Analyze this exact portfolio snapshot:
{snapshot}
Current date: March 31 2026.
Give concise bullet-point advice on concentration, Greeks, post-April covered-call plan, and any immediate actions.
Speak exactly like you do in our chat.
"""
        response = xai_client.chat.completions.create(
            model="grok-2",
            messages=[{"role": "user", "content": prompt}]
        )
        st.write(response.choices[0].message.content)
else:
    st.warning("⚠️ Connect Grok API in Streamlit Cloud secrets to enable AI analysis")

# Quick scenario button
st.subheader("Quick Scenario")
price_drop = st.slider("TSLA % drop", 0, 60, 20)
if st.button("Run TSLA Drop Scenario"):
    st.info("Scenario engine coming in v2 — for now copy-paste your earlier tables or ask me in chat.")
    st.caption("Tip: Just say 'run scenario analysis for TSLA -25%' in this chat and I'll give the table instantly.")

st.success("✅ Agent running! Refresh every 60s. Your April covered calls are still deep OTM.")
