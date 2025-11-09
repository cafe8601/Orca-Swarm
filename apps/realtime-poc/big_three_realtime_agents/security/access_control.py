"""
Access control - Permission and policy management.

Manages access permissions for agents and tools with
policy-based authorization.
"""

import logging
from typing import Dict, Set, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Available permissions."""
    CREATE_AGENT = "create_agent"
    DELETE_AGENT = "delete_agent"
    COMMAND_AGENT = "command_agent"
    BROWSER_USE = "browser_use"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"
    ADMIN = "admin"


class AccessControl:
    """
    Policy-based access control system.

    Manages permissions for agents and operations.

    Example:
        >>> access = AccessControl()
        >>> access.grant_permission("user1", Permission.CREATE_AGENT)
        >>> if access.check_permission("user1", Permission.CREATE_AGENT):
        ...     # Allow operation
    """

    def __init__(self):
        """Initialize access control."""
        self.permissions: Dict[str, Set[Permission]] = {}
        self.policies: List[Dict[str, Any]] = []

        # Default: allow all for system user
        self.grant_permission("system", Permission.ADMIN)

    def grant_permission(self, user: str, permission: Permission) -> None:
        """
        Grant permission to user.

        Args:
            user: User identifier
            permission: Permission to grant
        """
        if user not in self.permissions:
            self.permissions[user] = set()

        self.permissions[user].add(permission)
        logger.info(f"Granted {permission.value} to {user}")

    def revoke_permission(self, user: str, permission: Permission) -> None:
        """Revoke permission from user."""
        if user in self.permissions:
            self.permissions[user].discard(permission)
            logger.info(f"Revoked {permission.value} from {user}")

    def check_permission(
        self,
        user: str,
        permission: Permission
    ) -> bool:
        """
        Check if user has permission.

        Args:
            user: User identifier
            permission: Permission to check

        Returns:
            True if user has permission
        """
        user_perms = self.permissions.get(user, set())

        # Admin has all permissions
        if Permission.ADMIN in user_perms:
            return True

        # Check specific permission
        return permission in user_perms

    def add_policy(
        self,
        policy_id: str,
        description: str,
        rules: Dict[str, Any]
    ) -> None:
        """Add access control policy."""
        policy = {
            "policy_id": policy_id,
            "description": description,
            "rules": rules,
        }
        self.policies.append(policy)
        logger.info(f"Added policy: {policy_id}")

    def check_policy(
        self,
        user: str,
        operation: str,
        context: Dict[str, Any]
    ) -> bool:
        """
        Check if operation allowed by policies.

        Args:
            user: User identifier
            operation: Operation name
            context: Operation context

        Returns:
            True if allowed by policies
        """
        # If no policies, allow
        if not self.policies:
            return True

        # Check each policy (simplified)
        for policy in self.policies:
            rules = policy.get("rules", {})

            # Block list check
            if operation in rules.get("blocked_operations", []):
                logger.warning(
                    f"Policy {policy['policy_id']} blocked {operation} for {user}"
                )
                return False

        return True

    def get_user_permissions(self, user: str) -> List[str]:
        """Get all permissions for user."""
        perms = self.permissions.get(user, set())
        return [p.value for p in perms]
