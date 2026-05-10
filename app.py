import streamlit as st
import src.config.settings
import src.ui.dashboard_page
import src.ui.results_page
import src.config.settings  # ← this runs the EnvironmentError check immediately

st.set_page_config(page_title="TaskMind Agent", page_icon="🧠", layout="wide")

if "stage" not in st.session_state:
    st.session_state.stage = "dashboard"
if "tasks" not in st.session_state:
    st.session_state.tasks = []
if "error" not in st.session_state:
    st.session_state.error = None
if "location_filter" not in st.session_state:
    st.session_state.location_filter = ""
if "source_filter" not in st.session_state:
    st.session_state.source_filter = "All"

if st.session_state.stage == "dashboard":
    src.ui.dashboard_page.show_dashboard_page()
elif st.session_state.stage == "results":
    src.ui.results_page.show_results_page()
