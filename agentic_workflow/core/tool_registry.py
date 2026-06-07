from agentic_workflow.core.schemas import ToolDef, ToolResult


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, dict] = {}

    def register(self, tool: ToolDef, fn: callable):
        self._tools[tool.name] = {
            "def": tool,
            "fn": fn,
            "openai_schema": {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            },
        }

    def get_openai_schemas(self) -> list[dict]:
        return [t["openai_schema"] for t in self._tools.values()]

    def execute(self, name: str, args: dict) -> ToolResult:
        entry = self._tools.get(name)
        if not entry:
            return ToolResult(success=False, error=f"Unknown tool: {name}")
        try:
            result = entry["fn"](**args)
            return ToolResult(success=True, output=str(result))
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())
