import datetime
from typing import List, Dict, Any
from src.integrations import fetch_gmail_tasks, fetch_notion_tasks


def fetch_all_tasks() -> List[Dict[str, Any]]:
    print("Fetching tasks from Gmail and Notion...")
    gmail_tasks = fetch_gmail_tasks()
    notion_tasks = fetch_notion_tasks()

    combined_tasks = gmail_tasks + notion_tasks

    print(f"Total tasks fetched: {len(combined_tasks)}")
    print(
        f"Breakdown: {
            len(gmail_tasks)} from Gmail, {
            len(notion_tasks)} from Notion")

    return combined_tasks


def prioritize_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    now = datetime.datetime.now()
    now_utc = datetime.datetime.now(datetime.timezone.utc)

    for task in tasks:
        # Rule 1: Check existing priority from Notion
        existing_priority = task.get("priority")
        if existing_priority and isinstance(existing_priority, str):
            ep_upper = existing_priority.upper()
            if "HIGH" in ep_upper or "URGENT" in ep_upper:
                task["priority"] = "HIGH"
                continue

        # Rule 2 & 3: Check due dates
        due_date_str = task.get("due_date")
        assigned_priority = "LOW"

        if due_date_str:
            try:
                # Notion date format is typically ISO 8601 YYYY-MM-DD or
                # YYYY-MM-DDTHH:MM:SS
                if "T" in due_date_str:
                    try:
                        due_date = datetime.datetime.fromisoformat(
                            due_date_str.replace("Z", "+00:00"))
                        ref_time = now_utc if due_date.tzinfo else now
                    except ValueError:
                        due_date = None
                else:
                    due_date = datetime.datetime.strptime(
                        due_date_str, "%Y-%m-%d").date()
                    ref_time = now.date()

                if due_date:
                    if isinstance(
                            due_date,
                            datetime.datetime) and isinstance(
                            ref_time,
                            datetime.datetime):
                        delta = due_date - ref_time
                    else:
                        # both are date objects
                        delta = due_date - ref_time

                    # Calculate total days diff
                    delta_days = delta.days + \
                        (delta.seconds / 86400.0) if hasattr(delta, "seconds") else delta.days

                    if delta_days <= 1:
                        assigned_priority = "HIGH"
                    elif delta_days <= 3:
                        assigned_priority = "MEDIUM"
            except Exception as e:
                print(f"Warning: Failed to parse date {due_date_str} - {e}")

        task["priority"] = assigned_priority

    # Sort tasks by priority: HIGH -> MEDIUM -> LOW
    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
    tasks.sort(key=lambda x: priority_order.get(x.get("priority", "LOW"), 2))

    return tasks
