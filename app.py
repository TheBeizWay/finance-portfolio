import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Finance Manager Toolkit | Purav Mehta CA",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Finance Manager Toolkit")
st.caption("Built by Purav Mehta CA · thebeizway.com.au · Demonstration purposes only")

tab1, tab2, tab3, tab4 = st.tabs([
    "💰 Budget & Cost Model",
    "🔍 AP/AR Anomaly Detector",
    "👥 Payroll Compliance",
    "📋 Financial Control Dashboard"
])

# TAB 1 — BUDGET & COST MODEL
with tab1:
    st.header("Budget & Cost Intelligence Model")
    st.caption("Risk-adjusted forecasting for program and divisional planning.")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Parameters")
        dept = st.selectbox("Department", ["Operations", "Projects", "Corporate Services", "ICT", "Finance"])
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

        st.subheader("Output")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Base Budget", f"${total_base:,.0f}")
        m2.metric("Risk-Adjusted Forecast", f"${total_forecast:,.0f}", f"+${contingency:,.0f} contingency")
        m3.metric("Annualised Forecast", f"${annual_forecast:,.0f}")
        m4.metric("Variance to Approved", f"${variance:,.0f}", f"{variance_pct:.1f}%",
                  delta_color="normal" if variance >= 0 else "inverse")

        if variance < 0:
            st.error(f"OVER BUDGET by ${abs(variance):,.0f} — escalation required")
        elif variance_pct < 5:
            st.warning(f"Within {variance_pct:.1f}% of approved budget — monitor closely")
        else:
            st.success(f"${variance:,.0f} headroom remaining — within acceptable tolerance")

        st.subheader("Cost Breakdown")
        breakdown = pd.DataFrame({
            "Category": ["Staff", "Operating", "Program/Project", "Contingency"],
            "Amount ($)": [staff_cost, operating_cost, program_cost, contingency]
        })
        st.bar_chart(breakdown.set_index("Category"))

        st.subheader("Monthly Burn Rate")
        months = [f"M{i+1}" for i in range(timeline)]
        burn = np.linspace(total_forecast * 0.06, total_forecast * 0.10, timeline)
        cumulative = np.cumsum(burn)
        burn_df = pd.DataFrame({
            "Month": months,
            "Monthly Spend ($)": burn,
            "Cumulative ($)": cumulative
        })
        st.line_chart(burn_df.set_index("Month"))

# TAB 2 — AP/AR ANOMALY DETECTOR
with tab2:
    st.header("AP/AR Anomaly Detection")
    st.caption("Flags duplicate invoices, segregation of duty breaches, threshold circumvention and overdue AR.")

    np.random.seed(42)
    n = 60
    vendors = [f"Vendor_{i:02d}" for i in range(1, 16)]

    ap_data = pd.DataFrame({
        "Invoice #": [f"INV-{1000+i}" for i in range(n)],
        "Vendor": np.random.choice(vendors, n),
        "Amount ($)": np.random.choice([
            500, 1000, 5000, 10000, 2347, 8921, 1000, 500,
            10000, 3456, 7500, 15000, 250, 9999, 4500
        ], n),
        "Status": np.random.choice(["Paid", "Pending", "Overdue"], n, p=[0.6, 0.25, 0.15]),
        "Approved By": np.random.choice(
            ["Manager A", "Manager B", "Self-Approved", "Manager C"], n
        ),
        "Days Overdue": np.random.choice([0, 0, 0, 15, 32, 45, 60], n)
    })

    ap_data["Flag"] = ""
    ap_data.loc[ap_data["Amount ($)"] % 1000 == 0, "Flag"] = "Round Number"
    ap_data.loc[ap_data.duplicated(subset=["Vendor", "Amount ($)"], keep=False), "Flag"] = "Duplicate Risk"
    ap_data.loc[ap_data["Approved By"] == "Self-Approved", "Flag"] = "No Segregation of Duties"
    ap_data.loc[ap_data["Amount ($)"] == 9999, "Flag"] = "Just-Below-Threshold"
    ap_data.loc[(ap_data["Status"] == "Overdue") & (ap_data["Days Overdue"] > 30), "Flag"] = "Overdue >30 Days"

    flagged = ap_data[ap_data["Flag"] != ""]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Invoices", n)
    c2.metric("Flagged", len(flagged), f"{len(flagged)/n*100:.0f}%")
    c3.metric("Total AP Value", f"${ap_data['Amount ($)'].sum():,.0f}")
    c4.metric("Overdue AP", f"${ap_data[ap_data['Status']=='Overdue']['Amount ($)'].sum():,.0f}")

    st.subheader("Flag Breakdown")
    flag_counts = flagged.groupby("Flag").size().reset_index(name="Count")
    st.bar_chart(flag_counts.set_index("Flag"))

    st.subheader("Transaction Register")
    st.dataframe(ap_data, use_container_width=True)

    st.subheader("Recommended Actions")
    st.markdown("""
| Flag | Risk | Action |
|------|------|--------|
| Duplicate Risk | High | Hold payment — verify with vendor and original approver |
| No Segregation of Duties | High | Escalate for independent approval |
| Just-Below-Threshold | High | Review approval chain — potential policy circumvention |
| Round Number | Medium | Verify against contract or quote |
| Overdue >30 Days | Medium | Contact vendor — check dispute or processing error |
    """)

# TAB 3 — PAYROLL COMPLIANCE
with tab3:
    st.header("Payroll Compliance Checker")
    st.caption("Flags superannuation obligations, PAYG withholding issues and leave liability risks.")

    np.random.seed(7)
    n_emp = 20
    super_rate = 0.115

    payroll = pd.DataFrame({
        "Employee ID": [f"EMP-{100+i}" for i in range(n_emp)],
        "Type": np.random.choice(["Full-Time", "Part-Time", "Casual", "Contractor"], n_emp, p=[0.5, 0.2, 0.2, 0.1]),
        "Gross Pay ($)": np.random.randint(3000, 12000, n_emp),
        "PAYG Withheld ($)": np.random.randint(500, 3500, n_emp),
        "Super Paid ($)": np.random.randint(200, 1200, n_emp),
        "Leave Balance (days)": np.random.randint(0, 65, n_emp),
        "Super On Time": np.random.choice([True, False], n_emp, p=[0.85, 0.15])
    })

    payroll["Super Required ($)"] = (payroll["Gross Pay ($)"] * super_rate).round(2)
    payroll["Super Variance ($)"] = (payroll["Super Paid ($)"] - payroll["Super Required ($)"]).round(2)
    payroll["Tax Rate (%)"] = (payroll["PAYG Withheld ($)"] / payroll["Gross Pay ($)"] * 100).round(1)

    payroll["Flag"] = ""
    payroll.loc[payroll["Super Variance ($)"] < -50, "Flag"] = "Super Underpaid"
    payroll.loc[~payroll["Super On Time"], "Flag"] = "Super Paid Late"
    payroll.loc[payroll["Leave Balance (days)"] > 45, "Flag"] = "Excessive Leave Balance"
    payroll.loc[payroll["Tax Rate (%)"] < 10, "Flag"] = "Low PAYG Rate"
    payroll.loc[
        (payroll["Type"] == "Contractor") & (payroll["Super Paid ($)"] > 0), "Flag"
    ] = "Super to Contractor — Check Eligibility"

    flagged_p = payroll[payroll["Flag"] != ""]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Headcount", n_emp)
    c2.metric("Gross Payroll", f"${payroll['Gross Pay ($)'].sum():,.0f}")
    c3.metric("Compliance Issues", len(flagged_p))
    c4.metric("Leave Liability (days)", int(payroll["Leave Balance (days)"].sum()))

    if len(flagged_p) > 0:
        st.error(f"{len(flagged_p)} compliance issues — review before next pay run")
    else:
        st.success("No compliance issues in this pay run")

    display_cols = [
        "Employee ID", "Type", "Gross Pay ($)", "PAYG Withheld ($)",
        "Tax Rate (%)", "Super Required ($)", "Super Paid ($)",
        "Super Variance ($)", "Leave Balance (days)", "Flag"
    ]
    st.dataframe(payroll[display_cols], use_container_width=True)

    st.subheader("Payroll Summary")
    summary = pd.DataFrame({
        "Item": ["Total Gross Pay", "Total PAYG Withheld", "Total Super Required", "Total Super Paid", "Super Variance"],
        "Amount ($)": [
            payroll["Gross Pay ($)"].sum(),
            payroll["PAYG Withheld ($)"].sum(),
            payroll["Super Required ($)"].sum(),
            payroll["Super Paid ($)"].sum(),
            payroll["Super Variance ($)"].sum()
        ]
    })
    st.dataframe(summary, use_container_width=True)

# TAB 4 — FINANCIAL CONTROL DASHBOARD
with tab4:
    st.header("Financial Control Dashboard")
    st.caption("Month-end close status, GL variance flags and reconciliation tracker.")

    np.random.seed(99)

    recon_items = [
        "Bank Reconciliation", "Accounts Payable Ledger", "Accounts Receivable Ledger",
        "Payroll Clearing Account", "GST/BAS Reconciliation",
        "Fixed Assets Register", "Intercompany Accounts", "Prepayments & Accruals"
    ]

    recon_data = pd.DataFrame({
        "Control Item": recon_items,
        "Status": np.random.choice(["Complete", "In Progress", "Not Started", "Issues Found"], 8, p=[0.5, 0.25, 0.125, 0.125]),
        "Responsible": np.random.choice(["Finance Manager", "AP Officer", "AR Officer", "Payroll Officer"], 8


