from pathlib import Path

from agentic_workflow.core.schemas import ToolDef


def read_file(path: str) -> str:
    try:
        p = Path(path).resolve()
        if not p.exists():
            return f"ERROR: File not found: {path}"
        return p.read_text(encoding="utf-8")
    except Exception as e:
        return f"ERROR: {e}"


def write_file(path: str, content: str) -> str:
    try:
        p = Path(path).resolve()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"Written {len(content)} bytes to {path}"
    except Exception as e:
        return f"ERROR: {e}"


READ_TOOL = ToolDef(
    name="read",
    description="Read a file from the filesystem.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute or relative path to the file",
            },
        },
        "required": ["path"],
    },
)

WRITE_TOOL = ToolDef(
    name="write",
    description="Write content to a file (creates parent dirs if needed).",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Absolute or relative path to the file",
            },
            "content": {
                "type": "string",
                "description": "File content to write",
            },
        },
        "required": ["path", "content"],
    },
)
