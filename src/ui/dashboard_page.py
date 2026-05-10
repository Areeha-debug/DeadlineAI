import os
import streamlit as st
from src.ui.components import show_header, show_error, show_task_card, show_source_legend
from src.integrations.voice_recorder import add_voice_task
from src.agents.task_agent import run_agent


def show_dashboard_page():
    show_header()
    show_error()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### Gmail")
        if os.environ.get("GMAIL_CREDENTIALS_JSON_PATH"):
            st.success("✅ Connected")
        else:
            st.warning("⚠️ Missing Config")

    with col2:
        st.markdown("### Notion")
        if os.environ.get("NOTION_API_KEY") and os.environ.get(
                "NOTION_DATABASE_ID"):
            st.success("✅ Connected")
        else:
            st.warning("⚠️ Missing Config")

    with col3:
        st.markdown("### Voice")
        st.success("✅ Available")

    st.markdown("### Add a Voice Task")
    audio_value = st.audio_input("Record Voice Task")
    
    if audio_value:
        if "last_audio_hash" not in st.session_state:
            st.session_state.last_audio_hash = None
            
        current_audio_hash = hash(audio_value.getvalue())
        
        if current_audio_hash != st.session_state.last_audio_hash:
            st.session_state.last_audio_hash = current_audio_hash
            with st.spinner("Transcribing with Groq Whisper..."):
                try:
                    voice_task = add_voice_task(audio_value)
                    st.session_state.tasks.append(voice_task)
                    st.success("Voice task added successfully!")
                except Exception as e:
                    st.session_state.error = f"Failed to transcribe voice task: {str(e)}"
                    st.rerun()

    st.markdown("---")
    if st.button(
        "Fetch & Prioritize All Tasks",
        type="primary",
            use_container_width=True):
        with st.spinner("Pulling from Gmail and Notion, then prioritizing with AI... this may take 20-40 seconds"):
            try:
                tasks = run_agent()
                st.session_state.tasks = tasks
                st.session_state.stage = "results"
                st.rerun()
            except Exception as e:
                st.session_state.error = f"Agent failed: {str(e)}"
                st.rerun()

    st.markdown("---")
    if st.session_state.tasks:
        st.subheader("Current Tasks")
        show_source_legend()

        # Source filter
        st.session_state.source_filter = st.selectbox(
            "Filter by Source", [
                "All", "Gmail", "Notion", "Voice"], index=[
                "All", "Gmail", "Notion", "Voice"].index(
                st.session_state.get(
                    "source_filter", "All")))

        filtered_tasks = st.session_state.tasks
        if st.session_state.source_filter != "All":
            filtered_tasks = [
                t for t in filtered_tasks if str(
                    t.get(
                        "source",
                        "")).lower() == st.session_state.source_filter.lower()]

        for i, task in enumerate(filtered_tasks):
            show_task_card(task, i)
