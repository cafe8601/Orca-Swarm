"""
Extended tool specifications for agent pool and workflow systems.

Provides OpenAI function calling specs for the new advanced tools.
"""

from typing import List, Dict, Any


def build_pool_tool_specs() -> List[Dict[str, Any]]:
    """Build tool specs for agent pool system."""
    return [
        {
            "type": "function",
            "name": "list_expert_pool",
            "description": (
                "List all available expert agents in the pool. "
                "Shows 150+ specialized experts organized by tier "
                "(tier1-core, tier2-specialized, tier3-experimental). "
                "Use this to discover which experts are available."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
        {
            "type": "function",
            "name": "create_pool_agent",
            "description": (
                "Create an agent from the expert pool. "
                "If agent_id not specified, intelligently selects the best expert "
                "based on task analysis. This is preferred over create_agent "
                "as it uses specialized expert templates."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task description the agent will work on"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": (
                            "Optional specific expert ID (e.g., 'backend-architect'). "
                            "If not provided, best expert will be auto-selected."
                        )
                    },
                    "context": {
                        "type": "string",
                        "description": "Optional additional context for agent selection"
                    },
                },
                "required": ["task"],
            },
        },
        {
            "type": "function",
            "name": "search_experts",
            "description": (
                "Search expert pool by keyword to find relevant specialists. "
                "Useful when you need to discover which expert handles a specific domain."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keyword (e.g., 'API', 'security', 'testing')"
                    },
                },
                "required": ["query"],
            },
        },
        {
            "type": "function",
            "name": "get_pool_status",
            "description": (
                "Get current status of agent pool including active instances, "
                "available experts, and resource usage."
            ),
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    ]


def build_workflow_tool_specs() -> List[Dict[str, Any]]:
    """Build tool specs for workflow orchestration system."""
    return [
        {
            "type": "function",
            "name": "plan_simple_workflow",
            "description": (
                "Create a simple single-task workflow plan. "
                "Use this for straightforward tasks that need one expert agent."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {
                        "type": "string",
                        "description": "Task description"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Expert agent ID to use (e.g., 'backend-architect')"
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["sequential", "parallel"],
                        "description": "Execution strategy (default: sequential)"
                    },
                },
                "required": ["task", "agent_id"],
            },
        },
        {
            "type": "function",
            "name": "plan_multi_task_workflow",
            "description": (
                "Create a complex multi-task workflow plan. "
                "Use this for complex projects requiring multiple agents "
                "and coordinated execution."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "goal": {
                        "type": "string",
                        "description": "Overall workflow goal"
                    },
                    "tasks": {
                        "type": "array",
                        "description": "Array of task objects",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "agent_id": {"type": "string"},
                                "duration": {"type": "number"},
                                "dependencies": {"type": "array", "items": {"type": "string"}},
                            },
                            "required": ["description", "agent_id"],
                        },
                    },
                    "strategy": {
                        "type": "string",
                        "enum": ["sequential", "parallel"],
                        "description": "Overall execution strategy"
                    },
                },
                "required": ["goal", "tasks"],
            },
        },
        {
            "type": "function",
            "name": "get_workflow_status",
            "description": (
                "Get real-time status of a running workflow including "
                "task completion, failures, and progress."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "plan_id": {
                        "type": "string",
                        "description": "Workflow plan identifier"
                    },
                },
                "required": ["plan_id"],
            },
        },
    ]
