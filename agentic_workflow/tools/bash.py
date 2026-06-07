import subprocess

from agentic_workflow.core.schemas import ToolDef


def bash(command: str, workdir: str = "") -> str:
    cwd = workdir or None
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=cwd,
        )
        output = result.stdout
        if result.stderr:
            output += f"\n[stderr]\n{result.stderr}"
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "ERROR: Command timed out after 30s"
    except Exception as e:
        return f"ERROR: {e}"


BASH_TOOL = ToolDef(
    name="bash",
    description="Execute a shell command. Use for running scripts, compiling, testing.",
    parameters={
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute",
            },
            "workdir": {
                "type": "string",
                "description": "Working directory (optional)",
            },
        },
        "required": ["command"],
    },
)
