"""
Session management for OpenAI Realtime API.

Handles token usage tracking, cost calculation, and session state management.
"""

import logging
from typing import Optional, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel


class SessionManager:
    """
    Manages session state, token usage, and cost tracking.

    Provides centralized management of session configuration, token counting,
    and cost calculation for OpenAI Realtime API interactions.
    """

    def __init__(self, logger: logging.Logger, realtime_model: str):
        """
        Initialize session manager.

        Args:
            logger: Logger instance for session events.
            realtime_model: Model name for cost calculation.
        """
        self.logger = logger
        self.realtime_model = realtime_model
        self.console = Console()

        # Token usage tracking
        self.token_usage = {
            "text_input_tokens": 0,
            "audio_input_tokens": 0,
            "text_output_tokens": 0,
            "audio_output_tokens": 0,
            "total_cost": 0.0,
        }

    def update_token_usage(self, usage_data: Dict[str, int]):
        """
        Update token usage from API response.

        Args:
            usage_data: Dictionary containing token counts from API.
        """
        for key in ["text_input_tokens", "audio_input_tokens",
                    "text_output_tokens", "audio_output_tokens"]:
            if key in usage_data:
                self.token_usage[key] += usage_data[key]

    def calculate_cost_from_usage(self, usage_data: Dict[str, int], model: Optional[str] = None) -> float:
        """
        Calculate cost from token usage data.

        Args:
            usage_data: Token usage dictionary.
            model: Optional model override for cost calculation.

        Returns:
            Cost in USD.
        """
        model = model or self.realtime_model

        # OpenAI Realtime API pricing (per million tokens)
        text_input_rate = 10.0
        text_output_rate = 40.0
        audio_input_rate = 200.0
        audio_output_rate = 800.0

        text_cost = (
            (usage_data.get("text_input_tokens", 0) / 1_000_000) * text_input_rate
            + (usage_data.get("text_output_tokens", 0) / 1_000_000) * text_output_rate
        )

        audio_cost = (
            (usage_data.get("audio_input_tokens", 0) / 1_000_000) * audio_input_rate
            + (usage_data.get("audio_output_tokens", 0) / 1_000_000) * audio_output_rate
        )

        return text_cost + audio_cost

    def display_token_summary(self):
        """Display token usage and cost summary in rich table format."""
        usage = self.token_usage

        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Category", style="bold")
        table.add_column("Input Tokens", justify="right")
        table.add_column("Output Tokens", justify="right")
        table.add_column("Cost (USD)", justify="right")

        text_cost = (
            (usage.get("text_input_tokens", 0) / 1_000_000) * 10.0
            + (usage.get("text_output_tokens", 0) / 1_000_000) * 40.0
        )
        audio_cost = (
            (usage.get("audio_input_tokens", 0) / 1_000_000) * 200.0
            + (usage.get("audio_output_tokens", 0) / 1_000_000) * 800.0
        )

        table.add_row(
            "Text",
            f"{usage.get('text_input_tokens', 0):,}",
            f"{usage.get('text_output_tokens', 0):,}",
            f"${text_cost:.4f}",
        )
        table.add_row(
            "Audio",
            f"{usage.get('audio_input_tokens', 0):,}",
            f"{usage.get('audio_output_tokens', 0):,}",
            f"${audio_cost:.4f}",
        )
        table.add_row(
            "[bold]Total[/bold]",
            f"[bold]{usage.get('text_input_tokens', 0) + usage.get('audio_input_tokens', 0):,}[/bold]",
            f"[bold]{usage.get('text_output_tokens', 0) + usage.get('audio_output_tokens', 0):,}[/bold]",
            f"[bold]${usage.get('total_cost', 0.0):.4f}[/bold]",
        )

        self.console.print(Panel.fit(table, title="Token Usage & Cost", border_style="cyan"))
