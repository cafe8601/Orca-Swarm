"""
Workflow validation - Verify execution results.

Validates workflow execution results against success criteria
and provides quality assessment.
"""

import logging
from typing import Dict, Any, List
from .workflow_models import WorkflowPlan, TaskStatus

logger = logging.getLogger(__name__)


class WorkflowValidator:
    """
    Validate workflow execution results.

    Checks if tasks completed successfully and meet criteria.

    Example:
        >>> validator = WorkflowValidator()
        >>> is_valid = validator.validate_execution(plan, results)
    """

    def __init__(self):
        """Initialize workflow validator."""
        self.logger = logger

    def validate_execution(
        self,
        plan: WorkflowPlan,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate workflow execution results.

        Args:
            plan: Original workflow plan
            results: Execution results

        Returns:
            Validation result with pass/fail and details
        """
        validation = {
            "valid": False,
            "score": 0.0,
            "checks": [],
            "issues": [],
            "recommendations": [],
        }

        # Check 1: All tasks attempted
        total_tasks = len(plan.get_all_tasks())
        stage_results = results.get("stage_results", [])
        task_results = []
        for stage in stage_results:
            task_results.extend(stage.get("task_results", []))

        if len(task_results) < total_tasks:
            validation["issues"].append(
                f"Only {len(task_results)}/{total_tasks} tasks attempted"
            )
        else:
            validation["checks"].append("All tasks attempted")
            validation["score"] += 25

        # Check 2: Task completion rate
        completed = sum(
            1 for r in task_results
            if r.get("status") == "completed"
        )
        completion_rate = completed / total_tasks if total_tasks > 0 else 0

        if completion_rate == 1.0:
            validation["checks"].append("100% task completion")
            validation["score"] += 50
        elif completion_rate >= 0.8:
            validation["checks"].append(f"{completion_rate*100:.0f}% task completion")
            validation["score"] += 35
            validation["recommendations"].append("Some tasks incomplete")
        else:
            validation["issues"].append(
                f"Low completion rate: {completion_rate*100:.0f}%"
            )

        # Check 3: No critical failures
        failed = sum(1 for r in task_results if r.get("status") == "failed")
        if failed == 0:
            validation["checks"].append("No task failures")
            validation["score"] += 25
        else:
            validation["issues"].append(f"{failed} task(s) failed")
            validation["recommendations"].append("Review failed tasks and retry")

        # Overall validation
        validation["valid"] = validation["score"] >= 75
        validation["completion_rate"] = completion_rate
        validation["tasks_completed"] = completed
        validation["tasks_failed"] = failed

        self.logger.info(
            f"Validation: {'PASS' if validation['valid'] else 'FAIL'} "
            f"(score: {validation['score']})"
        )

        return validation

    def validate_task_result(
        self,
        task_result: Dict[str, Any],
        criteria: str
    ) -> bool:
        """
        Validate single task result against criteria.

        Args:
            task_result: Task execution result
            criteria: Validation criteria

        Returns:
            True if valid, False otherwise
        """
        # Basic validation: task completed
        if task_result.get("status") != "completed":
            return False

        # If no specific criteria, completion is enough
        if not criteria:
            return True

        # Check for error indicators
        if task_result.get("error"):
            return False

        # Criteria-based validation (simplified)
        # In full implementation, this would use LLM
        return True
