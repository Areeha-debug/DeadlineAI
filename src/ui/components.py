import streamlit as st


def show_header():
    st.title("🧠 Deadline ai")
    st.markdown("*Your tasks, unified and prioritized by AI*")
    st.divider()


def show_error():
    if st.session_state.get("error"):
        st.error(st.session_state["error"])
        if st.button("Dismiss Error"):
            st.session_state["error"] = None
            st.rerun()


def show_task_card(task: dict, index: int):
    with st.container():
        priority = str(task.get("priority", "LOW")).upper()
        if priority == "HIGH":
            color = "#ff4b4b"
        elif priority == "MEDIUM":
            color = "#ffa421"
        else:
            color = "#00c04b"

        badge_html = f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 0.8em;">{priority}</span>'

        # Source icon
        source = str(task.get("source", "")).lower()
        if source == "gmail":
            icon = "📧"
        elif source == "notion":
            icon = "📝"
        elif source == "voice":
            icon = "🎤"
        else:
            icon = "❓"

        st.markdown(
            f"{badge_html} &nbsp;&nbsp; {icon} **Source: {
                source.capitalize()}**",
            unsafe_allow_html=True)
        st.subheader(task.get("title", "Untitled Task"))

        action_summary = task.get("action_summary")
        if action_summary:
            st.markdown(f"*{action_summary}*")
        else:
            description = task.get("description")
            if description:
                st.markdown(f"*{description}*")

        due_date = task.get("due_date")
        if due_date:
            st.write(f"**Due Date:** {due_date}")

        url = task.get("url")
        if url:
            st.link_button("Open Task", url)

        st.markdown("---")


def show_source_legend():
    st.markdown("**Legend:** 📧 Gmail | 📝 Notion | 🎤 Voice")
