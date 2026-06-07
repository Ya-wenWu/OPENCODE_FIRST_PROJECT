import pytest
from agentic_workflow.core.schemas import ToolDef
from agentic_workflow.core.tool_registry import ToolRegistry


def dummy_fn(arg: str = "") -> str:
    return f"executed {arg}"


def failing_fn() -> str:
    raise RuntimeError("oops")


@pytest.fixture
def registry():
    reg = ToolRegistry()
    tool = ToolDef(
        name="dummy",
        description="A dummy tool",
        parameters={
            "type": "object",
            "properties": {
                "arg": {"type": "string", "description": "an argument"}
            },
        },
    )
    reg.register(tool, dummy_fn)
    return reg


def test_register_and_execute(registry):
    result = registry.execute("dummy", {"arg": "hello"})
    assert result.success is True
    assert result.output == "executed hello"


def test_unknown_tool(registry):
    result = registry.execute("nope", {})
    assert result.success is False
    assert "Unknown tool" in result.error


def test_execute_failure(registry):
    registry._tools["dummy"]["fn"] = failing_fn
    result = registry.execute("dummy", {})
    assert result.success is False
    assert result.error == "oops"


def test_get_openai_schemas(registry):
    schemas = registry.get_openai_schemas()
    assert len(schemas) == 1
    assert schemas[0]["type"] == "function"
    assert schemas[0]["function"]["name"] == "dummy"


def test_tool_names(registry):
    assert registry.tool_names == ["dummy"]
