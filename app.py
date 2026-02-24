import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(
    page_title="Finance Manager Toolkit | Purav Mehta CA",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Finance Manager Toolkit")
st.caption("Built by Purav Mehta CA · thebeizway.com.au · For demonstration purposes only")

tab1, tab2, tab3, tab4 = st.tabs([
    "💰 Budget & Cost Model",
    "🔍 AP/AR Anomaly Detector", 
    "👥 Payroll Compliance",
    "📋 Financial Control Dashboard"
])

# ── TAB 1: BUDGET & COST MODEL ──────────────────────────────────────────────
with tab1:
    st.header("Budget & Cost Intelligence Model")
    st.write("Risk-adjusted budget forecasting for program and divisional planning.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Parameters")
        dept = st.selectbox("Department / Program", [
            "Operations", "Projects", "Corporate Services", "ICT", "Finance"
        ])
        staff_cost = st.number_input("Staff Costs ($)", 50000, 5000000, 500000, step=10000)
        operating_cost = st.number_input("Operating Costs ($)", 10000, 2000000, 150000, step=5000)
        program_cost = st.number_input("Program/Project Costs ($)", 0, 5000000, 200000, step=10000)
        risk_level = st.selectbox("Risk Level", ["Low", "Medium", "High"])
        timeline = st.slider("Planning Horizon (months)", 3, 24, 12)
        approved_budget = st.number_input("Approved Budget ($)", 100000, 10000000, 1000000, step=50000)

    with col2:
        risk_factor = {"Low": 1.05, "Medium": 1.12, "High": 1.20}[risk_level]
        total_base = staff_cost + operating_cost + program_cost
        contingency = total_base * (risk_factor - 1)
        total_forecast = total_base + contingency
        annual_forecast = total_forecast * (12 / timeline)
        variance = approved_budget - total_forecast
        variance_pct = (variance / approved_budget) * 100

        st.subheader("Budget Intelligence Output")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Base Budget", f"${total_base:,.0f}")
        m2.metric("Risk-Adjusted Forecast", f"${total_forecast:,.0f}", f"+${contingency:,.0f}")
        m3.metric("Annualised Forecast", f"${annual_forecast:,.0f}")
        m4.metric("Variance to Approved", f"${variance:,.0f}", f"{variance_pct:.1f}%",
                  delta_color="normal" if variance >= 0 else "inverse")

        if variance < 0:
            st.error(f"⚠️ OVER BUDGET by ${abs(variance):,.0f} — escalation required")
        elif variance_pct < 5:
            st.warning(f"⚠️ Within {variance_pct:.1f}% of approved budget — monitor closely")
        else:
            st.success(f"✅ ${variance:,.0f} headroom remaining — within acceptable tolerance")

        st.subheader("Cost Breakdown")
        breakdown = pd.DataFrame({
            "Category": ["Staff", "Operating", "Program/Project", "Contingency"],
            "Amount ($)": [staff_cost, operating_cost, program_cost, contingency]
        })
        st.bar_chart(breakdown.set_index("Category"))

        st.subheader("Monthly Burn Rate Projection")
        months = [f"M{i+1}" for i in range(timeline)]
        burn = np.linspace(total_forecast * 0.06, total_forecast * 0.10, timeline)
        cumulative = np.cumsum(burn)
        budget_line = [approved_budget] * timeline
        burn_df = pd.DataFrame({
            "Month": months,
            "Monthly Spend ($)": burn,
            "Cumulative ($)": cumulative,
            "Approved Budget ($)": budget_line
        })
        st.line_chart(burn_df.set_index("Month"))

# ── TAB 2: AP/AR ANOMALY DETECTOR ───────────────────────────────────────────
with tab2:
    st.header("AP/AR Anomaly Detection")
    st.write("Flags duplicate invoices, overdue receivables, round-number risks and new vendor alerts.")

    np.random.seed(42)
    n = 60
    vendors = [f"Vendor_{i:02d}" for i in range(1, 16)]
    
    ap_data = pd.DataFrame({
        "Invoice #": [f"INV-{1000+i}" for i in range(n)],
        "Vendor": np.random.choice(vendors, n),
        "Amount ($)": np.random.choice([
            500, 1000, 5000, 10000, 2347, 8921, 1000, 500, 10000,
            3456, 7500, 15000, 250, 9999, 4500
        ], n),
        "Invoice Date": pd.date_range("2025-07-01", periods=n, freq="3D"),
        "Due Date": pd.date_range("2025-08-01", periods=n, freq="3D"),
        "Status": np.random.choice(["Paid", "Pending", "Overdue"], n, p=[0.6, 0.25, 0.15]),
        "Approved By": np.random.choice(["Manager A", "Manager B", "Self-Approved", "Manager C"], n)
    })

    ap_data["Days Overdue"] = ap_data.apply(
        lambda r: max(0, (datetime(2025, 12, 1) - r["Due Date"]).days)
        if r["Status"] == "Overdue" else 0, axis=1
    )

    ap_data["Flag"] = ""
    ap_data.loc[ap_data["Amount ($)"] % 1000 == 0, "Flag"] = "⚠️ Round Number"
    ap_data.loc[ap_data.duplicated(subset=["Vendor", "Amount ($)"], keep=False), "Flag"] = "🚨 Duplicate Risk"
    ap_data.loc[ap_data["Approved By"] == "Self-Approved", "Flag"] = "🔴 No Segregation of Duties"
    ap_data.loc[ap_data["Amount ($)"] == 9999, "Flag"] = "🚨 Just-Below-Threshold"
    ap_data.loc[(ap_data["Status"] == "Overdue") & (ap_data["Days Overdue"] > 30), "Flag"] = "⚠️ Overdue >30 Days"

    flagged = ap_data[ap_data["Flag"] != ""]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Invoices", n)
    col2.metric("Flagged for Review", len(flagged), f"{len(flagged)/n*100:.0f}% of total")
    col3.metric("Total AP Value", f"${ap_data['Amount ($)'].sum():,.0f}")
    col4.metric("Overdue AP", f"${ap_data[ap_data['Status']=='Overdue']['Amount ($)'].sum():,.0f}")

    st.subheader("Flag Summary")
    flag_summary = flagged.groupby("Flag").size().reset_index(name="Count")
    st.bar_chart(flag_summary.set_index("Flag"))

    st.subheader("All Transactions — Flagged Items Highlighted")
    
    def highlight_flags(row):
        if row["Flag"] == "🚨 Duplicate Risk" or row["Flag"] == "🚨 Just-Below-Threshold":
            return ["background-color: #f8d7da"] * len(row)
        elif row["Flag"] == "🔴 No Segregation of Duties":
            return ["background-color: #f5c6cb"] * len(row)
        elif row["Flag"] != "":
            return ["background-color: #fff3cd"] * len(row)
        return [""] * len(row)

    st.dataframe(
        ap_data.style.apply(highlight_flags, axis=1),
        use_container_width=True
    )

    st.subheader("Recommended Actions")
    st.markdown("""
    | Flag | Risk | Recommended Action |
    |------|------|-------------------|
    | 🚨 Duplicate Risk | High | Hold payment — verify with vendor and original approver |
    | 🔴 No Segregation of Duties | High | Escalate to Finance Manager for independent approval |
    | 🚨 Just-Below-Threshold | High | Review approval chain — potential threshold circumvention |
    | ⚠️ Round Number | Medium | Verify invoice is supported by a contract or quote |
    | ⚠️ Overdue >30 Days | Medium | Contact vendor — check dispute or payment processing error |
    """)

# ── TAB 3: PAYROLL COMPLIANCE ────────────────────────────────────────────────
with tab3:
    st.header("Payroll Compliance Checker")
    st.write("Flags superannuation obligations, PAYG withholding issues and leave liability risks.")

    np.random.seed(7)
    n_emp = 20
    
    payroll_data = pd.DataFrame({
        "Employee ID": [f"EMP-{100+i}" for i in range(n_emp)],
        "Employment Type": np.random.choice(["Full-Time", "Part-Time", "Casual", "Contractor"], n_emp, p=[0.5, 0.2, 0.2, 0.1]),
        "Gross Pay ($)": np.random.randint(3000, 12000, n_emp),
        "PAYG Withheld ($)": np.random.randint(500, 3500, n_emp),
        "Super Paid ($)": np.random.randint(200, 1200, n_emp),
        "Annual Leave Balance (days)": np.random.randint(0, 65, n_emp),
        "Super Paid On Time": np.random.choice([True, False], n_emp, p=[0.85, 0.15])
    })

    super_rate = 0.115
    payroll_data["Super Required ($)"] = (payroll_data["Gross Pay ($)"] * super_rate).round(2)
    payroll_data["Super Variance ($)"] = payroll_data["Super Paid ($)"] - payroll_data["Super Required ($)"]
    
    payroll_data["Effective Tax Rate (%)"] = (
        payroll_data["PAYG Withheld ($)"] / payroll_data["Gross Pay ($)"] * 100
    ).round(1)

    payroll_data["Compliance Flag"] = ""
    payroll_data.loc[payroll_data["Super Variance ($)"] < -50, "Compliance Flag"] = "🚨 Super Underpaid"
    payroll_data.loc[~payroll_data["Super Paid On Time"], "Compliance Flag"] = "⚠️ Super Paid Late"
    payroll_data.loc[payroll_data["Annual Leave Balance (days)"] > 45, "Compliance Flag"] = "⚠️ Excessive Leave Balance"
    payroll_data.loc[payroll_data["Effective Tax Rate (%)"] < 10, "Compliance Flag"] = "🔴 Low PAYG Rate — Review"
    payroll_data.loc[
        (payroll_data["Employment Type"] == "Contractor") & 
        (payroll_data["Super Paid ($)"] > 0), "Compliance Flag"
    ] = "⚠️ Super Paid to Contractor — Check Eligibility"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Headcount", n_emp)
    col2.metric("Total Gross Payroll", f"${payroll_data['Gross Pay ($)'].sum():,.0f}")
    col3.metric("Super Compliance Issues", len(payroll_data[payroll_data["Compliance Flag"].str.contains("Super", na=False)]))
    col4.metric("Total Leave Liability (days)", int(payroll_data["Annual Leave Balance (days)"].sum()))

    flagged_payroll = payroll_data[payroll_data["Compliance Flag"] != ""]
    if len(flagged_payroll) > 0:
        st.error(f"⚠️ {len(flagged_payroll)} compliance issues identified — review required before next pay run")
    else:
        st.success("✅ No compliance issues identified in this pay run")

    st.subheader("Payroll Register — Compliance View")
    display_cols = ["Employee ID", "Employment Type", "Gross Pay ($)", 
                    "PAYG Withheld ($)", "Effective Tax Rate (%)",
                    "Super Required ($)", "Super Paid ($)", "Super Variance ($)",
                    "Annual Leave Balance (days)", "Compliance Flag"]
    
    def highlight_payroll(row):
        if "🚨" in str(row["Compliance Flag"]):
            return ["background-color: #f8d7da"] * len(row)
        elif "⚠️" in str(row["Compliance Flag"]):
            return ["background-color: #fff3cd"] * len(row)
        elif "🔴" in str(row["Compliance Flag"]):
            return ["background-color: #f5c6cb"] * len(row)
        return [""] * len(row)

    st.dataframe(
        payroll_data[display_cols].style.apply(highlight_payroll,

