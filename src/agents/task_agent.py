import os
import json
from openai import OpenAI
from src.tools.task_tools import fetch_all_tasks, prioritize_tasks
from src.memory.task_store import save_tasks
from src.tools.tool_registry import TOOL_DEFINITIONS, execute_tool


def run_agent():
    print("Starting task agent...")

    # Fetch raw tasks
    raw_tasks = fetch_all_tasks()
    if not raw_tasks:
        print("No tasks found from any source.")
        return []

    # Pre-sort tasks
    presorted_tasks = prioritize_tasks(raw_tasks)

    # Save pre-sorted tasks to store
    save_tasks(presorted_tasks)
    print("Saved pre-sorted tasks to memory store.")

    system_prompt = """You are a smart task prioritization assistant.
Your job is to process a JSON list of tasks from multiple sources (Gmail, Notion, Voice).
Follow these rules strictly:
1. Deduplicate tasks that appear to describe the same action, even if worded differently.
2. Assign a final priority of HIGH, MEDIUM, or LOW to each task based on:
   - Deadline urgency
   - Sender importance signals (e.g., words like "urgent", "ASAP", "deadline", "by EOD")
   - Notion priority field values
   - Task source (voice tasks from managers are likely urgent)
3. Write a one-sentence action summary for each task in plain English starting with a verb (e.g. "Submit the Q3 report to the finance team by Friday").
4. Return ONLY a raw JSON array of the processed tasks with no markdown formatting and no explanation.

Each item in the returned array must strictly contain these keys:
- source (string)
- title (string)
- action_summary (string)
- priority (string: HIGH, MEDIUM, or LOW)
- due_date (string or null)
- sender (string or null)
- url (string or null)"""

    user_message = f"""Here is the pre-sorted task list in JSON format:
{json.dumps(presorted_tasks, default=str)}

Please begin deduplication and prioritization immediately."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    openai_api_key = os.environ.get("OPENAI_API_KEY")
    client = OpenAI(api_key=openai_api_key)
    max_iterations = 10

    for i in range(max_iterations):
        print(f"Agent loop iteration {i + 1}/{max_iterations}")

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=0.2
        )

        message = response.choices[0].message
        messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args_str = tool_call.function.arguments
                print(
                    f"Agent requested tool call: {tool_name} with args: {tool_args_str}")

                try:
                    tool_args = json.loads(tool_args_str)
                except json.JSONDecodeError:
                    tool_args = {}

                tool_result = execute_tool(tool_name, tool_args)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })
        else:
            final_content = message.content or ""
            print("Agent returned final response.")

            # Strip markdown fencing if present
            cleaned_content = final_content.strip()
            if cleaned_content.startswith("```json"):
                cleaned_content = cleaned_content[7:]
            elif cleaned_content.startswith("```"):
                cleaned_content = cleaned_content[3:]
            if cleaned_content.endswith("```"):
                cleaned_content = cleaned_content[:-3]

            cleaned_content = cleaned_content.strip()

            try:
                final_tasks = json.loads(cleaned_content)
                save_tasks(final_tasks)
                print(f"Saved {len(final_tasks)} prioritized tasks to store.")
                return final_tasks
            except json.JSONDecodeError as e:
                print(
                    f"Failed to parse final JSON response: {e}\nResponse was: {final_content}")
                return presorted_tasks  # fallback

    raise RuntimeError(
        "Agent reached maximum iterations without returning a final response.")
