"""
Instance Executor - Execute tasks on expert agent instances.

Manages task execution, result handling, and context accumulation.
"""

import logging
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path

from .agent_pool import AgentPoolManager, AgentInstance, AgentStatus


logger = logging.getLogger(__name__)


class InstanceExecutor:
    """Execute tasks on agent instances."""

    def __init__(self, pool_manager: AgentPoolManager, claude_coder, logger_instance=None):
        """
        Initialize instance executor.

        Args:
            pool_manager: Agent pool manager
            claude_coder: ClaudeCodeAgenticCoder instance for execution
            logger_instance: Logger instance
        """
        self.pool_manager = pool_manager
        self.claude_coder = claude_coder
        self.logger = logger_instance or logger

    async def execute_task(
        self, instance_id: str, task: str, context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute task on expert instance.

        Args:
            instance_id: Instance ID (e.g., "BackendExpert#1")
            task: Task description
            context: Additional context (optional)

        Returns:
            Execution result dict
        """
        # Get instance
        instance = self.pool_manager.get_instance(instance_id)
        if not instance:
            return {"success": False, "error": f"Instance {instance_id} not found"}

        if instance.status == AgentStatus.TERMINATED:
            return {"success": False, "error": f"Instance {instance_id} is terminated"}

        try:
            # Mark as working
            self.pool_manager.mark_working(instance_id)

            # Build full task with context
            full_task = self._build_task_with_context(instance, task, context)

            # Execute using Claude coder
            result = await self._execute_via_claude(instance, full_task)

            # Update instance
            self._update_instance_after_execution(instance, task, result)

            # Release instance
            task_summary = result.get("output", "")[:500]  # First 500 chars
            self.pool_manager.release_instance(instance_id, task_summary)

            return {
                "success": True,
                "instance_id": instance_id,
                "output": result.get("output", ""),
                "files_modified": result.get("files_modified", []),
                "task_count": len(instance.task_history),
            }

        except Exception as exc:
            self.logger.error(f"Task execution failed for {instance_id}: {exc}")

            # Release instance even on error
            self.pool_manager.release_instance(instance_id, f"ERROR: {str(exc)}")

            return {"success": False, "error": str(exc), "instance_id": instance_id}

    def _build_task_with_context(
        self, instance: AgentInstance, task: str, additional_context: Optional[str]
    ) -> str:
        """Build task prompt with accumulated context."""
        parts = []

        # Add accumulated context from previous tasks
        if instance.accumulated_context:
            parts.append(f"# Previous Work Context\n{instance.accumulated_context}")

        # Add additional context if provided
        if additional_context:
            parts.append(f"# Additional Context\n{additional_context}")

        # Add current task
        parts.append(f"# Current Task\n{task}")

        return "\n\n".join(parts)

    async def _execute_via_claude(
        self, instance: AgentInstance, task: str
    ) -> Dict[str, Any]:
        """Execute task using Claude Code agent."""
        expert_def = self.pool_manager.expert_definitions[instance.expert_id]

        # Load system prompt
        prompt_path = Path(expert_def.system_prompt_template)
        if prompt_path.exists():
            system_prompt = prompt_path.read_text(encoding="utf-8")
        else:
            system_prompt = f"You are {expert_def.name}. {expert_def.description}"

        # Use Claude coder to execute
        # This is a simplified version - production would use full Claude SDK
        try:
            working_dir = Path(expert_def.working_directory)
            result = await self.claude_coder.execute_task(
                task=f"{system_prompt}\n\n{task}", working_dir=working_dir
            )
            return result
        except Exception as exc:
            self.logger.error(f"Claude execution error: {exc}")
            return {"output": f"Execution error: {str(exc)}", "files_modified": []}

    def _update_instance_after_execution(
        self, instance: AgentInstance, task: str, result: Dict[str, Any]
    ):
        """Update instance state after task execution."""
        # Task already added to history by release_instance
        # Just log success
        if result.get("output"):
            self.logger.info(
                f"Task completed for {instance.instance_id}: {task[:50]}... "
                f"(Total tasks: {len(instance.task_history) + 1})"
            )

    def get_instance_context(self, instance_id: str) -> Optional[str]:
        """Get accumulated context for instance."""
        instance = self.pool_manager.get_instance(instance_id)
        if instance:
            return instance.accumulated_context
        return None

    def clear_instance_context(self, instance_id: str) -> bool:
        """Clear accumulated context for instance."""
        instance = self.pool_manager.get_instance(instance_id)
        if instance:
            instance.accumulated_context = ""
            self.logger.info(f"Cleared context for {instance_id}")
            return True
        return False
