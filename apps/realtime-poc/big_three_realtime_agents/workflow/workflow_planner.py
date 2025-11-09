"""
Workflow planner - AI-powered task decomposition.

Analyzes user requests and creates executable workflow plans
with intelligent agent assignment and execution strategies.
"""

import uuid
import logging
from typing import Dict, Any, List

from .workflow_models import (
    WorkflowPlan,
    WorkflowStage,
    WorkflowTask,
    ExecutionStrategy,
)

logger = logging.getLogger(__name__)


class WorkflowPlanner:
    """
    AI-powered workflow planning.

    Decomposes complex tasks into structured workflows with
    agent assignments and execution strategies.

    Example:
        >>> planner = WorkflowPlanner(pool_manager, memory)
        >>> plan = planner.create_simple_plan("Build blog API", "backend-architect")
    """

    def __init__(self, pool_manager, memory_manager):
        """
        Initialize workflow planner.

        Args:
            pool_manager: Agent pool manager
            memory_manager: Memory manager
        """
        self.pool_manager = pool_manager
        self.memory = memory_manager
        self.logger = logger

    def create_simple_plan(
        self,
        task_description: str,
        agent_id: str,
        strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
    ) -> WorkflowPlan:
        """
        Create simple single-task workflow plan.

        Args:
            task_description: What to do
            agent_id: Which expert agent to use
            strategy: Execution strategy

        Returns:
            WorkflowPlan with single stage and task
        """
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        task = WorkflowTask(
            task_id=f"task_{uuid.uuid4().hex[:6]}",
            description=task_description,
            agent_id=agent_id,
            estimated_duration=120,
        )

        stage = WorkflowStage(
            stage_id="stage_1",
            name="Execution",
            tasks=[task],
            strategy=strategy,
        )

        plan = WorkflowPlan(
            plan_id=plan_id,
            goal=task_description,
            stages=[stage],
            estimated_total_duration=120,
            success_criteria="Task completed without errors",
        )

        self.logger.info(f"Created simple plan: {plan_id}")
        return plan

    def create_multi_task_plan(
        self,
        goal: str,
        tasks: List[Dict[str, Any]],
        strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
    ) -> WorkflowPlan:
        """
        Create workflow with multiple tasks.

        Args:
            goal: Overall goal
            tasks: List of task dicts with description and agent_id
            strategy: Execution strategy

        Returns:
            WorkflowPlan with tasks organized in stages
        """
        plan_id = f"plan_{uuid.uuid4().hex[:8]}"

        workflow_tasks = []
        for i, task_data in enumerate(tasks, 1):
            task = WorkflowTask(
                task_id=f"task_{i}",
                description=task_data["description"],
                agent_id=task_data["agent_id"],
                estimated_duration=task_data.get("duration", 120),
                dependencies=task_data.get("dependencies", []),
            )
            workflow_tasks.append(task)

        # Calculate total duration
        if strategy == ExecutionStrategy.PARALLEL:
            total_duration = max(t.estimated_duration for t in workflow_tasks)
        else:
            total_duration = sum(t.estimated_duration for t in workflow_tasks)

        stage = WorkflowStage(
            stage_id="stage_1",
            name="Multi-Task Execution",
            tasks=workflow_tasks,
            strategy=strategy,
        )

        plan = WorkflowPlan(
            plan_id=plan_id,
            goal=goal,
            stages=[stage],
            estimated_total_duration=total_duration,
            success_criteria="All tasks completed successfully",
        )

        self.logger.info(
            f"Created multi-task plan: {plan_id} ({len(tasks)} tasks, {strategy.value})"
        )
        return plan

    def visualize_plan(self, plan: WorkflowPlan) -> str:
        """
        Create ASCII visualization of workflow plan.

        Args:
            plan: Workflow plan to visualize

        Returns:
            Formatted string representation
        """
        lines = []
        lines.append("=" * 60)
        lines.append(f"WORKFLOW PLAN: {plan.goal}")
        lines.append("=" * 60)
        lines.append(f"Plan ID: {plan.plan_id}")
        lines.append(f"Estimated Duration: {plan.estimated_total_duration}s")
        lines.append(f"Total Stages: {len(plan.stages)}")
        lines.append(f"Total Tasks: {len(plan.get_all_tasks())}")
        lines.append("")

        for i, stage in enumerate(plan.stages, 1):
            lines.append(f"[Stage {i}] {stage.name}")
            lines.append(f"  Strategy: {stage.strategy.value}")
            lines.append(f"  Tasks: {len(stage.tasks)}")
            lines.append("")

            for j, task in enumerate(stage.tasks, 1):
                deps = f" (depends: {', '.join(task.dependencies)})" if task.dependencies else ""
                lines.append(f"    {j}. [{task.agent_id}] {task.description}{deps}")
                lines.append(f"       Duration: ~{task.estimated_duration}s")

            lines.append("")

        lines.append(f"Success Criteria: {plan.success_criteria}")
        lines.append("=" * 60)

        return "\n".join(lines)
