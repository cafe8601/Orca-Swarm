"""
Orchestrator integration - Connect all advanced systems.

Integrates agent pool, memory, and workflow systems with the
OpenAI realtime orchestrator.
"""

import logging
from pathlib import Path
from typing import Dict, Any

from .agents.pool.pool_integration import PoolIntegrationManager
from .memory.memory_manager import MemoryManager
from .workflow.workflow_planner import WorkflowPlanner
from .workflow.execution_engine import ExecutionEngine
from .workflow.workflow_validator import WorkflowValidator
from .workflow.workflow_reflector import WorkflowReflector
from .agents.openai.tools_pool import PoolTools
from .agents.openai.tools_workflow import WorkflowTools
from .learning.learning_manager import LearningManager
from .security.security_manager import SecurityManager

logger = logging.getLogger(__name__)


class OrchestratorIntegration:
    """
    Main integration layer for advanced systems.

    Coordinates agent pool, memory, and workflow systems with
    the realtime orchestrator.

    Example:
        >>> integration = OrchestratorIntegration(
        ...     pool_dir="agentpool/",
        ...     claude_coder=claude_coder
        ... )
        >>> integration.initialize()
        >>> tools = integration.get_extended_tools()
    """

    def __init__(
        self,
        pool_dir: Path,
        claude_coder,
        storage_dir: Optional[Path] = None
    ):
        """
        Initialize orchestrator integration.

        Args:
            pool_dir: Path to agentpool directory
            claude_coder: ClaudeCodeAgenticCoder instance
            storage_dir: Directory for persistent storage
        """
        self.pool_dir = Path(pool_dir)
        self.storage_dir = Path(storage_dir or "apps/content-gen/storage")

        # Initialize subsystems
        self.pool_integration = PoolIntegrationManager(pool_dir, claude_coder)
        self.memory = MemoryManager(storage_dir=self.storage_dir / "memory")

        # Initialize workflow system
        self.workflow_planner = WorkflowPlanner(
            self.pool_integration.pool_manager,
            self.memory
        )
        self.execution_engine = ExecutionEngine(
            self.pool_integration,
            self.memory
        )
        self.workflow_validator = WorkflowValidator()
        self.workflow_reflector = WorkflowReflector()

        # Initialize learning system
        self.learning = LearningManager(
            storage_dir=self.storage_dir / "learning"
        )

        # Initialize security system
        self.security = SecurityManager(
            storage_dir=self.storage_dir / "security"
        )
        self.security.initialize_default_permissions()

        # Initialize tool interfaces
        self.pool_tools = PoolTools(self.pool_integration)
        self.workflow_tools = WorkflowTools(
            self.workflow_planner,
            self.execution_engine,
            self.memory
        )

        self.logger = logger
        self.logger.info("Orchestrator integration initialized with all systems")

    def initialize(self) -> Dict[str, Any]:
        """
        Initialize all subsystems.

        Returns:
            Dict with initialization status
        """
        try:
            # Load agent pool
            expert_count = len(self.pool_integration.pool_manager.expert_definitions)

            # Initialize memory
            mem_stats = self.memory.get_stats()

            # Get learning stats
            learning_stats = self.learning.get_learning_stats()

            # Get security stats
            security_stats = self.security.get_security_summary()

            self.logger.info(
                f"Initialized: {expert_count} experts, "
                f"{mem_stats['session_keys']} session keys, "
                f"{learning_stats['total_outcomes']} outcomes tracked"
            )

            return {
                "ok": True,
                "expert_count": expert_count,
                "memory_stats": mem_stats,
                "learning_stats": learning_stats,
                "security_stats": security_stats,
                "systems": {
                    "agent_pool": True,
                    "memory": True,
                    "workflow": True,
                    "learning": True,
                    "security": True,
                },
            }

        except Exception as exc:
            self.logger.error(f"Initialization failed: {exc}")
            return {"ok": False, "error": str(exc)}

    def get_extended_tools(self) -> Dict[str, callable]:
        """
        Get all extended tool functions.

        Returns:
            Dict mapping tool names to callable functions
        """
        return {
            # Agent pool tools
            "list_expert_pool": self.pool_tools.list_expert_pool,
            "create_pool_agent": self.pool_tools.create_pool_agent,
            "get_pool_status": self.pool_tools.get_pool_status,
            "search_experts": self.pool_tools.search_experts,

            # Workflow tools
            "plan_simple_workflow": self.workflow_tools.plan_simple_workflow,
            "plan_multi_task_workflow": self.workflow_tools.plan_multi_task_workflow,
            "execute_workflow": self.workflow_tools.execute_workflow,
            "get_workflow_status": self.workflow_tools.get_workflow_status,
        }

    def shutdown(self) -> None:
        """Cleanup and shutdown all subsystems."""
        # Cleanup idle instances
        cleaned = self.pool_integration.pool_manager.cleanup_idle_instances()
        self.logger.info(f"Cleaned up {cleaned} idle agent instances")

        # Log shutdown event
        self.security.audit_log("system_shutdown", {
            "idle_instances_cleaned": cleaned
        })

        # Clear session memory
        self.memory.clear_session()

        self.logger.info("Orchestrator integration shutdown complete")

    def create_pool_agent_with_learning(
        self,
        task: str,
        agent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create pool agent with learning-enhanced selection.

        Args:
            task: Task description
            agent_id: Optional specific agent ID

        Returns:
            Agent creation result
        """
        # Get recommendation from learning system
        if not agent_id:
            agent_id = self.learning.suggest_agent_for_task(
                task,
                self.pool_integration.selector
            )

        # Create agent
        result = self.pool_tools.create_pool_agent(task, agent_id)

        # Audit log
        if result.get("ok"):
            self.security.audit_log("agent_created", {
                "instance_id": result.get("instance_id"),
                "agent_id": agent_id,
                "task": task[:100],
            })

        return result

    def execute_workflow_with_validation(
        self,
        plan_id: str
    ) -> Dict[str, Any]:
        """
        Execute workflow with validation and reflection.

        Args:
            plan_id: Workflow plan ID

        Returns:
            Execution result with validation and insights
        """
        # Get plan
        plan = self.workflow_tools.active_workflows.get(plan_id)
        if not plan:
            return {"ok": False, "error": "Plan not found"}

        # Execute
        result = await self.workflow_tools.execute_workflow(plan_id)

        # Validate
        validation = self.workflow_validator.validate_execution(plan, result)

        # Reflect
        reflection = self.workflow_reflector.reflect(plan, result)

        # Record outcome for learning
        self.learning.record_task_outcome(
            task=plan.goal,
            agent_id="workflow",
            result=result,
            success=validation["valid"]
        )

        # Audit log
        self.security.audit_log("workflow_executed", {
            "plan_id": plan_id,
            "goal": plan.goal,
            "status": result.get("status"),
            "validation_score": validation["score"],
        })

        return {
            **result,
            "validation": validation,
            "reflection": reflection,
        }
