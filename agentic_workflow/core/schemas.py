from pydantic import BaseModel, Field
from typing import Any


class ToolDef(BaseModel):
    name: str = Field(description="Tool name used in function calls")
    description: str = Field(description="What the tool does")
    parameters: dict[str, Any] = Field(description="JSON Schema for tool arguments")


class ToolResult(BaseModel):
    success: bool
    output: str = ""
    error: str | None = None


class AgentState(BaseModel):
    task: str
    messages: list[dict] = []
    iteration: int = 0
    max_iterations: int = 10
    done: bool = False
    result: str | None = None
    last_action: Any = None
    action_count: int = 0
