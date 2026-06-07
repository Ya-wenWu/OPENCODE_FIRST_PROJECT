from agentic_workflow.tools.bash import bash


def test_bash_echo():
    result = bash('echo "hello"')
    assert result == "hello"


def test_bash_pwd():
    result = bash("pwd")
    assert result.startswith("/")


def test_bash_exit_code():
    result = bash("false")
    assert "[exit code: 1]" in result


def test_bash_exit_code_nonzero():
    result = bash("exit 42")
    assert "[exit code: 42]" in result
