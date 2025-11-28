"""
Pytest configuration and shared fixtures for Big Three Agents testing.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock
import asyncio

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_addoption(parser):
    """Add custom pytest command line options."""
    parser.addoption(
        "--run-expensive",
        action="store_true",
        default=False,
        help="run expensive tests that incur API costs"
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_openai_api_key(monkeypatch):
    """Mock OpenAI API key for testing."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-1234567890")
    return "sk-test-key-1234567890"


@pytest.fixture
def mock_anthropic_api_key(monkeypatch):
    """Mock Anthropic API key for testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-key-1234567890")
    return "sk-ant-test-key-1234567890"


@pytest.fixture
def mock_gemini_api_key(monkeypatch):
    """Mock Gemini API key for testing."""
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key-1234567890")
    return "test-gemini-key-1234567890"


@pytest.fixture
def all_api_keys(mock_openai_api_key, mock_anthropic_api_key, mock_gemini_api_key):
    """Mock all API keys together."""
    return {
        "OPENAI_API_KEY": mock_openai_api_key,
        "ANTHROPIC_API_KEY": mock_anthropic_api_key,
        "GEMINI_API_KEY": mock_gemini_api_key,
    }


@pytest.fixture
def temp_working_dir(tmp_path):
    """Create temporary working directory for agent tests."""
    working_dir = tmp_path / "agent_working_dir"
    working_dir.mkdir()
    return working_dir


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection for OpenAI Realtime API."""
    ws = AsyncMock()
    ws.send = AsyncMock()
    ws.recv = AsyncMock()
    ws.close = AsyncMock()
    return ws


@pytest.fixture
def mock_playwright_browser():
    """Mock Playwright browser for Gemini agent testing."""
    browser = AsyncMock()
    page = AsyncMock()

    # Setup page mock
    page.goto = AsyncMock()
    page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")
    page.click = AsyncMock()
    page.type = AsyncMock()
    page.evaluate = AsyncMock()
    page.wait_for_selector = AsyncMock()
    page.wait_for_load_state = AsyncMock()
    page.set_viewport_size = AsyncMock()

    # Setup browser mock
    browser.new_page = AsyncMock(return_value=page)
    browser.close = AsyncMock()

    return browser, page


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for Claude agent testing."""
    client = Mock()
    client.messages = Mock()
    client.messages.create = AsyncMock()
    return client


@pytest.fixture
def mock_gemini_model():
    """Mock Google Gemini model for browser agent testing."""
    model = Mock()
    response = Mock()
    response.text = '{"action": "click", "selector": "#test-button"}'
    model.generate_content = Mock(return_value=response)
    return model


@pytest.fixture
def sample_agent_task():
    """Sample task for agent testing."""
    return {
        "task": "Create a simple Python hello world script",
        "working_dir": "/tmp/test",
        "expected_output": "print('Hello, World!')",
    }


@pytest.fixture
def sample_browser_task():
    """Sample browser automation task."""
    return {
        "task": "Navigate to example.com and click the login button",
        "url": "https://example.com",
        "expected_action": "click",
    }


@pytest.fixture(autouse=True)
def reset_config_cache():
    """Reset configuration cache between tests."""
    import importlib
    from apps.realtime_poc.big_three_realtime_agents import config
    importlib.reload(config)
    yield
    importlib.reload(config)
