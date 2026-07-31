import streamlit as st
import requests
import pandas as pd
import plotly.express as px

API = "http://127.0.0.1:8000"

st.title("SalesGenie Dashboard")

try:
    test = requests.get(f"{API}/docs", timeout=3)
    if test.status_code == 200:
        st.success("✅ Backend Connected")
    else:
        st.warning("⚠️ Backend running but not responding properly")
except:
    st.error("❌ Backend NOT running. Start FastAPI server.")


# ===============================
# ➕ CREATE LEAD
# ===============================
st.header("➕ Add Lead")

name = st.text_input("Name")
email = st.text_input("Email")
company = st.text_input("Company")
status = st.selectbox("Status", ["new", "contacted", "converted"])
notes = st.text_area("Notes")

if st.button("Create Lead"):
    if not name or not email:
        st.warning("Name and Email are required!")
    else:
        try:
            res = requests.post(
                f"{API}/leads/",
                json={
                    "name": name,
                    "email": email,
                    "company": company,
                    "status": status,
                    "notes": notes,
                },
                timeout=5   # ✅ ADDED
            )

            if res.status_code == 200:
                st.success("✅ Lead Created Successfully!")
            else:
                st.error("Failed to create lead")
                st.text(res.text)

        except Exception as e:
            st.error(f"Connection Error: {e}")


# ======================================================
# 📂 CSV UPLOAD 
# ======================================================
st.header("📂 Upload Leads via CSV")

uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:
    st.info(f"Selected file: {uploaded_file.name}")

    if st.button("Upload CSV"):
        try:
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")
            }

            res = requests.post(
                f"{API}/leads/upload-csv",
                files=files,
                timeout=10   
            )

            if res.status_code == 200:
                result = res.json()

                st.success("✅ CSV Processed Successfully")
                st.write("📊 Inserted:", result.get("inserted", 0))
                st.write("⚠️ Duplicates:", result.get("duplicates", 0))
                st.write("❌ Invalid:", result.get("invalid", 0))
            else:
                st.error("Failed to process CSV")
                st.text(res.text)

        except Exception as e:
            st.error(f"Upload Error: {e}")


# ===============================
# LOAD LEADS
# ===============================
st.header("All Leads")

if st.button("Load Leads"):
    try:
        res = requests.get(f"{API}/leads/", timeout=5)  # ✅ ADDED

        if res.status_code == 200:
            data = res.json()

            if data:
                df = pd.DataFrame(data)
                st.dataframe(df)
            else:
                st.warning("⚠️ No leads found")

        else:
            st.error("Failed to fetch leads")
            st.text(res.text)

    except Exception as e:
        st.error(f"Connection Error: {e}")

# ===============================
# 📊 DASHBOARD ANALYTICS (NEW)
# ===============================
st.header("📊 Lead Insights Dashboard")

if st.button("Show Analytics"):
    try:
        res = requests.get(f"{API}/leads/", timeout=5)

        if res.status_code == 200:
            data = res.json()

            if data:
                df = pd.DataFrame(data)

                # Leads by Status
                st.subheader("Leads by Status")
                status_counts = df["status"].value_counts()
                st.bar_chart(status_counts)

                # Leads by Company
                st.subheader("Top Companies")
                company_counts = df["company"].value_counts().head(5)
                st.bar_chart(company_counts)

                # Total Leads
                st.metric("Total Leads", len(df))

            else:
                st.warning("No data available")

        else:
            st.error("Failed to load data")

    except Exception as e:
        st.error(f"Error: {e}")


# ===============================
# UPDATE LEAD
# ===============================
st.header("Update Lead")

update_id = st.number_input("Lead ID to Update", min_value=1)

new_name = st.text_input("New Name")
new_email = st.text_input("New Email")
new_company = st.text_input("New Company")
new_status = st.selectbox("New Status", ["new", "contacted", "converted"])
new_notes = st.text_area("New Notes")

if st.button("Update Lead"):
    try:
        res = requests.put(
            f"{API}/leads/{int(update_id)}",
            json={
                "name": new_name,
                "email": new_email,
                "company": new_company,
                "status": new_status,
                "notes": new_notes,
            },
            timeout=5  
        )

        if res.status_code == 200:
            st.success("Lead updated successfully")
        else:
            st.error("Failed to update")
            st.text(res.text)

    except Exception as e:
        st.error(f"Error: {e}")


# ===============================
# DELETE LEAD
# ===============================
st.header("Delete Lead")

delete_id = st.number_input("Lead ID to Delete", min_value=1, key="delete")

if st.button("Delete Lead"):
    try:
        res = requests.delete(f"{API}/leads/{int(delete_id)}", timeout=5) 

        if res.status_code == 200:
            st.success("Lead deleted successfully")
        else:
            st.error("Failed to delete")
            st.text(res.text)

    except Exception as e:
        st.error(f"Error: {e}")


# ===============================
# COMPANY INTELLIGENCE
# ===============================
st.header("Company Intelligence")

cname = st.text_input("Enter company name")

if st.button("Analyze Company"):
    if cname.strip() == "":
        st.warning("Please enter a company name")
    else:
        try:
            url = f"{API}/intelligence/analyze/{cname.strip()}"
            res = requests.get(url, timeout=5)  

            if res.status_code == 200:
                st.success("Analysis Complete ✅")
                st.json(res.json())
            elif res.status_code == 404:
                st.error("API route not found (404). Check backend endpoint!")
            else:
                st.error(f"Error: {res.status_code}")
                st.text(res.text)

        except requests.exceptions.ConnectionError:
            st.error("Cannot connect to backend. Is server running?")
        except Exception as e:
            st.error(f"Unexpected Error: {e}")


# ===============================
# LEAD SCORING
# ===============================
st.header("Lead Scoring")

company = st.text_input("Company for scoring")
status = st.selectbox("Lead Status", ["new", "contacted", "qualified", "lost"])

if st.button("Get Score"):
    if company.strip() == "":
        st.warning("Please enter a company name")
    else:
        try:
            payload = {
                "company": company,
                "status": status
            }

            res = requests.post(
                f"{API}/intelligence/score",
                json=payload,
                timeout=5   
            )

            if res.status_code == 200:
                st.success("Score Generated ✅")
                st.json(res.json())
            else:
                st.error(f"Error: {res.status_code}")
                st.text(res.text)

        except Exception as e:
            st.error(f"Connection Error: {e}")

# ===============================
# 📧 AI OUTREACH GENERATOR (MODULE 3)
# ===============================

st.header("📧 AI Outreach Generator")


outreach_lead_id = st.number_input(
    "Lead ID",
    min_value=1,
    key="outreach_lead_id"
)


outreach_name = st.text_input(
    "Lead Name",
    key="outreach_name"
)


outreach_company = st.text_input(
    "Company Name",
    key="outreach_company"
)


outreach_industry = st.selectbox(
    "Industry",
    [
        "tech",
        "finance",
        "health",
        "other"
    ],
    key="outreach_industry"
)


outreach_status = st.selectbox(
    "Lead Status",
    [
        "new",
        "contacted",
        "converted"
    ],
    key="outreach_status"
)



if st.button("Generate Email"):

    try:

        res = requests.post(

            f"{API}/outreach/generate",

            json={

                "lead_id": outreach_lead_id,

                "name": outreach_name,

                "company": outreach_company,

                "industry": outreach_industry,

                "status": outreach_status

            },

            timeout=10

        )


        if res.status_code == 200:

            data = res.json()


            st.success(
                "✅ Outreach Generated & Saved"
            )


            st.info(
                f"Tone: {data['tone']}"
            )


            st.subheader(
                "Generated Message"
            )


            st.write(
                data["generated_message"]
            )


            st.write(
                "Outreach ID:",
                data["outreach_id"]
            )


        else:

            st.error(
                "Failed to generate outreach"
            )

            st.text(
                res.text
            )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )
# ===============================
# 🤖 AI LEAD SCORING (MODULE 4)
# ===============================

st.header("🤖 AI Lead Scoring + Recommendation")


score_lead_id = st.number_input(
    "Lead ID",
    min_value=1,
    key="score_lead_id"
)


score_company = st.text_input(
    "Company",
    key="score_company"
)


score_industry = st.selectbox(
    "Industry",
    [
        "tech",
        "finance",
        "health",
        "other"
    ],
    key="score_industry"
)


score_status = st.selectbox(
    "Status",
    [
        "new",
        "contacted",
        "qualified",
        "converted"
    ],
    key="score_status"
)



if st.button("Get AI Score"):

    try:

        res = requests.post(

            f"{API}/ai/score",

            json={

                "lead_id": score_lead_id,

                "company": score_company,

                "industry": score_industry,

                "status": score_status

            },

            timeout=10
        )


        if res.status_code == 200:

            data = res.json()


            st.success(
                "✅ AI Score Generated & Saved"
            )


            st.metric(
                "Lead Score",
                data["score"]
            )


            st.info(
                data["recommendation"]
            )


            st.write(
                "Score ID:",
                data["score_id"]
            )


        else:

            st.error(
                f"Failed to get score ({res.status_code})"
            )

            st.text(
                res.text
            )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )
# =====================================
# 🧠 MODULE 5 : CONVERSATION INTELLIGENCE
# =====================================


st.header(
    "🧠 Conversation Intelligence & CRM Integration"
)


lead_id = st.number_input(
    "Lead ID",
    min_value=1,
    key="conversation_lead"
)


conversation_type = st.selectbox(
    "Conversation Type",
    [
        "Sales Call",
        "Meeting",
        "Email"
    ],
    key="conversation_type"
)


transcript = st.text_area(
    "Paste Customer Conversation",
    height=200,
    key="conversation_text"
)



if st.button(
    "Analyze Conversation & Sync CRM"
):

    try:

        res = requests.post(

            f"{API}/conversation/analyze",

            json={

                "lead_id": lead_id,

                "conversation_type":
                conversation_type,

                "transcript":
                transcript

            },

            timeout=30

        )


        if res.status_code == 200:


            data = res.json()


            st.success(
                "✅ Conversation analyzed"
            )


            st.success(
                "📌 CRM Activity Synced"
            )


            st.subheader(
                "AI Conversation Insights"
            )


            st.write(
                data["analysis"]
            )


            st.subheader(
                "CRM Information"
            )


            st.write(
                "Lead ID:",
                data["lead_id"]
            )


            st.write(
                "Conversation ID:",
                data["conversation_id"]
            )


            st.write(
                "CRM Activity ID:",
                data["crm_activity_id"]
            )


            st.write(
                "CRM Status:",
                data["crm_status"]
            )



        else:

            st.error(
                res.text
            )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )

# ===============================
# EXECUTIVE KPI DASHBOARD
# ===============================


st.subheader(
    "📌 Executive Overview"
)


try:

    res = requests.get(
        f"{API}/dashboard/summary"
    )


    if res.status_code == 200:

        data = res.json()


        c1,c2,c3,c4 = st.columns(4)


        c1.metric(
            "Total Leads",
            data["total_leads"]
        )


        c2.metric(
            "New Leads",
            data["new_leads"]
        )


        c3.metric(
            "Converted",
            data["converted_leads"]
        )


        c4.metric(
            "Conversion Rate",
            data["conversion_rate"]
        )


except Exception as e:

    st.error(e)
# =====================================
# 📊 MODULE 6 : DASHBOARD & SALES ANALYTICS
# =====================================


st.header(
    "📊 SalesGenie AI Dashboard & Analytics"
)



# ===============================
# SALES SUMMARY
# ===============================

st.subheader(
    "📌 Sales Summary"
)


if st.button(
    "Load Sales Summary"
):

    try:

        res = requests.get(
            f"{API}/dashboard/summary",
            timeout=10
        )


        if res.status_code == 200:

            data = res.json()


            col1, col2, col3, col4 = st.columns(4)


            col1.metric(
                "Total Leads",
                data["total_leads"]
            )


            col2.metric(
                "New Leads",
                data["new_leads"]
            )


            col3.metric(
                "Converted Leads",
                data["converted_leads"]
            )


            col4.metric(
                "Conversion Rate",
                data["conversion_rate"]
            )


        else:

            st.error(
                "Failed to load summary"
            )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )


# ===============================
# PIPELINE STATUS WITH PLOTLY
# ===============================

st.subheader(
    "📈 Sales Pipeline Visualization"
)


if st.button("Show Pipeline"):

    try:

        res = requests.get(
            f"{API}/dashboard/pipeline",
            timeout=10
        )


        if res.status_code == 200:

            data = res.json()


            pipeline = data["pipeline"]


            if pipeline:

                df_pipeline = pd.DataFrame(
                    pipeline.items(),
                    columns=[
                        "Status",
                        "Count"
                    ]
                )


                # Bar Chart

                fig_bar = px.bar(
                    df_pipeline,
                    x="Status",
                    y="Count",
                    title="Lead Pipeline Status"
                )


                st.plotly_chart(
                    fig_bar,
                    use_container_width=True
                )



                # Pie Chart

                fig_pie = px.pie(
                    df_pipeline,
                    names="Status",
                    values="Count",
                    title="Lead Distribution"
                )


                st.plotly_chart(
                    fig_pie,
                    use_container_width=True
                )


            else:

                st.warning(
                    "No pipeline data available"
                )


        else:

            st.error(
                res.text
            )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )



# ===============================
# OUTREACH EFFECTIVENESS
# ===============================

st.subheader(
    "📧 Outreach Performance"
)



if st.button(
    "Analyze Outreach"
):

    try:

        res = requests.get(
            f"{API}/dashboard/outreach",
            timeout=10
        )


        if res.status_code == 200:

            data = res.json()


            st.metric(
                "Total AI Outreach Generated",
                data["total_outreach_generated"]
            )


        else:

            st.error(
                res.text
            )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )





# ===============================
# AI SCORE INSIGHTS
# ===============================


st.subheader(
    "🤖 AI Lead Score Insights"
)



if st.button(
    "Load AI Insights"
):

    try:

        res = requests.get(
            f"{API}/dashboard/scores",
            timeout=10
        )


        if res.status_code == 200:

            data = res.json()


            col1,col2 = st.columns(2)


            col1.metric(
                "Average Lead Score",
                data["average_score"]
            )


            col2.metric(
                "High Priority Leads",
                data["high_quality_leads"]
            )


        else:

            st.error(
                res.text
            )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )





# ===============================
# CRM ACTIVITY REPORT
# ===============================


st.subheader(
    "🔄 CRM Activity Report"
)



if st.button(
    "Load CRM Report"
):

    try:

        res = requests.get(
            f"{API}/dashboard/crm",
            timeout=10
        )


        if res.status_code == 200:

            data = res.json()


            col1,col2 = st.columns(2)


            col1.metric(
                "CRM Activities",
                data["crm_activities"]
            )


            col2.metric(
                "Customer Conversations",
                data["customer_conversations"]
            )


        else:

            st.error(
                res.text
            )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )





# ===============================
# SALES INTELLIGENCE REPORT
# ===============================


st.subheader(
    "🧠 Sales Intelligence Report"
)



if st.button(
    "Generate Sales Report"
):

    try:

        res = requests.get(
            f"{API}/dashboard/report",
            timeout=10
        )


        if res.status_code == 200:

            data = res.json()


            st.json(
                data
            )


        else:

            st.error(
                res.text
            )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )
        # =====================================
# AI FOLLOW-UP RECOMMENDATIONS
# =====================================

st.header(
    "🤖 AI Follow-up Recommendations"
)


if st.button(
    "Generate Follow-up Actions"
):

    try:

        res = requests.get(
            f"{API}/dashboard/recommendations",
            timeout=10
        )


        if res.status_code == 200:

            data = res.json()


            st.success(
                "AI Recommendations Generated"
            )


            df = pd.DataFrame(
                data["recommendations"]
            )


            st.dataframe(
                df,
                use_container_width=True
            )


        else:

            st.error(
                res.text
            )


    except Exception as e:

        st.error(
            f"Error: {e}"
        )
