"""
Tool specification builders for OpenAI Realtime API.

Builds tool specs organized by functional domain.
"""

from typing import List, Dict, Any

from ...config import CLAUDE_CODE_TOOL, GEMINI_TOOL, AGENTIC_CODING_TYPE, AGENTIC_BROWSERING_TYPE


class AgentToolSpecs:
    """Agent management tool specifications."""

    @staticmethod
    def get_specs() -> List[Dict[str, Any]]:
        """Get agent management tool specs."""
        return [
            {
                "type": "function",
                "name": "list_agents",
                "description": "List all registered agents (both Claude Code and Gemini browser agents)",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
            {
                "type": "function",
                "name": "create_agent",
                "description": f"Create a new agent. For coding tasks use tool='{CLAUDE_CODE_TOOL}' and type='{AGENTIC_CODING_TYPE}'. For browser tasks use tool='{GEMINI_TOOL}' and type='{AGENTIC_BROWSERING_TYPE}'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "tool": {
                            "type": "string",
                            "enum": [CLAUDE_CODE_TOOL, GEMINI_TOOL],
                            "description": f"Tool type: '{CLAUDE_CODE_TOOL}' for coding or '{GEMINI_TOOL}' for browser automation",
                        },
                        "type": {
                            "type": "string",
                            "enum": [AGENTIC_CODING_TYPE, AGENTIC_BROWSERING_TYPE],
                            "description": f"Agent type: '{AGENTIC_CODING_TYPE}' for coding or '{AGENTIC_BROWSERING_TYPE}' for browser",
                        },
                        "agent_name": {
                            "type": "string",
                            "description": "Optional custom name for the agent",
                        },
                    },
                    "required": ["tool", "type"],
                },
            },
            {
                "type": "function",
                "name": "command_agent",
                "description": "Send a command to an existing agent",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Name of the agent to command",
                        },
                        "prompt": {
                            "type": "string",
                            "description": "Task prompt for the agent",
                        },
                    },
                    "required": ["agent_name", "prompt"],
                },
            },
            {
                "type": "function",
                "name": "check_agent_result",
                "description": "Check the result of an agent's work",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Name of the agent",
                        },
                        "operator_file_name": {
                            "type": "string",
                            "description": "Optional operator file name",
                        },
                    },
                    "required": ["agent_name"],
                },
            },
            {
                "type": "function",
                "name": "delete_agent",
                "description": "Delete an agent from the registry",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "agent_name": {
                            "type": "string",
                            "description": "Name of the agent to delete",
                        }
                    },
                    "required": ["agent_name"],
                },
            },
        ]


class BrowserToolSpecs:
    """Browser automation tool specifications."""

    @staticmethod
    def get_specs() -> List[Dict[str, Any]]:
        """Get browser automation tool specs."""
        return [
            {
                "type": "function",
                "name": "browser_use",
                "description": "Perform browser automation tasks directly",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "task": {
                            "type": "string",
                            "description": "Browser task description",
                        },
                        "url": {
                            "type": "string",
                            "description": "Optional starting URL",
                        },
                    },
                    "required": ["task"],
                },
            },
        ]


class FilesystemToolSpecs:
    """Filesystem operation tool specifications."""

    @staticmethod
    def get_specs() -> List[Dict[str, Any]]:
        """Get filesystem tool specs."""
        return [
            {
                "type": "function",
                "name": "open_file",
                "description": "Open a file in VS Code or default application",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Relative path to the file",
                        }
                    },
                    "required": ["file_path"],
                },
            },
            {
                "type": "function",
                "name": "read_file",
                "description": "Read and return the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Relative path to the file",
                        }
                    },
                    "required": ["file_path"],
                },
            },
        ]


class ReportingToolSpecs:
    """Reporting and monitoring tool specifications."""

    @staticmethod
    def get_specs() -> List[Dict[str, Any]]:
        """Get reporting tool specs."""
        return [
            {
                "type": "function",
                "name": "report_costs",
                "description": "Display token usage and cost summary",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        ]
