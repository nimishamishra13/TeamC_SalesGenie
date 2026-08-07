import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.title("💬 Conversation Intelligence")

lead_id = st.number_input(
    "Lead ID",
    min_value=1,
    step=1
)

transcript = st.text_area(
    "Conversation Transcript",
    height=250,
    placeholder="Paste your sales conversation here..."
)

if st.button("🚀 Analyze Conversation"):

    response = requests.post(
        f"{API}/conversation/analyze",
        json={
            "lead_id": lead_id,
            "transcript": transcript
        }
    )

    if response.status_code == 200:

        result = response.json()

        st.session_state.analysis = result
        st.session_state.transcript = transcript
        st.session_state.lead_id = lead_id

if "analysis" in st.session_state:

    data = st.session_state.analysis

    st.divider()

    st.subheader("📄 Meeting Summary")
    st.write(data["summary"])

    st.subheader("😊 Sentiment")
    st.success(data["sentiment"])

    st.subheader("🔥 Buying Intent")
    st.info(data["buying_intent"])

    st.subheader("⚠️ Pain Points")
    for item in data["pain_points"]:
        st.write("•", item)

    st.subheader("❌ Objections")
    for item in data["objections"]:
        st.write("•", item)

    st.subheader("➡️ Next Actions")
    for item in data["next_actions"]:
        st.write("•", item)

    st.subheader("📝 CRM Notes")
    st.write(data["crm_notes"])

if "analysis" in st.session_state:

    if st.button("💾 Save to CRM"):

        requests.post(
            f"{API}/conversation/save",
            json={
                "lead_id": st.session_state.lead_id,
                "transcript": st.session_state.transcript,
                "summary": st.session_state.analysis["summary"],
                "sentiment": st.session_state.analysis["sentiment"],
                "buying_intent": st.session_state.analysis["buying_intent"],
                "next_action": "\n".join(st.session_state.analysis["next_actions"]),
                "crm_notes": st.session_state.analysis["crm_notes"]
            }
        )

        st.success("Conversation saved successfully!")
