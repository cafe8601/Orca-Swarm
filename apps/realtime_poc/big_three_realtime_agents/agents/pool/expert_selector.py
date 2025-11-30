"""
Expert Selector - AI-based intelligent expert selection.

Uses Claude to analyze tasks and select the most appropriate expert agent.
"""

import logging
import json
from typing import Optional, List, Dict, Any

from .agent_pool import AgentPoolManager, ExpertDefinition


logger = logging.getLogger(__name__)


class ExpertSelector:
    """AI-based expert selection system."""

    def __init__(self, pool_manager: AgentPoolManager, logger_instance=None):
        """
        Initialize expert selector.

        Args:
            pool_manager: Agent pool manager instance
            logger_instance: Logger instance
        """
        self.pool_manager = pool_manager
        self.logger = logger_instance or logger

    async def select_expert(
        self, task_description: str, available_experts: List[ExpertDefinition] = None
    ) -> Optional[str]:
        """
        Select most appropriate expert for task.

        Args:
            task_description: User task description
            available_experts: List of available experts (or None for all)

        Returns:
            expert_id (e.g., "BackendExpert") or None
        """
        if available_experts is None:
            available_experts = list(self.pool_manager.expert_definitions.values())

        if not available_experts:
            self.logger.warning("No experts available for selection")
            return None

        # Build expert descriptions
        experts_description = "\n".join(
            [
                f"- {exp.expert_id}: {exp.description}\n  Skills: {', '.join(exp.skills[:3])}"
                for exp in available_experts
            ]
        )

        # Simple heuristic-based selection (production would use Claude API)
        selected = self._heuristic_selection(task_description, available_experts)

        if selected:
            self.logger.info(
                f"Selected expert: {selected} for task: {task_description[:50]}..."
            )
            return selected

        # Default: Use first available or GeneralExpert
        fallback = "GeneralExpert" if "GeneralExpert" in [e.expert_id for e in available_experts] else available_experts[0].expert_id
        self.logger.warning(f"No specific expert found, using {fallback}")
        return fallback

    def _heuristic_selection(
        self, task_description: str, available_experts: List[ExpertDefinition]
    ) -> Optional[str]:
        """
        Heuristic-based expert selection.

        Args:
            task_description: Task description
            available_experts: Available experts

        Returns:
            Selected expert_id or None
        """
        task_lower = task_description.lower()

        # Keyword matching
        keywords_map = {
            "BackendExpert": ["backend", "api", "server", "database", "fastapi", "django"],
            "FrontendExpert": ["frontend", "ui", "react", "vue", "component", "page"],
            "DevOpsExpert": ["deploy", "docker", "kubernetes", "ci/cd", "infrastructure"],
            "SecurityExpert": ["security", "auth", "vulnerability", "penetration"],
            "DataExpert": ["data", "ml", "machine learning", "model", "training"],
            "TestExpert": ["test", "testing", "qa", "unit test", "integration"],
        }

        # Score each expert
        scores = {}
        for expert in available_experts:
            score = 0
            keywords = keywords_map.get(expert.expert_id, [])

            for keyword in keywords:
                if keyword in task_lower:
                    score += 1

            # Also check skills
            for skill in expert.skills:
                if skill.lower() in task_lower:
                    score += 0.5

            if score > 0:
                scores[expert.expert_id] = score

        # Return highest scoring expert
        if scores:
            best_expert = max(scores, key=scores.get)
            return best_expert

        return None

    async def check_needs_new_expert(
        self, task_description: str, existing_experts: List[ExpertDefinition] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if new expert type is needed (AI-powered analysis).

        Args:
            task_description: Task description
            existing_experts: Existing expert definitions

        Returns:
            {
                "needs_new": True/False,
                "suggested_expert": {...} if needs_new
            }
        """
        if existing_experts is None:
            existing_experts = list(self.pool_manager.expert_definitions.values())

        experts_list = ", ".join([exp.expert_id for exp in existing_experts])

        # Simplified heuristic check
        # In production, this would use Claude API for intelligent analysis

        # Check if any existing expert matches
        selected = await self.select_expert(task_description, existing_experts)

        if selected and selected != "GeneralExpert":
            # Found specific expert
            return {"needs_new": False}

        # Heuristic: Check for specialized keywords not covered
        specialized_keywords = {
            "blockchain": {"expert_id": "BlockchainExpert", "name": "Blockchain Expert"},
            "quantum": {"expert_id": "QuantumExpert", "name": "Quantum Computing Expert"},
            "game": {"expert_id": "GameExpert", "name": "Game Development Expert"},
            "mobile": {"expert_id": "MobileExpert", "name": "Mobile Development Expert"},
        }

        task_lower = task_description.lower()
        for keyword, expert_def in specialized_keywords.items():
            if keyword in task_lower:
                # Check if not already in pool
                if expert_def["expert_id"] not in [e.expert_id for e in existing_experts]:
                    return {
                        "needs_new": True,
                        "expert_id": expert_def["expert_id"],
                        "name": expert_def["name"],
                        "specialization": keyword,
                        "description": f"Expert in {keyword} development and technology",
                        "skills": [keyword, "development", "architecture"],
                    }

        # No new expert needed
        return {"needs_new": False}

    def suggest_experts_for_workflow(
        self, workflow_steps: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Suggest experts for multi-step workflow.

        Args:
            workflow_steps: List of workflow step descriptions

        Returns:
            List of suggested experts with allocation strategy
        """
        suggestions = []

        for i, step in enumerate(workflow_steps):
            expert_id = self._heuristic_selection(
                step, list(self.pool_manager.expert_definitions.values())
            )

            if expert_id:
                suggestions.append(
                    {
                        "step_index": i,
                        "step_description": step,
                        "suggested_expert": expert_id,
                        "can_reuse": i > 0
                        and suggestions
                        and suggestions[-1]["suggested_expert"] == expert_id,
                    }
                )

        return suggestions
