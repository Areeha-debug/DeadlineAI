import streamlit as st
from src.ui.components import show_header, show_error, show_task_card, show_source_legend
from src.memory.task_store import clear_tasks


def show_results_page():
    show_header()
    show_error()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Total Tasks: {len(st.session_state.tasks)}")
    with col2:
        if st.button("Start Over", use_container_width=True):
            clear_tasks()
            st.session_state.tasks = []
            st.session_state.error = None
            st.session_state.location_filter = ""
            st.session_state.source_filter = "All"
            st.session_state.stage = "dashboard"
            st.rerun()

    if not st.session_state.tasks:
        st.warning("No tasks found.")
        return

    high_count = sum(
        1 for t in st.session_state.tasks if str(
            t.get(
                "priority",
                "")).upper() == "HIGH")
    medium_count = sum(
        1 for t in st.session_state.tasks if str(
            t.get(
                "priority",
                "")).upper() == "MEDIUM")
    low_count = sum(
        1 for t in st.session_state.tasks if str(
            t.get(
                "priority",
                "")).upper() == "LOW")

    m1, m2, m3 = st.columns(3)
    m1.metric("HIGH Priority", high_count)
    m2.metric("MEDIUM Priority", medium_count)
    m3.metric("LOW Priority", low_count)

    st.markdown("---")

    priority_filter = st.selectbox(
        "Filter by Priority",
        ["All", "HIGH only", "MEDIUM only", "LOW only"]
    )

    filtered_tasks = st.session_state.tasks
    if priority_filter != "All":
        target_priority = priority_filter.split(" ")[0]
        filtered_tasks = [t for t in filtered_tasks if str(
            t.get("priority", "")).upper() == target_priority]

    show_source_legend()
    st.markdown("<br>", unsafe_allow_html=True)

    for i, task in enumerate(filtered_tasks):
        show_task_card(task, i)

    st.markdown("---")
    st.caption("Powered by OpenAI GPT-4o · Gmail API · Notion API · OpenAI Whisper · Built with Streamlit on Google Antigravity")
