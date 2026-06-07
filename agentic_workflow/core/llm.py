import json
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from agentic_workflow.config import settings


class LLMError(Exception):
    pass


class LLMResponse:
    def __init__(self, content: str, tool_calls: list[dict] | None = None):
        self.content = content
        self.tool_calls = tool_calls or []


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(min=2, max=15),
    retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException)),
)
def chat(
    messages: list[dict],
    tools: list[dict] | None = None,
) -> LLMResponse:
    api_key = settings.api_key
    if not api_key:
        raise LLMError("NVIDIA_API_KEY not set")

    body: dict = {
        "model": settings.model,
        "messages": messages,
        "temperature": settings.temperature,
        "max_tokens": 4096,
    }
    if tools:
        body["tools"] = tools
        body["tool_choice"] = "auto"

    with httpx.Client(timeout=60) as client:
        resp = client.post(
            f"{settings.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
        )
        resp.raise_for_status()
        data = resp.json()

    choice = data["choices"][0]
    msg = choice["message"]

    content = msg.get("content", "")
    tool_calls_raw = msg.get("tool_calls")

    tool_calls = []
    if tool_calls_raw:
        for tc in tool_calls_raw:
            args = tc["function"]["arguments"]
            if isinstance(args, str):
                args = json.loads(args)
            tool_calls.append({
                "id": tc["id"],
                "name": tc["function"]["name"],
                "arguments": args,
            })

    return LLMResponse(content=content, tool_calls=tool_calls)
