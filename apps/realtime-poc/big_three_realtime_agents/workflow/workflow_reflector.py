"""
Workflow reflection - Analyze outcomes and extract insights.

Provides post-execution analysis to identify improvements
and learning opportunities.
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkflowReflector:
    """
    Analyze workflow execution and extract insights.

    Performs retrospective analysis to identify patterns,
    improvements, and lessons learned.

    Example:
        >>> reflector = WorkflowReflector()
        >>> insights = reflector.reflect(plan, results)
    """

    def __init__(self):
        """Initialize workflow reflector."""
        self.logger = logger

    def reflect(
        self,
        plan,
        results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Reflect on workflow execution.

        Args:
            plan: Original workflow plan
            results: Execution results

        Returns:
            Reflection insights and recommendations
        """
        reflection = {
            "execution_id": results.get("execution_id"),
            "goal": plan.goal,
            "timestamp": datetime.now().isoformat(),
            "performance": {},
            "insights": [],
            "lessons_learned": [],
            "recommendations": [],
        }

        # Performance analysis
        actual_duration = results.get("duration_seconds", 0)
        estimated_duration = plan.estimated_total_duration

        reflection["performance"] = {
            "estimated_duration": estimated_duration,
            "actual_duration": actual_duration,
            "variance": actual_duration - estimated_duration,
            "efficiency": (
                estimated_duration / actual_duration
                if actual_duration > 0 else 1.0
            ),
        }

        # Duration insights
        if actual_duration < estimated_duration * 0.8:
            reflection["insights"].append(
                "Workflow completed faster than estimated (efficient)"
            )
        elif actual_duration > estimated_duration * 1.5:
            reflection["insights"].append(
                "Workflow took significantly longer than estimated"
            )
            reflection["recommendations"].append(
                "Review task estimates for better planning"
            )

        # Task analysis
        stage_results = results.get("stage_results", [])
        total_tasks = sum(len(s.get("task_results", [])) for s in stage_results)
        completed = sum(
            sum(1 for t in s.get("task_results", []) if t.get("status") == "completed")
            for s in stage_results
        )
        failed = sum(
            sum(1 for t in s.get("task_results", []) if t.get("status") == "failed")
            for s in stage_results
        )

        reflection["task_summary"] = {
            "total": total_tasks,
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total_tasks if total_tasks > 0 else 0,
        }

        # Success insights
        if failed == 0:
            reflection["insights"].append("All tasks completed successfully")
            reflection["lessons_learned"].append(
                "Agent selection and task assignment was effective"
            )
        else:
            reflection["insights"].append(f"{failed} task(s) failed")
            reflection["recommendations"].append(
                "Analyze failed tasks for common patterns"
            )

        # Stage analysis
        for i, stage_result in enumerate(stage_results, 1):
            stage_status = stage_result.get("status")
            if stage_status == "failed":
                reflection["insights"].append(
                    f"Stage {i} failed - workflow may need redesign"
                )

        # General recommendations
        if reflection["task_summary"]["success_rate"] < 0.8:
            reflection["recommendations"].append(
                "Consider breaking tasks into smaller units"
            )

        self.logger.info(
            f"Reflection complete: {len(reflection['insights'])} insights, "
            f"{len(reflection['recommendations'])} recommendations"
        )

        return reflection

    def compare_executions(
        self,
        executions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Compare multiple workflow executions for patterns.

        Args:
            executions: List of execution results

        Returns:
            Comparative analysis
        """
        if not executions:
            return {"error": "No executions to compare"}

        comparison = {
            "total_executions": len(executions),
            "success_rate": 0.0,
            "avg_duration": 0.0,
            "patterns": [],
        }

        successful = sum(
            1 for e in executions
            if e.get("status") == "completed"
        )
        comparison["success_rate"] = successful / len(executions)

        durations = [e.get("duration_seconds", 0) for e in executions]
        comparison["avg_duration"] = sum(durations) / len(durations)

        # Pattern detection (simplified)
        if comparison["success_rate"] > 0.9:
            comparison["patterns"].append("High reliability workflow")
        elif comparison["success_rate"] < 0.5:
            comparison["patterns"].append("Workflow needs improvement")

        return comparison
