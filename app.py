import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state for leads database
if "leads_data" not in st.session_state:
    st.session_state.leads_data = pd.DataFrame(columns=[
        "id", "company", "industry", "employees", "decision_maker", "role", 
        "ai_need", "lead_score", "status", "notes", "created_at"
    ])
    st.session_state.next_id = 1

def add_lead(data):
    """Add a lead to session state dataframe"""
    new_row = pd.DataFrame([{
        "id": st.session_state.next_id,
        "company": data[0],
        "industry": data[1],
        "employees": data[2],
        "decision_maker": data[3],
        "role": data[4],
        "ai_need": data[5],
        "lead_score": data[6],
        "status": data[7],
        "notes": data[8],
        "created_at": data[9]
    }])
    st.session_state.leads_data = pd.concat([st.session_state.leads_data, new_row], ignore_index=True)
    st.session_state.next_id += 1

def load_leads():
    """Load all leads from session state"""
    return st.session_state.leads_data.sort_values("id", ascending=False).reset_index(drop=True)

def update_status(lead_id, new_status):
    """Update status of a lead"""
    mask = st.session_state.leads_data["id"] == lead_id
    if mask.any():
        st.session_state.leads_data.loc[mask, "status"] = new_status

def score_lead(employees, role, ai_need):
    score = 0
    if employees >= 200: score += 20
    if employees >= 500: score += 10
    if role.lower() in ["cto", "founder", "ceo", "ai head", "ai/ml head", "innovation head", "engineering head"]:
        score += 30
    if ai_need.strip(): score += 40
    return min(score, 100)

def ai_use_case(industry):
    mapping = {
        "Healthcare": "AI customer support, document processing, appointment automation and predictive analytics",
        "Finance": "Fraud detection, document automation, customer-service assistants and risk analytics",
        "Retail": "Demand forecasting, recommendation systems, customer-support automation and inventory analytics",
        "Manufacturing": "Predictive maintenance, quality inspection, process automation and demand forecasting",
        "Education": "AI tutoring, student-support assistants, document processing and personalized learning",
        "Software": "AI coding assistants, support automation, knowledge-base search and workflow automation",
        "Logistics": "Route optimization, demand forecasting, document processing and customer-support automation",
        "Other": "Customer support automation, document processing, analytics and workflow automation"
    }
    return mapping.get(industry, mapping["Other"])

def generate_email(company, person, role, industry, ai_need):
    return f"""Subject: AI Automation Opportunity for {company}

Hello {person},

I was researching {company} and noticed that you operate in the {industry} industry.

Based on your business area, there may be opportunities to use AI for {ai_need.lower()}.

I would be happy to understand your current workflow and see whether an AI solution could reduce manual effort or improve efficiency.

Would you be open to a short discovery call?

Regards,
Mahmood Zuhair
AI Sales & Business Development
"""

st.set_page_config(page_title="AI B2B Sales Assistant", page_icon="🤖", layout="wide")

st.title("🤖 AI-Powered B2B Lead Generation & CRM Assistant")
st.caption("Portfolio project aligned with AI sales, prospecting, lead qualification, outreach and CRM workflows.")

menu = st.sidebar.radio("Navigation", ["Dashboard", "Add Lead", "AI Use-Case Finder", "Cold Email Generator", "Lead Database"])

if menu == "Dashboard":
    df = load_leads()
    st.subheader("Sales Dashboard")
    if df.empty:
        st.info("No leads yet. Add your first prospect from the sidebar.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Leads", len(df))
        c2.metric("Qualified Leads", int((df["lead_score"] >= 70).sum()))
        c3.metric("Meetings", int((df["status"] == "Meeting Scheduled").sum()))
        c4.metric("Avg. Lead Score", round(df["lead_score"].mean(), 1))

        st.subheader("Pipeline")
        pipeline = df["status"].value_counts().reindex(
            ["New","Contacted","Responded","Qualified","Meeting Scheduled","Opportunity","Won","Lost"],
            fill_value=0)
        st.bar_chart(pipeline)

        st.subheader("Recent Leads")
        st.dataframe(df[["company","industry","decision_maker","role","lead_score","status"]].head(10),
                     use_container_width=True)

elif menu == "Add Lead":
    st.subheader("➕ Add B2B Prospect")
    with st.form("lead_form"):
        company = st.text_input("Company name")
        industry = st.selectbox("Industry", ["Software","Healthcare","Finance","Retail","Manufacturing","Education","Logistics","Other"])
        employees = st.number_input("Employees", min_value=1, value=200)
        person = st.text_input("Decision maker")
        role = st.selectbox("Decision-maker role",
                            ["CTO","Founder","CEO","AI Head","AI/ML Head","Innovation Head","Engineering Head","Other"])
        ai_need = st.text_area("Potential AI requirement / pain point")
        notes = st.text_area("Notes")
        submitted = st.form_submit_button("Calculate Score & Save Lead")

    if submitted:
        if not company or not person:
            st.error("Company name and decision maker are required.")
        else:
            score = score_lead(employees, role, ai_need)
            add_lead((company, industry, employees, person, role, ai_need, score, "New", notes, 
                     datetime.now().strftime("%Y-%m-%d %H:%M")))
            st.success(f"Lead saved successfully. Lead score: {score}/100")
            st.rerun()

elif menu == "AI Use-Case Finder":
    st.subheader("💡 AI Business Use-Case Finder")
    industry = st.selectbox("Select target industry",
                            ["Software","Healthcare","Finance","Retail","Manufacturing","Education","Logistics","Other"])
    if st.button("Find AI Opportunities"):
        st.success(f"Potential AI opportunities for {industry}:")
        for item in ai_use_case(industry).split(", "):
            st.write("• " + item.capitalize())

elif menu == "Cold Email Generator":
    st.subheader("📧 Personalized Cold Email Generator")
    company = st.text_input("Company")
    person = st.text_input("Decision maker")
    role = st.text_input("Role", value="CTO")
    industry = st.selectbox("Industry", ["Software","Healthcare","Finance","Retail","Manufacturing","Education","Logistics","Other"])
    need = st.text_input("Potential AI requirement", value=ai_use_case(industry))
    if st.button("Generate Email"):
        if company and person:
            st.code(generate_email(company, person, role, industry, need), language="text")
        else:
            st.warning("Enter company and decision-maker name.")

elif menu == "Lead Database":
    st.subheader("📋 Lead Database / Mini CRM")
    df = load_leads()
    if df.empty:
        st.info("No leads available.")
    else:
        st.dataframe(df, use_container_width=True)
        st.divider()
        lead_id = st.number_input("Lead ID to update", min_value=1, step=1)
        new_status = st.selectbox("New status",
                                  ["New","Contacted","Responded","Qualified","Meeting Scheduled","Opportunity","Won","Lost"])
        if st.button("Update Status"):
            update_status(lead_id, new_status)
            st.success("Status updated.")
            st.rerun()
        st.download_button("⬇️ Export Leads as CSV",
                           df.to_csv(index=False).encode("utf-8"),
                           "b2b_leads.csv",
                           "text/csv")
