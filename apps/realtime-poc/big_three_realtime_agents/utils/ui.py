"""
UI utilities for Big Three Realtime Agents.

Provides rich console formatting and display utilities.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from .ui_formatters import format_relative_paths, get_most_recent_file


# Global console instance
console = Console()


def log_panel(
    message: str, *, title: str = "Agent", style: str = "cyan",
    expand: bool = True, logger: Optional[logging.Logger] = None, level: str = "info"
) -> None:
    """Log message to console panel and file logger."""
    console.print(Panel(message, title=title, border_style=style, expand=expand))
    if logger:
        log_fn = getattr(logger, level, None)
        if log_fn:
            log_fn(message)


def log_tool_catalog(tool_specs: List[Dict[str, Any]], logger: Optional[logging.Logger] = None) -> None:
    """Display available tools in a panel."""
    if not tool_specs:
        return

    entries = []
    for spec in tool_specs:
        name = spec.get("name", "unknown_tool")
        properties = spec.get("parameters", {}).get("properties", {}) or {}
        params = ", ".join(properties.keys())
        entries.append(f"{name}({params})" if params else f"{name}()")

    syntax = Syntax(json.dumps(entries, indent=2, ensure_ascii=False), "json",
                    theme="monokai", word_wrap=True)
    console.print(Panel(syntax, title="Tool Catalog", border_style="cyan", expand=True))
    if logger:
        logger.info("Tool catalog loaded with %d tools", len(tool_specs))


def log_agent_roster(
    agents_payload: List[Dict[str, Any]], working_directory: Path,
    logger: Optional[logging.Logger] = None
) -> None:
    """Display agent roster in a table."""
    if not agents_payload:
        log_panel("No registered agents yet. Use create_agent to spin one up.",
                  title="Agent Roster", style="yellow", logger=logger)
        return

    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Name", style="bold")
    table.add_column("Session ID", overflow="fold")
    table.add_column("Type")
    table.add_column("Tool")
    table.add_column("Recent File", overflow="fold")

    for agent in agents_payload:
        files = agent.get("operator_files") or []
        relative_paths = format_relative_paths(files, working_directory) if files else []
        recent_file = get_most_recent_file(relative_paths)

        table.add_row(
            agent.get("name", "?"),
            agent.get("session_id", "?"),
            agent.get("type", "?"),
            agent.get("tool", "?"),
            recent_file,
        )

    console.print(Panel.fit(table, title="Agent Roster", border_style="cyan"))
    if logger:
        logger.debug("Listed %d agents", len(agents_payload))


def log_tool_request(
    tool_name: str, call_id: str, arguments_str: str, logger: Optional[logging.Logger] = None
) -> None:
    """Display tool request in a panel."""
    try:
        args_obj = json.loads(arguments_str)
        args_formatted = json.dumps(args_obj, indent=2, ensure_ascii=False)
    except (json.JSONDecodeError, TypeError):
        args_formatted = arguments_str

    content = f"[bold]Call ID:[/bold] {call_id}\n[bold]Arguments:[/bold]\n{args_formatted}"
    console.print(Panel(content, title=f"Tool: {tool_name}", border_style="yellow"))
    if logger:
        logger.debug(f"Tool request: {tool_name}({arguments_str})")
