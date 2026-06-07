import sys

from agentic_workflow.config import settings
from agentic_workflow.core.tool_registry import ToolRegistry
from agentic_workflow.core.agent_loop import run_task
from agentic_workflow.tools.bash import bash, BASH_TOOL
from agentic_workflow.tools.filesystem import read_file, write_file, READ_TOOL, WRITE_TOOL


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m agentic_workflow.cli \"your task description\"")
        print("Example: python -m agentic_workflow.cli \"write a python calculator\"")
        sys.exit(1)

    task = " ".join(sys.argv[1:])

    if not settings.api_key:
        print("ERROR: NVIDIA_API_KEY not set")
        print("Set it: export NVIDIA_API_KEY=nvapi-...")
        sys.exit(1)

    registry = ToolRegistry()
    registry.register(BASH_TOOL, bash)
    registry.register(READ_TOOL, read_file)
    registry.register(WRITE_TOOL, write_file)

    print(f" Model: {settings.model}")
    print(f" Max iterations: {settings.max_iterations}")
    print(f" Task: {task}")
    print("=" * 50)

    result = run_task(task, registry)

    print("=" * 50)
    print(" RESULT")
    print("=" * 50)
    print(result)


if __name__ == "__main__":
    main()
