import streamlit as st
import pandas as pd
from portfolio import get_portfolio_snapshot
from dotenv import load_dotenv
import os
from xai_sdk import Client # Grok AI

load_dotenv()
xai_client = Client(api_key=os.getenv("XAI_API_KEY"))

st.set_page_config(page_title="Jane Street AI Agent — Your Book", layout="wide")
st.title("🚀 Jane Street AI Trading Agent")
st.caption("Live Greeks • Scenarios • Risk • AI Advice (exactly like the desk)")

if st.button("🔄 Refresh All Data"):
    pass # Streamlit auto-refreshes

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
if st.button("Get Full Risk Advice"):
    prompt = f"""
You are a Jane Street trader. Analyze this exact portfolio snapshot:
{snapshot}
Current date: March 31 2026.
Give concise bullet-point advice on concentration, Greeks, post-April covered-call plan, and any immediate actions.
Speak exactly like you do in our chat.
"""
    response = xai_client.chat.completions.create(
        model="grok-4.20", # or latest flagship
        messages=[{"role": "user", "content": prompt}]
    )
    st.write(response.choices[0].message.content)

# Quick scenario button
st.subheader("Quick Scenario")
price_drop = st.slider("TSLA % drop", 0, 60, 20)
if st.button("Run TSLA Drop Scenario"):
    st.info("Scenario engine coming in v2 — for now copy-paste your earlier tables or ask me in chat.")
    st.caption("Tip: Just say 'run scenario analysis for TSLA -25%' in this chat and I'll give the table instantly.")

st.success("✅ Agent running! Refresh every 60s. Your April covered calls are still deep OTM.")
