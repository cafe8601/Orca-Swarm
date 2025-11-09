"""
Workflow Orchestration System - Intelligent task coordination.

Provides workflow planning, execution strategies, and result validation
for complex multi-agent tasks.

Modules:
    workflow_planner: Task decomposition and planning
    execution_engine: Workflow execution with strategies
    workflow_models: Data structures for workflows

Example:
    >>> from .workflow_planner import WorkflowPlanner
    >>> from .execution_engine import ExecutionEngine
    >>> planner = WorkflowPlanner(pool_manager, memory)
    >>> plan = await planner.create_plan("Build blog API")
    >>> engine = ExecutionEngine(pool_manager, memory)
    >>> result = await engine.execute(plan)
"""

from .workflow_models import (
    ExecutionStrategy,
    TaskStatus,
    WorkflowTask,
    WorkflowStage,
    WorkflowPlan,
)
from .workflow_planner import WorkflowPlanner
from .execution_engine import ExecutionEngine

__all__ = [
    "ExecutionStrategy",
    "TaskStatus",
    "WorkflowTask",
    "WorkflowStage",
    "WorkflowPlan",
    "WorkflowPlanner",
    "ExecutionEngine",
]
