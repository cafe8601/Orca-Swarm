#!/usr/bin/env python3
"""
Main entry point for Big Three Realtime Agents.

Handles command-line argument parsing and agent initialization.
"""

import argparse
from rich.panel import Panel

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


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Big Three Realtime Agents - Unified agent system with voice, coding, and browser automation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
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

    args = parser.parse_args()

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

    logger = setup_logging()
    logger.info("=" * 60)
    logger.info("Big Three Realtime Agents")
    logger.info("=" * 60)
    logger.info(f"Input: {input_mode}, Output: {output_mode}")
    logger.info(f"Realtime model: {realtime_model}")
    logger.info(f"Gemini model: {GEMINI_MODEL}")
    logger.info(f"Claude model: {DEFAULT_CLAUDE_MODEL}")
    logger.info(f"Agent working directory: {AGENT_WORKING_DIRECTORY}")
    if startup_prompt:
        logger.info(f"Auto prompt enabled: {startup_prompt}")

    config_message = (
        f"Input: {input_mode}\n"
        f"Output: {output_mode}\n"
        f"Realtime model: {realtime_model}\n"
        f"Gemini model: {GEMINI_MODEL}\n"
        f"Claude model: {DEFAULT_CLAUDE_MODEL}\n"
        f"Working dir: {AGENT_WORKING_DIRECTORY}"
    )
    console.print(
        Panel(config_message, title="Launch Configuration", border_style="cyan")
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
        agent = OpenAIRealtimeVoiceAgent(
            input_mode=input_mode,
            output_mode=output_mode,
            logger=logger,
            startup_prompt=startup_prompt,
            realtime_model=realtime_model,
            auto_timeout=args.timeout,
        )
        agent.connect()
    except KeyboardInterrupt:
        logger.info("\nShutdown requested by user")
    except Exception as exc:
        logger.error(f"Fatal error: {exc}", exc_info=True)
        return 1

    logger.info("Agent terminated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
