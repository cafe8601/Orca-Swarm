#!/usr/bin/env python3
"""
Main entry point for Big Three Realtime Agents.

Handles command-line argument parsing and agent initialization.
Supports profile-based system configuration for different use cases.
"""

import argparse
import signal
import sys
from typing import Optional
from rich.panel import Panel
from rich.table import Table

from .logging_setup import setup_logging
from .config import (
    REALTIME_MODEL_DEFAULT,
    REALTIME_MODEL_MINI,
    GEMINI_MODEL,
    DEFAULT_CLAUDE_MODEL,
    AGENT_WORKING_DIRECTORY,
)
from .utils import console
from .agents.openai import OpenAIRealtimeVoiceAgent
from .profiles import ProfileManager, Profile, WorkflowTemplateRegistry


# Global instances for signal handlers
_agent_instance: Optional[OpenAIRealtimeVoiceAgent] = None
_profile_manager: Optional[ProfileManager] = None
_workflow_registry: Optional[WorkflowTemplateRegistry] = None


def signal_handler(signum: int, frame) -> None:
    """
    Handle SIGTERM and SIGINT gracefully.

    Args:
        signum: Signal number received.
        frame: Current stack frame.
    """
    signal_name = "SIGTERM" if signum == signal.SIGTERM else "SIGINT"
    print(f"\n{signal_name} received, shutting down gracefully...", file=sys.stderr)

    if _agent_instance:
        try:
            _agent_instance.cleanup()
            print("Agent cleanup completed successfully", file=sys.stderr)
        except Exception as e:
            print(f"Error during cleanup: {e}", file=sys.stderr)

    sys.exit(0)


def display_profiles(profile_manager: ProfileManager) -> None:
    """Display available profiles in a formatted table."""
    table = Table(title="Available Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Display Name", style="green")
    table.add_column("Description", style="white")

    for profile in profile_manager.list_profiles():
        table.add_row(
            profile["name"],
            profile["display_name"],
            profile["description"][:60] + "..." if len(profile["description"]) > 60 else profile["description"]
        )

    console.print(table)


def display_workflows(workflow_registry: WorkflowTemplateRegistry, profile_name: Optional[str] = None) -> None:
    """Display available workflow templates."""
    table = Table(title=f"Workflow Templates{f' for {profile_name}' if profile_name else ''}")
    table.add_column("Name", style="cyan")
    table.add_column("Category", style="magenta")
    table.add_column("Complexity", style="yellow")
    table.add_column("Duration", style="green")

    templates = workflow_registry.list_templates(category=profile_name if profile_name else None)
    for template in templates:
        table.add_row(
            template["name"],
            template["category"],
            template["complexity"],
            template["estimated_duration"]
        )

    console.print(table)


def main() -> int:
    """Main entry point."""
    global _agent_instance, _profile_manager, _workflow_registry

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser(
        description="Big Three Realtime Agents - Unified agent system with voice, coding, and browser automation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Profiles:
  developer   Software development mode (default)
  researcher  Academic research and paper writing mode
  business    Business analysis and strategic planning mode

Examples:
  %(prog)s --profile researcher --workflow literature_review
  %(prog)s --profile business --prompt "Analyze market trends for AI"
  %(prog)s --voice --profile developer
        """
    )
    parser.add_argument(
        "--input",
        choices=["text", "audio"],
        default="text",
        help="Input mode: 'text' for typing, 'audio' for microphone",
    )
    parser.add_argument(
        "--output",
        choices=["text", "audio"],
        default="text",
        help="Output mode: 'text' for text responses, 'audio' for voice responses",
    )
    parser.add_argument(
        "--voice",
        action="store_true",
        help="Enable voice mode (sets both input and output to audio)",
    )
    parser.add_argument(
        "--prompt",
        type=str,
        help="Optional text prompt to auto-dispatch (forces text input/output).",
    )
    parser.add_argument(
        "--mini",
        action="store_true",
        help=f"Use the mini realtime model ({REALTIME_MODEL_MINI}) instead of the default",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Auto-prompt mode timeout in seconds (default: 300)",
    )
    # Profile-related arguments
    parser.add_argument(
        "--profile",
        type=str,
        default="developer",
        help="System profile to use (developer, researcher, business)",
    )
    parser.add_argument(
        "--workflow",
        type=str,
        help="Workflow template to execute",
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List available profiles and exit",
    )
    parser.add_argument(
        "--list-workflows",
        action="store_true",
        help="List available workflow templates and exit",
    )

    args = parser.parse_args()

    # Initialize profile manager and workflow registry
    _profile_manager = ProfileManager()
    _workflow_registry = WorkflowTemplateRegistry()

    # Handle list commands
    if args.list_profiles:
        display_profiles(_profile_manager)
        return 0

    if args.list_workflows:
        display_workflows(_workflow_registry, args.profile if args.profile != "developer" else None)
        return 0

    # Set active profile
    if not _profile_manager.set_active_profile(args.profile):
        console.print(f"[red]Error: Unknown profile '{args.profile}'[/red]")
        console.print("Available profiles:")
        display_profiles(_profile_manager)
        return 1

    active_profile = _profile_manager.get_active_profile()

    startup_prompt = None
    input_mode = args.input
    output_mode = args.output
    realtime_model = REALTIME_MODEL_MINI if args.mini else REALTIME_MODEL_DEFAULT

    # Voice flag overrides input/output settings
    if args.voice:
        input_mode = "audio"
        output_mode = "audio"

    # Prompt flag forces text mode
    if args.prompt:
        startup_prompt = args.prompt
        input_mode = "text"
        output_mode = "text"

    # If workflow specified, add it to the prompt context
    workflow_template = None
    if args.workflow:
        workflow_template = _workflow_registry.get(args.workflow)
        if not workflow_template:
            console.print(f"[red]Error: Unknown workflow '{args.workflow}'[/red]")
            display_workflows(_workflow_registry, args.profile)
            return 1

    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Big Three Realtime Agents")
    logger.info("=" * 60)
    logger.info(f"Profile: {active_profile.display_name if active_profile else 'None'}")
    logger.info(f"Input: {input_mode}, Output: {output_mode}")
    logger.info(f"Realtime model: {realtime_model}")
    logger.info(f"Gemini model: {GEMINI_MODEL}")
    logger.info(f"Claude model: {DEFAULT_CLAUDE_MODEL}")
    logger.info(f"Agent working directory: {AGENT_WORKING_DIRECTORY}")
    if workflow_template:
        logger.info(f"Workflow: {workflow_template.display_name}")
    if startup_prompt:
        logger.info(f"Auto prompt enabled: {startup_prompt}")

    config_message = (
        f"Profile: {active_profile.display_name if active_profile else 'None'}\n"
        f"Input: {input_mode}\n"
        f"Output: {output_mode}\n"
        f"Realtime model: {realtime_model}\n"
        f"Gemini model: {GEMINI_MODEL}\n"
        f"Claude model: {DEFAULT_CLAUDE_MODEL}\n"
        f"Working dir: {AGENT_WORKING_DIRECTORY}"
    )
    if workflow_template:
        config_message += f"\nWorkflow: {workflow_template.display_name}"

    console.print(
        Panel(config_message, title="Launch Configuration", border_style="cyan")
    )

    # Display profile information
    if active_profile:
        profile_info = (
            f"Description: {active_profile.description}\n"
            f"Primary Agents: {', '.join(active_profile.primary_agents[:5])}"
            f"{'...' if len(active_profile.primary_agents) > 5 else ''}"
        )
        console.print(
            Panel(profile_info, title=f"Profile: {active_profile.display_name}", border_style="green")
        )

    if startup_prompt:
        console.print(
            Panel(
                f"Auto prompt enabled:\n{startup_prompt}",
                title="Auto Prompt",
                border_style="magenta",
            )
        )

    try:
        # Build system prompt additions from profile
        system_prompt_additions = _profile_manager.get_system_prompt_additions()

        agent = OpenAIRealtimeVoiceAgent(
            input_mode=input_mode,
            output_mode=output_mode,
            logger=logger,
            startup_prompt=startup_prompt,
            realtime_model=realtime_model,
            auto_timeout=args.timeout,
            profile=active_profile,
            workflow_template=workflow_template,
            system_prompt_prefix=system_prompt_additions.get("prefix", ""),
            system_prompt_suffix=system_prompt_additions.get("suffix", ""),
        )
        _agent_instance = agent  # Set global instance for signal handlers

        agent.connect()
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
    except Exception as exc:
        logger.error(f"Fatal error: {exc}", exc_info=True)
        return 1
    finally:
        # Ensure cleanup is always called
        if _agent_instance:
            try:
                _agent_instance.cleanup()
                logger.info("Agent cleanup completed")
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")
            _agent_instance = None

    logger.info("Agent terminated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
