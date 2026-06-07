import tempfile
from pathlib import Path

from agentic_workflow.tools.filesystem import read_file, write_file


def test_write_and_read_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "test.txt")
        result = write_file(path, "hello world")
        assert "Written" in result
        assert "test.txt" in result

        content = read_file(path)
        assert content == "hello world"


def test_read_nonexistent_file():
    result = read_file("/tmp/nonexistent_file_xyz.txt")
    assert "ERROR" in result
    assert "not found" in result


def test_write_creates_parent_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "sub" / "nested" / "file.txt")
        result = write_file(path, "nested")
        assert "Written" in result
        assert Path(path).exists()


def test_read_empty_file():
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "empty.txt")
        write_file(path, "")
        content = read_file(path)
        assert content == ""
