import json
from typing import Dict, Any
from src.tools.task_tools import fetch_all_tasks
from src.memory.task_store import get_tasks

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "fetch_all_tasks",
            "description": "Fetches all pending tasks from connected integrations (Gmail, Notion) and returns them as a combined list.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []}}},
    {
        "type": "function",
        "function": {
            "name": "get_task_details",
            "description": "Retrieves the full details of a specific task from the memory store using its index.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_index": {
                        "type": "integer",
                        "description": "The zero-based index of the task to retrieve."}},
                "required": ["task_index"]}}}]


def execute_tool(tool_name: str, args: Dict[str, Any]) -> str:
    print(f"Executing tool: {tool_name} with arguments: {args}")

    try:
        if tool_name == "fetch_all_tasks":
            # Call the function from task_tools
            tasks = fetch_all_tasks()
            return json.dumps(tasks, default=str)

        elif tool_name == "get_task_details":
            # Fetch from task_store
            task_index = args.get("task_index")
            if task_index is None:
                return json.dumps(
                    {"error": "Missing required argument 'task_index'"})

            tasks = get_tasks()

            if not isinstance(
                    task_index,
                    int) or task_index < 0 or task_index >= len(tasks):
                return json.dumps(
                    {"error": f"Invalid task_index: {task_index}. Out of bounds."})

            task = tasks[task_index]
            return json.dumps(task, default=str)

        else:
            return json.dumps(
                {"error": f"Tool '{tool_name}' is not recognized."})

    except Exception as e:
        return json.dumps(
            {"error": f"Error executing tool {tool_name}: {str(e)}"})
