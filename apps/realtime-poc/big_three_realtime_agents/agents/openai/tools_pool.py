"""
Agent pool tools for OpenAI orchestrator.

Provides tools for interacting with the expert agent pool system.
"""

import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class PoolTools:
    """
    Agent pool interaction tools.

    Provides tools for listing, selecting, and creating agents from pool.

    Tools:
        - list_expert_pool: List available expert agents
        - create_pool_agent: Create agent from pool
        - get_pool_status: Get pool instance status
    """

    def __init__(self, pool_integration):
        """
        Initialize pool tools.

        Args:
            pool_integration: PoolIntegrationManager instance
        """
        self.pool = pool_integration
        self.logger = logger

    def list_expert_pool(self) -> Dict[str, Any]:
        """
        List all available expert agents in pool.

        Returns:
            Dict with list of available experts
        """
        try:
            experts = self.pool.pool_manager.list_available_experts()

            self.logger.info(f"Listed {len(experts)} experts from pool")

            return {
                "ok": True,
                "total": len(experts),
                "experts": experts,
                "tiers": self._group_by_tier(experts),
            }

        except Exception as exc:
            self.logger.error(f"Failed to list expert pool: {exc}")
            return {"ok": False, "error": str(exc)}

    def create_pool_agent(
        self,
        task: str,
        agent_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create agent from expert pool.

        If agent_id not specified, intelligently selects best expert.

        Args:
            task: Task description
            agent_id: Optional specific expert ID
            context: Optional additional context

        Returns:
            Dict with agent creation result
        """
        try:
            result = self.pool.create_pool_agent(
                task=task,
                agent_id=agent_id,
                context=context
            )

            if result.get("ok"):
                self.logger.info(
                    f"Created pool agent: {result['instance_id']} "
                    f"({result['expert_name']})"
                )

            return result

        except Exception as exc:
            self.logger.error(f"Failed to create pool agent: {exc}")
            return {"ok": False, "error": str(exc)}

    def get_pool_status(self) -> Dict[str, Any]:
        """
        Get status of agent pool and active instances.

        Returns:
            Dict with pool statistics and instance status
        """
        try:
            instances = self.pool.pool_manager.get_instance_status()
            stats = {
                "total_experts": len(self.pool.pool_manager.expert_definitions),
                "active_instances": len(instances),
                "instances_by_status": self._group_by_status(instances),
            }

            return {
                "ok": True,
                "stats": stats,
                "instances": instances,
            }

        except Exception as exc:
            self.logger.error(f"Failed to get pool status: {exc}")
            return {"ok": False, "error": str(exc)}

    def search_experts(self, query: str) -> Dict[str, Any]:
        """
        Search expert pool by keyword.

        Args:
            query: Search keyword

        Returns:
            Dict with matching experts
        """
        try:
            results = self.pool.selector.search_experts(query)

            return {
                "ok": True,
                "query": query,
                "matches": len(results),
                "results": results,
            }

        except Exception as exc:
            self.logger.error(f"Failed to search experts: {exc}")
            return {"ok": False, "error": str(exc)}

    def _group_by_tier(self, experts: List[Dict]) -> Dict[str, int]:
        """Group experts by tier."""
        tiers = {}
        for expert in experts:
            tier = expert["tier"]
            tiers[tier] = tiers.get(tier, 0) + 1
        return tiers

    def _group_by_status(self, instances: List[Dict]) -> Dict[str, int]:
        """Group instances by status."""
        statuses = {}
        for instance in instances:
            status = instance["status"]
            statuses[status] = statuses.get(status, 0) + 1
        return statuses
