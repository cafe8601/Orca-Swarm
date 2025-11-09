"""
Agent execution logic for Claude Code agents.

Handles command threading and agent query execution.
"""

import threading
import logging
from typing import Dict, Any

from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient, AssistantMessage, TextBlock

from ...config import DEFAULT_CLAUDE_MODEL, AGENT_WORKING_DIRECTORY


class AgentExecutor:
    """Handles Claude Code agent command execution."""

    def __init__(self, logger: logging.Logger):
        """
        Initialize agent executor.

        Args:
            logger: Logger instance.
        """
        self.logger = logger

    def run_command_thread(
        self,
        agent_name: str,
        session_id: str,
        prompt: str,
        operator_file_path: str,
        background_threads: list,
    ):
        """
        Run agent command in background thread.

        Args:
            agent_name: Name of the agent.
            session_id: Session ID.
            prompt: Command prompt.
            operator_file_path: Path to operator file.
            background_threads: List to track background threads.
        """

        def thread_func():
            import asyncio

            try:
                asyncio.run(
                    self._run_existing_agent_async(
                        agent_name, session_id, prompt, operator_file_path
                    )
                )
            except Exception as e:
                self.logger.error(f"Background agent thread failed: {e}")

        t = threading.Thread(target=thread_func, daemon=True)
        t.start()
        background_threads.append(t)
        self.logger.info(
            f"Started background command for '{agent_name}' - check status with check_agent_result"
        )

    async def _run_existing_agent_async(
        self, agent_name: str, session_id: str, prompt: str, operator_file_path: str
    ):
        """
        Run existing agent asynchronously.

        Args:
            agent_name: Name of the agent.
            session_id: Session ID.
            prompt: Command prompt.
            operator_file_path: Path to operator file.
        """
        options = ClaudeAgentOptions(
            model=DEFAULT_CLAUDE_MODEL,
            cwd=str(AGENT_WORKING_DIRECTORY),
            session_id=session_id,
        )

        full_prompt = f"{prompt}\n\nIMPORTANT: Log all your work and results to: {operator_file_path}"

        try:
            async with ClaudeSDKClient(options=options) as client:
                await client.query(full_prompt)

                async for message in client.receive_response():
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                self.logger.info(f"[{agent_name}] {block.text}")
        except Exception as exc:
            self.logger.error(f"Agent execution failed: {exc}")

    async def collect_text_from_query(self, prompt: str) -> str:
        """
        Collect text response from Claude query.

        Args:
            prompt: Query prompt.

        Returns:
            Collected text response.
        """
        from claude_agent_sdk import query

        options = ClaudeAgentOptions(model="claude-3-5-haiku-20241022")
        chunks = []
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        chunks.append(block.text)
        return "".join(chunks).strip()
