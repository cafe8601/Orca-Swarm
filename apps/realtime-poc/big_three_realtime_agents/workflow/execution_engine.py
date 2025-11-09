"""
Workflow execution engine.

Executes workflow plans with support for sequential and parallel
execution strategies.
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, List
from datetime import datetime

from .workflow_models import (
    WorkflowPlan,
    WorkflowStage,
    WorkflowTask,
    ExecutionStrategy,
    TaskStatus,
)

logger = logging.getLogger(__name__)


class ExecutionEngine:
    """
    Execute workflow plans with different strategies.

    Supports sequential and parallel execution with basic error handling.

    Example:
        >>> engine = ExecutionEngine(pool_integration, memory)
        >>> result = await engine.execute_plan(plan)
    """

    def __init__(self, pool_integration, memory_manager):
        """
        Initialize execution engine.

        Args:
            pool_integration: Pool integration manager
            memory_manager: Memory manager for context
        """
        self.pool = pool_integration
        self.memory = memory_manager
        self.logger = logger

    async def execute_plan(self, plan: WorkflowPlan) -> Dict[str, Any]:
        """
        Execute complete workflow plan.

        Args:
            plan: Workflow plan to execute

        Returns:
            Execution result with status and outcomes
        """
        self.logger.info(f"Executing workflow: {plan.plan_id}")
        execution_id = f"exec_{uuid.uuid4().hex[:8]}"
        start_time = datetime.now()

        results = {
            "execution_id": execution_id,
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "started_at": start_time.isoformat(),
            "stage_results": [],
            "status": "running",
        }

        # Execute each stage
        for stage in plan.stages:
            stage_result = await self._execute_stage(stage, plan)
            results["stage_results"].append(stage_result)

            # Check for failures
            if stage_result["status"] == "failed" and not stage.continue_on_failure:
                results["status"] = "failed"
                break

        # Determine overall status
        if results["status"] != "failed":
            if plan.is_complete():
                results["status"] = "completed"
            elif plan.has_failures():
                results["status"] = "partial"

        results["completed_at"] = datetime.now().isoformat()
        results["duration_seconds"] = (
            datetime.now() - start_time
        ).total_seconds()

        # Store in workflow memory
        self.memory.workflow.store_execution(execution_id, results)

        self.logger.info(
            f"Workflow {plan.plan_id} {results['status']}: "
            f"{results['duration_seconds']:.1f}s"
        )

        return results

    async def _execute_stage(
        self,
        stage: WorkflowStage,
        plan: WorkflowPlan
    ) -> Dict[str, Any]:
        """Execute a workflow stage."""
        self.logger.info(f"Executing stage: {stage.name} ({stage.strategy.value})")

        if stage.strategy == ExecutionStrategy.PARALLEL:
            task_results = await self._execute_parallel(stage.tasks)
        else:
            task_results = await self._execute_sequential(stage.tasks)

        # Check status
        failed = sum(1 for r in task_results if r.get("status") == "failed")
        completed = sum(1 for r in task_results if r.get("status") == "completed")

        stage_status = "completed" if failed == 0 else "failed"

        return {
            "stage_id": stage.stage_id,
            "stage_name": stage.name,
            "status": stage_status,
            "completed": completed,
            "failed": failed,
            "task_results": task_results,
        }

    async def _execute_sequential(
        self,
        tasks: List[WorkflowTask]
    ) -> List[Dict[str, Any]]:
        """Execute tasks sequentially."""
        results = []
        for task in tasks:
            result = await self._execute_task(task)
            results.append(result)
        return results

    async def _execute_parallel(
        self,
        tasks: List[WorkflowTask]
    ) -> List[Dict[str, Any]]:
        """Execute tasks in parallel."""
        # For now, simulate parallel with sequential
        # Full async implementation requires more complexity
        self.logger.warning("Parallel execution not fully implemented, using sequential")
        return await self._execute_sequential(tasks)

    async def _execute_task(self, task: WorkflowTask) -> Dict[str, Any]:
        """Execute a single task."""
        task.start()

        try:
            # This would integrate with actual agent execution
            # For now, return success placeholder
            result = {
                "task_id": task.task_id,
                "status": "completed",
                "agent_id": task.agent_id,
                "description": task.description,
                "started_at": task.started_at.isoformat(),
            }

            task.complete(result)
            return result

        except Exception as exc:
            self.logger.error(f"Task {task.task_id} failed: {exc}")
            task.fail(str(exc))
            return {
                "task_id": task.task_id,
                "status": "failed",
                "error": str(exc),
            }
