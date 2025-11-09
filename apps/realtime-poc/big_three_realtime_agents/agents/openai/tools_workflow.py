"""
Workflow orchestration tools for OpenAI orchestrator.

Provides tools for planning and executing multi-agent workflows.
"""

import logging
from typing import Dict, Any, List, Optional

from ...workflow.workflow_models import ExecutionStrategy

logger = logging.getLogger(__name__)


class WorkflowTools:
    """
    Workflow orchestration tools.

    Provides tools for planning and executing complex workflows.

    Tools:
        - plan_simple_workflow: Create simple workflow
        - execute_workflow: Execute planned workflow
        - get_workflow_status: Check workflow status
    """

    def __init__(self, workflow_planner, execution_engine, memory_manager):
        """
        Initialize workflow tools.

        Args:
            workflow_planner: WorkflowPlanner instance
            execution_engine: ExecutionEngine instance
            memory_manager: MemoryManager instance
        """
        self.planner = workflow_planner
        self.engine = execution_engine
        self.memory = memory_manager
        self.active_workflows: Dict[str, Any] = {}
        self.logger = logger

    def plan_simple_workflow(
        self,
        task: str,
        agent_id: str,
        strategy: str = "sequential"
    ) -> Dict[str, Any]:
        """
        Create simple single-task workflow.

        Args:
            task: Task description
            agent_id: Expert agent to use
            strategy: "sequential" or "parallel"

        Returns:
            Dict with plan details
        """
        try:
            exec_strategy = ExecutionStrategy(strategy)
            plan = self.planner.create_simple_plan(task, agent_id, exec_strategy)

            # Store in memory
            self.memory.store(f"workflow_plan_{plan.plan_id}", plan.goal)

            # Visualize plan
            visualization = self.planner.visualize_plan(plan)

            return {
                "ok": True,
                "plan_id": plan.plan_id,
                "goal": plan.goal,
                "tasks": len(plan.get_all_tasks()),
                "estimated_duration": plan.estimated_total_duration,
                "visualization": visualization,
            }

        except Exception as exc:
            self.logger.error(f"Failed to plan workflow: {exc}")
            return {"ok": False, "error": str(exc)}

    def plan_multi_task_workflow(
        self,
        goal: str,
        tasks: List[Dict[str, Any]],
        strategy: str = "sequential"
    ) -> Dict[str, Any]:
        """
        Create multi-task workflow.

        Args:
            goal: Overall goal
            tasks: List of task dicts
            strategy: Execution strategy

        Returns:
            Dict with plan details
        """
        try:
            exec_strategy = ExecutionStrategy(strategy)
            plan = self.planner.create_multi_task_plan(goal, tasks, exec_strategy)

            # Store plan
            self.active_workflows[plan.plan_id] = plan

            # Store in memory
            self.memory.store(f"workflow_plan_{plan.plan_id}", plan.goal)

            return {
                "ok": True,
                "plan_id": plan.plan_id,
                "goal": plan.goal,
                "tasks": len(plan.get_all_tasks()),
                "estimated_duration": plan.estimated_total_duration,
                "visualization": self.planner.visualize_plan(plan),
            }

        except Exception as exc:
            self.logger.error(f"Failed to plan multi-task workflow: {exc}")
            return {"ok": False, "error": str(exc)}

    async def execute_workflow(self, plan_id: str) -> Dict[str, Any]:
        """
        Execute a planned workflow.

        Args:
            plan_id: Plan identifier

        Returns:
            Dict with execution result
        """
        plan = self.active_workflows.get(plan_id)
        if not plan:
            return {
                "ok": False,
                "error": f"Workflow plan '{plan_id}' not found"
            }

        try:
            result = await self.engine.execute_plan(plan)

            # Clean up completed plan
            if result["status"] in ("completed", "failed"):
                self.active_workflows.pop(plan_id, None)

            return {
                "ok": True,
                **result
            }

        except Exception as exc:
            self.logger.error(f"Failed to execute workflow: {exc}")
            return {"ok": False, "error": str(exc)}

    def get_workflow_status(self, plan_id: str) -> Dict[str, Any]:
        """
        Get status of active workflow.

        Args:
            plan_id: Plan identifier

        Returns:
            Dict with workflow status
        """
        plan = self.active_workflows.get(plan_id)
        if not plan:
            return {
                "ok": False,
                "error": f"Workflow '{plan_id}' not found or completed"
            }

        return {
            "ok": True,
            "plan_id": plan.plan_id,
            "goal": plan.goal,
            "is_complete": plan.is_complete(),
            "has_failures": plan.has_failures(),
            "total_tasks": len(plan.get_all_tasks()),
            "tasks": [
                {
                    "task_id": t.task_id,
                    "status": t.status.value,
                    "agent_id": t.agent_id,
                }
                for t in plan.get_all_tasks()
            ],
        }
