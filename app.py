import json
import importlib
import streamlit as st
import services

importlib.reload(services)

st.set_page_config(page_title="Stride Dashboard", layout="wide")
st.title("Stride - Hybrid AI Student Assistant")
st.caption("Unified view of emails, schedules, weather, and academic tasks synced with Discord.")

with open("mock_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

col1, col2, col3 = st.columns(3)
col1.metric("Weather", services.get_weather())
col2.metric("Pending Tasks", len(data["tasks"]))
col3.metric("Schedule Conflicts", "1 Detected")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Schedule & Conflict Detection")
    for ev in data["calendar"]:
        st.info(f"**{ev['title']}** - {ev['date']} ({ev['start']} - {ev['end']})")
    st.error("Conflict: 'Lab Evaluation & Viva' overlaps with 'Hackathon Pitch Sync' at 10:15 AM.")

    st.subheader("Academic Tasks")
    for t in data["tasks"]:
        st.checkbox(f"{t['task']} (Due: {t['deadline']})", value=(t["status"] == "Done"))

with right:
    st.subheader("AI Daily Briefing & Email Prep")
    if st.button("Generate Fresh AI Briefing"):
        with st.spinner("Analyzing emails, tasks, and schedule..."):
            st.markdown(services.generate_briefing())
    else:
        st.write("Click above to generate an AI summary of unread emails and preparation items.")
