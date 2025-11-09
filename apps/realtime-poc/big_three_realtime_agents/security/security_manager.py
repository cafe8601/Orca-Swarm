"""
Security manager - Central security coordinator.

Coordinates audit logging, access control, and security policies.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .audit_logger import AuditLogger, AuditEventType
from .access_control import AccessControl, Permission

logger = logging.getLogger(__name__)


class SecurityManager:
    """
    Central security system coordinator.

    Manages audit logging and access control for the system.

    Example:
        >>> security = SecurityManager(storage_dir="security")
        >>> security.audit_log("agent_created", {"agent_id": "backend"})
        >>> if security.authorize("user1", "create_agent"):
        ...     # Perform operation
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        """
        Initialize security manager.

        Args:
            storage_dir: Directory for security data storage
        """
        self.storage_dir = Path(storage_dir or "apps/content-gen/security")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self.audit = AuditLogger(self.storage_dir / "audit")
        self.access = AccessControl()

        self.logger = logger
        self.logger.info("Security manager initialized")

    def audit_log(
        self,
        event_type: str,
        data: Dict[str, Any],
        user: str = "system",
        severity: str = "info"
    ) -> None:
        """
        Log security audit event.

        Args:
            event_type: Type of event (string)
            data: Event data
            user: User who triggered event
            severity: Event severity
        """
        try:
            # Convert string to enum
            evt_enum = AuditEventType(event_type)
            self.audit.log_event(evt_enum, data, user, severity)
        except ValueError:
            # Unknown event type, log as info
            logger.warning(f"Unknown audit event type: {event_type}")

    def authorize(
        self,
        user: str,
        operation: str,
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if user authorized for operation.

        Args:
            user: User identifier
            operation: Operation name
            context: Optional operation context

        Returns:
            True if authorized, False otherwise
        """
        # Map operation to permission
        permission_map = {
            "create_agent": Permission.CREATE_AGENT,
            "delete_agent": Permission.DELETE_AGENT,
            "command_agent": Permission.COMMAND_AGENT,
            "browser_use": Permission.BROWSER_USE,
            "read_file": Permission.FILE_READ,
            "open_file": Permission.FILE_READ,
        }

        permission = permission_map.get(operation)
        if not permission:
            # Unknown operation - FAIL CLOSED (secure default)
            logger.warning(f"Unknown operation for authorization: {operation} - DENIED")
            self.audit_log("authorization_denied", {
                "user": user,
                "operation": operation,
                "reason": "unknown_operation"
            }, user=user, severity="warning")
            return False

        # Check permission
        has_permission = self.access.check_permission(user, permission)

        # Check policies
        passes_policy = self.access.check_policy(
            user,
            operation,
            context or {}
        )

        authorized = has_permission and passes_policy

        if not authorized:
            self.audit_log(
                "auth_failure",
                {
                    "user": user,
                    "operation": operation,
                    "reason": "insufficient_permissions"
                },
                user=user,
                severity="warning"
            )

        return authorized

    def get_security_summary(self) -> Dict[str, Any]:
        """Get security system summary."""
        audit_summary = self.audit.get_audit_summary()

        return {
            "audit": audit_summary,
            "active_users": len(self.access.permissions),
            "total_policies": len(self.access.policies),
        }

    def initialize_default_permissions(self) -> None:
        """Setup default permission scheme."""
        # System user has all permissions
        for perm in Permission:
            self.access.grant_permission("system", perm)

        logger.info("Default permissions initialized")
