"""Browser automation tools for OpenAI Realtime Agent."""

import logging
from typing import Dict, Any, Optional


class BrowserTools:
    """Browser automation tools."""

    def __init__(self, logger: logging.Logger, browser_agent):
        self.logger = logger
        self.browser_agent = browser_agent

    def browser_use(self, task: str, url: Optional[str] = None) -> Dict[str, Any]:
        """Execute browser automation task."""
        try:
            result = self.browser_agent.execute_task(task=task, url=url)
            return result
        except Exception as exc:
            self.logger.exception("Browser automation failed")
            return {"ok": False, "error": str(exc)}
