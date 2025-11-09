"""
Tool creation for Claude Code agents.

Handles browser_use tool creation with agent-specific screenshot management.
"""

import asyncio
import concurrent.futures
import uuid
import logging
from datetime import datetime
from typing import Any

from claude_agent_sdk import tool

from ...config import AGENTS_BASE_DIR, CLAUDE_CODE_TOOL_SLUG


def create_browser_tool(agent_name: str, browser_agent, logger: logging.Logger):
    """
    Create browser_use tool for Claude agents with agent-specific screenshot directory.

    Args:
        agent_name: Name of the agent using this tool.
        browser_agent: GeminiBrowserAgent instance.
        logger: Logger instance.

    Returns:
        Configured browser_use tool function.
    """

    @tool(
        "browser_use",
        "Automate web validation tasks. Use this to validate your frontend work. "
        "Can navigate websites, interact with web pages, extract data, confirm (or reject) "
        "the work is done correctly, and perform complex multi-step validation tasks.",
        {"task": str, "url": str},
    )
    async def browser_use_tool(args: dict[str, Any]) -> dict[str, Any]:
        """Execute browser automation task with agent-specific screenshot storage."""
        task = args.get("task", "")
        url = args.get("url")

        if not browser_agent:
            return {
                "content": [
                    {"type": "text", "text": "Browser agent not available."}
                ],
                "isError": True,
            }

        # Create agent-specific screenshot directory
        session_id = (
            datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + str(uuid.uuid4())[:8]
        )
        agent_browser_dir = (
            AGENTS_BASE_DIR
            / CLAUDE_CODE_TOOL_SLUG
            / agent_name
            / "browser_tool"
            / session_id
        )
        agent_browser_dir.mkdir(parents=True, exist_ok=True)

        # Import here to avoid circular dependency
        from ..gemini import GeminiBrowserAgent

        # Create a temporary browser agent instance with agent-specific screenshot dir
        temp_browser = GeminiBrowserAgent(logger=logger)
        temp_browser.screenshot_dir = agent_browser_dir
        temp_browser.session_id = session_id
        temp_browser.screenshot_counter = 0

        # Run browser task in thread pool to avoid Playwright sync API conflict with asyncio
        loop = asyncio.get_event_loop()

        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(
                executor, lambda: temp_browser.execute_task(task, agent_name, url)
            )

        # Cleanup browser
        try:
            temp_browser.cleanup()
        except:
            pass

        if result.get("ok"):
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Browser task completed!\n\nResult:\n{result.get('data')}\n\n"
                        f"Screenshots: {result.get('screenshot_dir')}",
                    }
                ]
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Browser task failed: {result.get('error')}",
                    }
                ],
                "isError": True,
            }

    return browser_use_tool
