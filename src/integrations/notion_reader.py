import os
from notion_client import Client
from notion_client.errors import APIResponseError


def fetch_notion_tasks():
    notion_api_key = os.environ.get("NOTION_API_KEY")
    database_id = os.environ.get("NOTION_DATABASE_ID")

    if not notion_api_key or not database_id:
        print("Warning: Notion API Key or Database ID not found in environment.")
        return []

    notion = Client(auth=notion_api_key)

    tasks = []
    try:
        # Querying pages where Status is not Done and not Archived
        # We assume the property is named "Status" and is of type "status"
        query_filter = {
            "and": [
                {
                    "property": "Status",
                    "status": {
                        "does_not_equal": "Done"
                    }
                },
                {
                    "property": "Status",
                    "status": {
                        "does_not_equal": "Archived"
                    }
                }
            ]
        }

        results = notion.databases.query(
            **{
                "database_id": database_id,
                "filter": query_filter
            }
        ).get("results")

        for page in results:
            properties = page.get("properties", {})

            # Extract title dynamically based on type 'title'
            title = "Untitled"
            for prop_name, prop_data in properties.items():
                if prop_data.get("type") == "title":
                    title_parts = prop_data.get("title", [])
                    if title_parts:
                        title = "".join([t.get("plain_text", "")
                                        for t in title_parts])
                    break

            # Extract due date based on type 'date'
            due_date = None
            for prop_name, prop_data in properties.items():
                if prop_data.get("type") == "date" and prop_data.get("date"):
                    due_date = prop_data.get("date").get("start")
                    break

            # Extract priority based on type 'select' or 'status'
            priority = None
            for prop_name, prop_data in properties.items():
                if prop_name.lower() == "priority":
                    if prop_data.get(
                            "type") == "select" and prop_data.get("select"):
                        priority = prop_data["select"].get("name")
                    elif prop_data.get("type") == "status" and prop_data.get("status"):
                        priority = prop_data["status"].get("name")
                    break

            tasks.append({
                "source": "notion",
                "title": title,
                "due_date": due_date,
                "priority": priority,
                "url": page.get("url")
            })

        print(f"Found {len(tasks)} Notion tasks.")
        return tasks

    except APIResponseError as e:
        print(f"Warning: Notion API error - {e}")
        return []
    except Exception as e:
        print(f"Warning: Unexpected error fetching from Notion - {e}")
        return []
