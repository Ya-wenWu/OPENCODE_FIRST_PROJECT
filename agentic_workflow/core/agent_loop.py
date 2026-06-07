import json

from agentic_workflow.config import settings
from agentic_workflow.core.schemas import AgentState
from agentic_workflow.core.llm import chat
from agentic_workflow.core.tool_registry import ToolRegistry

SYSTEM_PROMPT = """You are an autonomous coding agent. You have tools to help you:
- Use tools when you need to read files, write code, or run commands.
- After using a tool, analyze the result and decide what to do next.
- When the task is complete, provide a clear summary of what was done.
- Never repeat the same action with the same arguments more than once.
- If a tool fails, try a different approach."""

MAX_TASK_LENGTH = 32_768
MAX_MESSAGES = 30


def run_task(task: str, registry: ToolRegistry) -> str:
    if not task.strip():
        return "Task cannot be empty."
    if len(task) > MAX_TASK_LENGTH:
        task = task[:MAX_TASK_LENGTH] + "\n\n[TRUNCATED]"

    state = AgentState(
        task=task,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                   {"role": "user", "content": task}],
        max_iterations=settings.max_iterations,
    )

    while not state.done and state.iteration < state.max_iterations:
        state.iteration += 1

        try:
            response = chat(state.messages, tools=registry.get_openai_schemas())
        except Exception as e:
            state.done = True
            state.result = f"LLM call failed after retries: {e}"
            break

        if response.tool_calls:
            state.messages.append({
                "role": "assistant",
                "content": response.content or "",
                "tool_calls": [
                    {"id": tc["id"], "type": "function",
                     "function": {"name": tc["name"], "arguments": json.dumps(tc["arguments"])}}
                    for tc in response.tool_calls
                ],
            })

            for tc in response.tool_calls:
                action_key = (tc["name"], json.dumps(tc["arguments"], sort_keys=True))
                if action_key == state.last_action:
                    state.action_count += 1
                else:
                    state.last_action = action_key
                    state.action_count = 1

                if state.action_count >= 3:
                    state.messages.append({
                        "role": "tool",
                        "tool_call_id": tc["id"],
                        "content": "ERROR: Repeated same action 3 times. Provide final answer.",
                    })
                    continue

                result = registry.execute(tc["name"], tc["arguments"])
                if result.success:
                    content = result.model_dump_json()
                else:
                    content = f"TOOL_ERROR: {result.error}"
                state.messages.append({
                    "role": "tool",
                    "tool_call_id": tc["id"],
                    "content": content,
                })
        else:
            state.result = response.content
            state.done = True

        if len(state.messages) > MAX_MESSAGES:
            system = state.messages[0]
            user = state.messages[1]
            recent = state.messages[-(MAX_MESSAGES - 2):]
            state.messages = [system, user] + recent

    if not state.done:
        state.result = f"Reached max iterations ({state.max_iterations}). Progress above."

    return state.result or "No result produced."
