"""
Agent Pool Manager - Core pool management system.

Manages expert agent instances with dynamic allocation, reuse, and lifecycle management.
"""

import logging
import threading
import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from datetime import datetime, timezone
import json


logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent instance status."""
    IDLE = "idle"                  # Available for reuse
    WORKING = "working"            # Currently executing task
    RESERVED = "reserved"          # Allocated but not started
    TERMINATED = "terminated"      # Permanently stopped


@dataclass
class ExpertDefinition:
    """Expert agent type definition."""
    expert_id: str
    name: str
    specialization: str
    description: str
    skills: List[str]
    system_prompt_template: str
    allowed_tools: List[str]
    working_directory: str
    max_instances: int
    session_config: Dict[str, Any]


@dataclass
class AgentInstance:
    """Active expert agent instance."""
    instance_id: str              # e.g., "BackendExpert#1"
    expert_id: str                # e.g., "BackendExpert"
    session_id: str               # Claude SDK session ID
    status: AgentStatus
    created_at: datetime
    last_used_at: Optional[datetime]
    current_task: Optional[str]
    task_history: List[str]
    accumulated_context: str      # Context from previous tasks


class AgentPoolManager:
    """Expert agent pool manager with instance lifecycle management."""

    def __init__(self, pool_definition_path: str = None, logger_instance=None):
        """
        Initialize agent pool manager.

        Args:
            pool_definition_path: Path to expert definitions JSON
            logger_instance: Logger instance
        """
        self.logger = logger_instance or logger
        self.pool_lock = threading.Lock()

        # Load expert definitions
        self.expert_definitions: Dict[str, ExpertDefinition] = {}
        if pool_definition_path:
            self._load_expert_definitions(pool_definition_path)
        else:
            self._load_from_markdown_agents()

        # Active instance pool
        self.active_instances: Dict[str, AgentInstance] = {}

        # Instance counters
        self.instance_counters: Dict[str, int] = {}

        self.logger.info(
            f"AgentPoolManager initialized with {len(self.expert_definitions)} expert types"
        )

    def _load_expert_definitions(self, path: str):
        """Load expert definitions from JSON file."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for expert_id, config in data.get("expert_pool", {}).items():
            self.expert_definitions[expert_id] = ExpertDefinition(
                expert_id=expert_id,
                name=config["name"],
                specialization=config["specialization"],
                description=config["description"],
                skills=config["skills"],
                system_prompt_template=config["system_prompt_template"],
                allowed_tools=config["allowed_tools"],
                working_directory=config["working_directory"],
                max_instances=config["max_instances"],
                session_config=config["session_config"],
            )

    def _load_from_markdown_agents(self):
        """Load expert definitions from agentpool markdown files."""
        from ...config import AGENT_POOL_DIR

        # Load from Tier 1 core agents
        tier1_dir = Path(AGENT_POOL_DIR) / "tier1-core"
        if tier1_dir.exists():
            for md_file in tier1_dir.glob("*.md"):
                expert_id = md_file.stem.replace("-", "_").title().replace("_", "")

                self.expert_definitions[expert_id] = ExpertDefinition(
                    expert_id=expert_id,
                    name=md_file.stem.replace("-", " ").title(),
                    specialization="general",
                    description=f"Expert from {md_file.name}",
                    skills=["coding", "development"],
                    system_prompt_template=str(md_file),
                    allowed_tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
                    working_directory="./",
                    max_instances=3,
                    session_config={"model": "claude-sonnet-4-5-20250929", "temperature": 0.7},
                )

        self.logger.info(f"Loaded {len(self.expert_definitions)} agents from markdown")

    def list_expert_types(self) -> List[Dict[str, Any]]:
        """List all available expert types."""
        return [
            {
                "expert_id": exp.expert_id,
                "name": exp.name,
                "specialization": exp.specialization,
                "description": exp.description,
                "skills": exp.skills,
                "max_instances": exp.max_instances,
            }
            for exp in self.expert_definitions.values()
        ]

    def list_active_instances(self) -> List[Dict[str, Any]]:
        """List currently active instances."""
        with self.pool_lock:
            return [
                {
                    "instance_id": inst.instance_id,
                    "expert_id": inst.expert_id,
                    "status": inst.status.value,
                    "current_task": inst.current_task,
                    "last_used_at": (
                        inst.last_used_at.isoformat() if inst.last_used_at else None
                    ),
                    "task_count": len(inst.task_history),
                }
                for inst in self.active_instances.values()
            ]

    async def acquire_expert(
        self, expert_id: str, task_description: str, prefer_reuse: bool = True
    ) -> Optional[AgentInstance]:
        """
        Acquire expert instance (reuse or create).

        Args:
            expert_id: Expert type (e.g., "BackendExpert")
            task_description: Task description
            prefer_reuse: True to reuse idle instances

        Returns:
            AgentInstance or None if allocation failed
        """
        with self.pool_lock:
            # 1. Find idle instance
            if prefer_reuse:
                idle_instance = self._find_idle_instance(expert_id)
                if idle_instance:
                    self.logger.info(f"Reusing idle instance: {idle_instance.instance_id}")
                    idle_instance.status = AgentStatus.RESERVED
                    idle_instance.current_task = task_description
                    return idle_instance

            # 2. Check if can create new instance
            if not self._can_create_instance(expert_id):
                self.logger.warning(
                    f"Cannot create new instance for {expert_id}: max instances reached"
                )
                return None

            # 3. Create new instance
            instance = await self._create_new_instance(expert_id, task_description)
            self.logger.info(f"Created new instance: {instance.instance_id}")
            return instance

    def _find_idle_instance(self, expert_id: str) -> Optional[AgentInstance]:
        """Find idle instance of given expert type."""
        for inst in self.active_instances.values():
            if inst.expert_id == expert_id and inst.status == AgentStatus.IDLE:
                return inst
        return None

    def _can_create_instance(self, expert_id: str) -> bool:
        """Check if new instance can be created."""
        expert_def = self.expert_definitions.get(expert_id)
        if not expert_def:
            return False

        # Count current instances
        current_count = sum(
            1
            for inst in self.active_instances.values()
            if inst.expert_id == expert_id and inst.status != AgentStatus.TERMINATED
        )

        return current_count < expert_def.max_instances

    async def _create_new_instance(
        self, expert_id: str, task_description: str
    ) -> AgentInstance:
        """Create new agent instance."""
        expert_def = self.expert_definitions[expert_id]

        # Generate instance ID
        counter = self.instance_counters.get(expert_id, 0) + 1
        self.instance_counters[expert_id] = counter
        instance_id = f"{expert_id}#{counter}"

        # Load system prompt
        prompt_path = Path(expert_def.system_prompt_template)
        if prompt_path.exists():
            system_prompt = prompt_path.read_text(encoding="utf-8")
        else:
            system_prompt = f"You are {expert_def.name}. {expert_def.description}"

        # Generate session ID (simplified - would use Claude SDK in production)
        session_id = f"session_{instance_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create instance object
        instance = AgentInstance(
            instance_id=instance_id,
            expert_id=expert_id,
            session_id=session_id,
            status=AgentStatus.RESERVED,
            created_at=datetime.now(timezone.utc),
            last_used_at=None,
            current_task=task_description,
            task_history=[],
            accumulated_context="",
        )

        self.active_instances[instance_id] = instance
        return instance

    def mark_working(self, instance_id: str):
        """Mark instance as working."""
        with self.pool_lock:
            if instance_id in self.active_instances:
                self.active_instances[instance_id].status = AgentStatus.WORKING

    def release_instance(self, instance_id: str, task_result: str = ""):
        """
        Release instance to idle state.

        Args:
            instance_id: Instance ID
            task_result: Task result to add to context
        """
        with self.pool_lock:
            if instance_id not in self.active_instances:
                return

            instance = self.active_instances[instance_id]

            # Update task history
            if instance.current_task:
                instance.task_history.append(instance.current_task)

            # Accumulate context
            if task_result:
                instance.accumulated_context += f"\n---\n{task_result}"

            # Change status
            instance.status = AgentStatus.IDLE
            instance.last_used_at = datetime.now(timezone.utc)
            instance.current_task = None

            self.logger.info(
                f"Released instance {instance_id} (now IDLE, tasks: {len(instance.task_history)})"
            )

    def terminate_instance(self, instance_id: str):
        """Permanently terminate instance."""
        with self.pool_lock:
            if instance_id in self.active_instances:
                self.active_instances[instance_id].status = AgentStatus.TERMINATED
                self.logger.info(f"Terminated instance {instance_id}")

    def cleanup_idle_instances(self, max_idle_time_seconds: int = 3600) -> int:
        """
        Cleanup old idle instances.

        Args:
            max_idle_time_seconds: Maximum idle time (default 1 hour)

        Returns:
            Number of instances cleaned up
        """
        with self.pool_lock:
            now = datetime.now(timezone.utc)
            to_terminate = []

            for inst_id, inst in self.active_instances.items():
                if inst.status == AgentStatus.IDLE and inst.last_used_at:
                    idle_duration = (now - inst.last_used_at).total_seconds()
                    if idle_duration > max_idle_time_seconds:
                        to_terminate.append(inst_id)

            for inst_id in to_terminate:
                self.terminate_instance(inst_id)
                self.logger.info(f"Cleaned up idle instance: {inst_id}")

            return len(to_terminate)

    def get_instance(self, instance_id: str) -> Optional[AgentInstance]:
        """Get instance by ID."""
        return self.active_instances.get(instance_id)

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics."""
        with self.pool_lock:
            by_status = {"idle": 0, "working": 0, "reserved": 0, "terminated": 0}

            for inst in self.active_instances.values():
                by_status[inst.status.value] += 1

            return {
                "total_instances": len(self.active_instances),
                "expert_types": len(self.expert_definitions),
                "by_status": by_status,
                "instance_counters": dict(self.instance_counters),
            }
