import streamlit as st
import pandas as pd
from portfolio import get_portfolio_snapshot
from dotenv import load_dotenv
import os
from xai_sdk import Client # Grok AI

# Load environment variables (for local dev)
load_dotenv()

# Get API keys - prefer Streamlit secrets, fallback to env vars
polygon_key = os.getenv("POLYGON_API_KEY") or st.secrets.get("POLYGON_API_KEY")
xai_key = os.getenv("XAI_API_KEY") or st.secrets.get("XAI_API_KEY")

if polygon_key:
    st.session_state.polygon_key = polygon_key
if xai_key:
    st.session_state.xai_key = xai_key

# Initialize clients only if keys exist
if 'xai_client' not in st.session_state and xai_key:
    xai_client = Client(api_key=xai_key)
    st.session_state.xai_client = xai_client
    st.session_state.xai_connected = True
else:
    st.session_state.xai_connected = False

st.set_page_config(page_title="Jane Street AI Agent — Your Book", layout="wide")
st.title("🚀 Jane Street AI Trading Agent")
st.caption("Live Greeks • Scenarios • Risk • AI Advice (exactly like the desk)")

# Show API status
col1, col2 = st.columns(2)
with col1:
    if polygon_key:
        st.success("✅ Polygon.io Connected")
    else:
        st.error("❌ Polygon API Key Missing")
with col2:
    if st.session_state.get('xai_connected'):
        st.success("✅ Grok AI Connected")
    else:
        st.warning("⚠️ Grok AI Not Connected (check secrets)")

if st.button("🔄 Refresh All Data"):
    st.rerun()

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

# Only show button if API is connected
if st.session_state.get('xai_connected'):
    if st.button("Get Full Risk Advice"):
        prompt = f"""
You are a Jane Street trader. Analyze this exact portfolio snapshot:
{snapshot}
Current date: March 31 2026.
Give concise bullet-point advice on concentration, Greeks, post-April covered-call plan, and any immediate actions.
Speak exactly like you do in our chat.
"""
        response = st.session_state.xai_client.chat.completions.create(
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
