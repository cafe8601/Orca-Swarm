"""
Security System - Access control and audit logging.

Provides security features including access control, audit trails,
and security policy enforcement.

Modules:
    security_manager: Central security coordinator
    audit_logger: Security audit trail
    access_control: Permission management
    secrets_manager: Enhanced secret handling

Example:
    >>> from .security_manager import SecurityManager
    >>> security = SecurityManager()
    >>> security.audit_log("agent_created", {"agent_id": "backend-arch"})
"""

from .security_manager import SecurityManager
from .audit_logger import AuditLogger
from .access_control import AccessControl

__all__ = [
    "SecurityManager",
    "AuditLogger",
    "AccessControl",
]
