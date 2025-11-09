"""Cost reporting tools for OpenAI Realtime Agent."""

import logging
from typing import Dict, Any

from ...config import OPENAI_PRICING


class ReportingTools:
    """Cost and usage reporting tools."""

    def __init__(self, logger: logging.Logger, token_usage_holder: dict, display_func):
        self.logger = logger
        self.token_usage_holder = token_usage_holder
        self.display_func = display_func

    def report_costs(self) -> Dict[str, Any]:
        """Display token usage and cost summary."""
        try:
            self.display_func()

            usage = self.token_usage_holder
            return {
                "ok": True,
                "total_cost_usd": usage.get("total_cost", 0.0),
                "text_tokens": {
                    "input": usage.get("text_input_tokens", 0),
                    "output": usage.get("text_output_tokens", 0),
                },
                "audio_tokens": {
                    "input": usage.get("audio_input_tokens", 0),
                    "output": usage.get("audio_output_tokens", 0),
                },
            }
        except Exception as exc:
            self.logger.exception("Failed to report costs")
            return {"ok": False, "error": str(exc)}

    def calculate_cost_from_usage(self, usage: Dict[str, Any], model: str) -> float:
        """Calculate cost in USD from usage data based on current model."""
        pricing = OPENAI_PRICING.get(model, OPENAI_PRICING["gpt-realtime-2025-08-28"])

        input_details = usage.get("input_token_details", {})
        output_details = usage.get("output_token_details", {})

        input_text_tokens = input_details.get("text_tokens", 0)
        input_audio_tokens = input_details.get("audio_tokens", 0)
        output_text_tokens = output_details.get("text_tokens", 0)
        output_audio_tokens = output_details.get("audio_tokens", 0)

        # Calculate costs
        text_input_cost = (input_text_tokens / 1_000_000) * pricing["text_input"]
        text_output_cost = (output_text_tokens / 1_000_000) * pricing["text_output"]
        audio_input_cost = (input_audio_tokens / 1_000_000) * pricing["audio_input"]
        audio_output_cost = (output_audio_tokens / 1_000_000) * pricing["audio_output"]

        total_cost = text_input_cost + text_output_cost + audio_input_cost + audio_output_cost
        return total_cost
