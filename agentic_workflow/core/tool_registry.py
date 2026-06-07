import json

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

    def _validate_args(self, args: dict, parameters: dict) -> str | None:
        properties = parameters.get("properties", {})
        required = parameters.get("required", [])

        for key in required:
            if key not in args:
                return f"Missing required argument: '{key}'"

        for key in args:
            if key not in properties:
                return f"Unknown argument: '{key}'"

        return None

    def execute(self, name: str, args: dict) -> ToolResult:
        entry = self._tools.get(name)
        if not entry:
            return ToolResult(success=False, error=f"Unknown tool: {name}")

        error = self._validate_args(args, entry["def"].parameters)
        if error:
            return ToolResult(success=False, error=error)

        try:
            result = entry["fn"](**args)
            if isinstance(result, (dict, list)):
                output = json.dumps(result, ensure_ascii=False)
            else:
                output = str(result)
            return ToolResult(success=True, output=output)
        except Exception as e:
            return ToolResult(success=False, error=str(e))

    @property
    def tool_names(self) -> list[str]:
        return list(self._tools.keys())
