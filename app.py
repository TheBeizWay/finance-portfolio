import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Financial Intelligence | Purav Mehta CA", page_icon="📊")
st.title("📊 Financial Cost Intelligence Model")
st.caption("Built by Purav Mehta CA · GAICD · thebeizway.com.au")

with st.sidebar:
    st.header("Parameters")
    dept = st.selectbox("Department / Program", ["Operations", "Projects", "Corporate Services", "ICT"])
    staff_cost = st.number_input("Staff Costs ($)", 50000, 5000000, 500000, step=10000)
    operating_cost = st.number_input("Operating Costs ($)", 10000, 2000000, 150000, step=5000)
    program_cost = st.number_input("Program/Project Costs ($)", 0, 5000000, 200000, step=10000)
    risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High"])
    timeline = st.slider("Planning Horizon (months)", 3, 24, 12)

risk_factor = {"Low": 1.05, "Medium": 1.12, "High": 1.20}[risk_level]
total_base = staff_cost + operating_cost + program_cost
contingency = total_base * (risk_factor - 1)
total_forecast = total_base + contingency
annual_forecast = total_forecast * (12 / timeline)
variance_flag = "⚠️ Over Budget Risk" if contingency > total_base * 0.15 else "✅ Within Tolerance"

st.subheader("📋 Budget Intelligence Output")
col1, col2, col3 = st.columns(3)
col1.metric("Base Budget", f"${total_base:,.0f}")
col2.metric("Risk-Adjusted Forecast", f"${total_forecast:,.0f}", f"+${contingency:,.0f} contingency")
col3.metric("Annualised Forecast", f"${annual_forecast:,.0f}")

if "Over Budget" in variance_flag:
    st.error(variance_flag)
else:
    st.success(variance_flag)

st.subheader("📊 Cost Breakdown")
breakdown = pd.DataFrame({
    "Category": ["Staff", "Operating", "Program/Project", "Contingency"],
    "Amount ($)": [staff_cost, operating_cost, program_cost, contingency]
})
st.bar_chart(breakdown.set_index("Category"))

st.subheader("📅 Monthly Burn Rate")
months = [f"Month {i+1}" for i in range(timeline)]
burn = np.linspace(total_forecast * 0.07, total_forecast * 0.09, timeline)
burn_df = pd.DataFrame({"Month": months, "Projected Spend ($)": burn})
st.line_chart(burn_df.set_index("Month"))

st.caption("Built with Python · Streamlit · For demonstration purposes.")
