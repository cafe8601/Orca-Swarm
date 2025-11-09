"""
Tool catalog builder for OpenAI Realtime Agent.

Builds tool specifications for OpenAI Realtime API including
extended tools for agent pool and workflow orchestration.
"""

from typing import List, Dict, Any

from .tool_spec_builders import (
    AgentToolSpecs,
    BrowserToolSpecs,
    FilesystemToolSpecs,
    ReportingToolSpecs,
)
from .extended_tool_specs import (
    build_pool_tool_specs,
    build_workflow_tool_specs,
)


def build_tool_specs(include_extended: bool = True) -> List[Dict[str, Any]]:
    """
    Build tool specifications for OpenAI Realtime API.

    Args:
        include_extended: Include pool and workflow tools (default: True)

    Returns:
        List of tool specification dictionaries.
    """
    specs = [
        *AgentToolSpecs.get_specs(),
        *BrowserToolSpecs.get_specs(),
        *FilesystemToolSpecs.get_specs(),
        *ReportingToolSpecs.get_specs(),
    ]

    # Add extended tools for agent pool and workflow
    if include_extended:
        specs.extend(build_pool_tool_specs())
        specs.extend(build_workflow_tool_specs())

    return specs
