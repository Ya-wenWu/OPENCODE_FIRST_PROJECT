from agentic_workflow.core.schemas import ToolDef, ToolResult, AgentState


def test_tool_def_creation():
    tool = ToolDef(
        name="test_tool",
        description="A test tool",
        parameters={"type": "object", "properties": {}},
    )
    assert tool.name == "test_tool"
    assert tool.description == "A test tool"


def test_tool_result_success():
    r = ToolResult(success=True, output="ok")
    assert r.success is True
    assert r.output == "ok"
    assert r.error is None


def test_tool_result_error():
    r = ToolResult(success=False, error="something broke")
    assert r.success is False
    assert r.error == "something broke"


def test_agent_state_defaults():
    s = AgentState(task="do something")
    assert s.task == "do something"
    assert s.iteration == 0
    assert s.max_iterations == 10
    assert s.done is False
    assert s.result is None
    assert s.loop_detected is False


def test_agent_state_custom_max_iter():
    s = AgentState(task="test", max_iterations=5)
    assert s.max_iterations == 5
