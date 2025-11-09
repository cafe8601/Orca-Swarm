"""
Workflow data models and structures.

Defines the core data structures for workflow planning and execution.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ExecutionStrategy(Enum):
    """Execution strategy for workflow stages."""
    SEQUENTIAL = "sequential"     # Execute tasks one by one
    PARALLEL = "parallel"         # Execute tasks concurrently
    PIPELINE = "pipeline"         # Pass results between tasks


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowTask:
    """
    Individual task in a workflow.

    Attributes:
        task_id: Unique task identifier
        description: Task description
        agent_id: Expert agent ID to use
        estimated_duration: Expected duration in seconds
        dependencies: Task IDs this depends on
        status: Current status
        result: Task execution result
        error: Error message if failed
    """
    task_id: str
    description: str
    agent_id: str
    estimated_duration: int = 60
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def start(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.now()

    def complete(self, result: Dict[str, Any]) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()

    def fail(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.error = error
        self.completed_at = datetime.now()


@dataclass
class WorkflowStage:
    """
    Stage in a workflow containing multiple tasks.

    Attributes:
        stage_id: Stage identifier
        name: Stage name
        tasks: List of tasks in this stage
        strategy: Execution strategy
        continue_on_failure: Continue if task fails
    """
    stage_id: str
    name: str
    tasks: List[WorkflowTask]
    strategy: ExecutionStrategy = ExecutionStrategy.SEQUENTIAL
    continue_on_failure: bool = False


@dataclass
class WorkflowPlan:
    """
    Complete workflow execution plan.

    Attributes:
        plan_id: Unique plan identifier
        goal: Overall workflow goal
        stages: List of workflow stages
        estimated_total_duration: Total estimated time in seconds
        success_criteria: Criteria for success
        created_at: Plan creation timestamp
        metadata: Additional metadata
    """
    plan_id: str
    goal: str
    stages: List[WorkflowStage]
    estimated_total_duration: int
    success_criteria: str = "All tasks completed successfully"
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def get_all_tasks(self) -> List[WorkflowTask]:
        """Get all tasks across all stages."""
        tasks = []
        for stage in self.stages:
            tasks.extend(stage.tasks)
        return tasks

    def get_task_by_id(self, task_id: str) -> Optional[WorkflowTask]:
        """Find task by ID."""
        for task in self.get_all_tasks():
            if task.task_id == task_id:
                return task
        return None

    def get_stage_by_id(self, stage_id: str) -> Optional[WorkflowStage]:
        """Find stage by ID."""
        for stage in self.stages:
            if stage.stage_id == stage_id:
                return stage
        return None

    def is_complete(self) -> bool:
        """Check if all tasks are completed."""
        return all(
            task.status in (TaskStatus.COMPLETED, TaskStatus.SKIPPED)
            for task in self.get_all_tasks()
        )

    def has_failures(self) -> bool:
        """Check if any task failed."""
        return any(
            task.status == TaskStatus.FAILED
            for task in self.get_all_tasks()
        )
