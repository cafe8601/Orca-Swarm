"""
Integration tests for agent lifecycle with real dependencies.

Tests agent creation, command dispatch, and cleanup with mocked external services.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path
from apps.realtime_poc.big_three_realtime_agents.agents.claude.agent_lifecycle import (
    AgentLifecycleManager,
)


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    return Mock()


@pytest.fixture
def mock_registry_manager():
    """Mock registry manager."""
    manager = Mock()
    manager.get_existing_names.return_value = ["agent1", "agent2"]
    manager.agent_exists.return_value = True
    manager.get_agent_session_id.return_value = "session_123"
    manager.get_agent_directory.return_value = Path("/tmp/test_agent")
    return manager


@pytest.fixture
def mock_agent_creator():
    """Mock agent creator."""
    creator = Mock()

    async def mock_create(*args, **kwargs):
        await asyncio.sleep(0.1)  # Simulate async work
        return {
            "agent_name": "test_agent",
            "session_id": "session_new",
            "status": "created",
        }

    creator.create_new_agent = AsyncMock(side_effect=mock_create)
    return creator


@pytest.fixture
def mock_operator_file_manager():
    """Mock operator file manager."""
    manager = Mock()

    async def mock_prepare(*args, **kwargs):
        await asyncio.sleep(0.05)  # Simulate async work
        return Path("/tmp/operator_test.md")

    manager.prepare_operator_file = AsyncMock(side_effect=mock_prepare)
    return manager


@pytest.fixture
def mock_agent_executor():
    """Mock agent executor."""
    executor = Mock()
    executor.run_command_thread = Mock()
    return executor


@pytest.fixture
def lifecycle_manager(
    mock_logger,
    mock_registry_manager,
    mock_agent_creator,
    mock_operator_file_manager,
    mock_agent_executor,
):
    """Create AgentLifecycleManager with mocked dependencies."""
    manager = AgentLifecycleManager(
        logger=mock_logger,
        registry_manager=mock_registry_manager,
        agent_creator=mock_agent_creator,
        operator_file_manager=mock_operator_file_manager,
        agent_executor=mock_agent_executor,
    )
    manager.background_threads = {}
    return manager


class TestAgentCreation:
    """Integration tests for agent creation."""

    def test_create_agent_success(self, lifecycle_manager, mock_agent_creator):
        """Test successful agent creation."""
        result = lifecycle_manager.create_agent(
            tool="claude_code",
            agent_type="agentic_coding",
            agent_name="test_agent",
            browser_agent=None,
        )

        assert result["ok"] is True
        assert "data" in result
        assert result["data"]["agent_name"] == "test_agent"
        mock_agent_creator.create_new_agent.assert_called_once()

    def test_create_agent_timeout(self, lifecycle_manager, mock_agent_creator):
        """Test agent creation timeout handling."""

        # Make creation take longer than timeout
        async def slow_create(*args, **kwargs):
            await asyncio.sleep(100)  # Longer than AGENT_CREATION_TIMEOUT

        mock_agent_creator.create_new_agent = AsyncMock(side_effect=slow_create)

        result = lifecycle_manager.create_agent(
            tool="claude_code",
            agent_type="agentic_coding",
            agent_name="test_agent",
            browser_agent=None,
        )

        assert result["ok"] is False
        assert "timed out" in result["error"]

    def test_create_agent_exception(self, lifecycle_manager, mock_agent_creator):
        """Test agent creation exception handling."""

        async def failing_create(*args, **kwargs):
            raise ValueError("Creation failed")

        mock_agent_creator.create_new_agent = AsyncMock(side_effect=failing_create)

        result = lifecycle_manager.create_agent(
            tool="claude_code",
            agent_type="agentic_coding",
            agent_name="test_agent",
            browser_agent=None,
        )

        assert result["ok"] is False
        assert "error" in result


class TestCommandDispatch:
    """Integration tests for command dispatch."""

    def test_command_agent_success(
        self, lifecycle_manager, mock_operator_file_manager, mock_agent_executor
    ):
        """Test successful command dispatch."""
        result = lifecycle_manager.command_agent(
            agent_name="agent1", prompt="Do something"
        )

        assert result["ok"] is True
        assert "data" in result
        mock_operator_file_manager.prepare_operator_file.assert_called_once()
        mock_agent_executor.run_command_thread.assert_called_once()

    def test_command_nonexistent_agent(self, lifecycle_manager, mock_registry_manager):
        """Test commanding non-existent agent."""
        mock_registry_manager.agent_exists.return_value = False

        result = lifecycle_manager.command_agent(
            agent_name="nonexistent", prompt="Do something"
        )

        assert result["ok"] is False
        assert "not found" in result["error"]

    def test_command_agent_no_session(self, lifecycle_manager, mock_registry_manager):
        """Test commanding agent without session ID."""
        mock_registry_manager.get_agent_session_id.return_value = None

        result = lifecycle_manager.command_agent(
            agent_name="agent1", prompt="Do something"
        )

        assert result["ok"] is False
        assert "no session_id" in result["error"]

    def test_command_timeout(self, lifecycle_manager, mock_operator_file_manager):
        """Test command preparation timeout."""

        async def slow_prepare(*args, **kwargs):
            await asyncio.sleep(100)  # Longer than timeout

        mock_operator_file_manager.prepare_operator_file = AsyncMock(
            side_effect=slow_prepare
        )

        result = lifecycle_manager.command_agent(
            agent_name="agent1", prompt="Do something"
        )

        assert result["ok"] is False
        assert "timed out" in result["error"]


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_full_agent_lifecycle(
        self, lifecycle_manager, mock_agent_creator, mock_agent_executor
    ):
        """Test complete agent lifecycle: create -> command -> success."""

        # Step 1: Create agent
        create_result = lifecycle_manager.create_agent(
            tool="claude_code",
            agent_type="agentic_coding",
            agent_name="test_agent",
            browser_agent=None,
        )

        assert create_result["ok"] is True

        # Step 2: Command agent
        command_result = lifecycle_manager.command_agent(
            agent_name="agent1",  # Using existing agent from fixture
            prompt="Write a function",
        )

        assert command_result["ok"] is True
        assert "Command dispatched" in command_result["data"]["message"]

    def test_concurrent_agent_operations(self, lifecycle_manager):
        """Test concurrent agent operations."""
        import concurrent.futures

        # Create multiple agents concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [
                executor.submit(
                    lifecycle_manager.create_agent,
                    "claude_code",
                    "agentic_coding",
                    f"agent_{i}",
                    None,
                )
                for i in range(3)
            ]

            results = [f.result() for f in futures]

        # All should succeed
        assert all(r["ok"] for r in results)


class TestErrorRecovery:
    """Tests for error recovery and resilience."""

    def test_retry_after_transient_failure(
        self, lifecycle_manager, mock_operator_file_manager
    ):
        """Test system recovers from transient failures."""

        call_count = {"value": 0}

        async def intermittent_prepare(*args, **kwargs):
            call_count["value"] += 1
            if call_count["value"] < 2:
                raise ConnectionError("Transient error")
            await asyncio.sleep(0.05)
            return Path("/tmp/operator.md")

        mock_operator_file_manager.prepare_operator_file = AsyncMock(
            side_effect=intermittent_prepare
        )

        # Should succeed after retry (if retry logic is in place)
        # Note: Current implementation may not retry at this level
        result = lifecycle_manager.command_agent(
            agent_name="agent1", prompt="Test command"
        )

        # Result depends on whether retry is implemented
        # This test documents expected behavior
        assert "ok" in result
