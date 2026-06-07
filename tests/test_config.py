from agentic_workflow.config import Settings


def test_settings_defaults():
    s = Settings()
    assert s.model == "deepseek-ai/deepseek-v4-flash"
    assert s.base_url == "https://integrate.api.nvidia.com/v1"
    assert s.max_iterations == 10
    assert s.temperature == 0.1


def test_settings_api_key_from_env(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "test-key-123")
    s = Settings(nvidia_api_key="")
    assert s.api_key == "test-key-123"


def test_settings_api_key_direct():
    s = Settings(nvidia_api_key="direct-key")
    assert s.api_key == "direct-key"


def test_settings_api_key_precedence(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "env-key")
    s = Settings(nvidia_api_key="direct-key")
    assert s.api_key == "direct-key"
