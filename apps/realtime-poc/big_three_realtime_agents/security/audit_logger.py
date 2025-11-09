"""
Audit logger - Security event tracking.

Tracks security-relevant events for compliance and debugging.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AuditEventType(Enum):
    """Security audit event types."""
    AGENT_CREATED = "agent_created"
    AGENT_DELETED = "agent_deleted"
    AGENT_COMMAND = "agent_command"
    TOOL_EXECUTED = "tool_executed"
    FILE_ACCESSED = "file_accessed"
    BROWSER_ACTION = "browser_action"
    AUTH_SUCCESS = "auth_success"
    AUTH_FAILURE = "auth_failure"
    SECURITY_VIOLATION = "security_violation"


class AuditLogger:
    """
    Security audit trail logger.

    Records security-relevant events with timestamps and context.

    Example:
        >>> audit = AuditLogger(storage_dir="security/audit")
        >>> audit.log_event(AuditEventType.AGENT_CREATED, {"agent_id": "backend"})
    """

    def __init__(self, storage_dir: Path):
        """
        Initialize audit logger.

        Args:
            storage_dir: Directory for audit logs
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self._current_log = self.storage_dir / "audit.jsonl"

    def log_event(
        self,
        event_type: AuditEventType,
        data: Dict[str, Any],
        user: str = "system",
        severity: str = "info"
    ) -> None:
        """
        Log security audit event.

        Args:
            event_type: Type of security event
            data: Event data
            user: User or system that triggered event
            severity: Event severity (info/warning/critical)
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type.value,
            "user": user,
            "severity": severity,
            "data": data,
        }

        try:
            with open(self._current_log, "a") as f:
                f.write(json.dumps(event) + "\n")

            if severity == "critical":
                logger.critical(f"AUDIT: {event_type.value} - {data}")
            elif severity == "warning":
                logger.warning(f"AUDIT: {event_type.value} - {data}")
            else:
                logger.info(f"AUDIT: {event_type.value}")

        except Exception as exc:
            logger.error(f"Failed to write audit log: {exc}")

    def get_recent_events(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent audit events."""
        if not self._current_log.exists():
            return []

        events = []
        try:
            with open(self._current_log, "r") as f:
                for line in f:
                    events.append(json.loads(line))
        except Exception as exc:
            logger.error(f"Failed to read audit log: {exc}")

        return events[-limit:] if events else []

    def search_events(
        self,
        event_type: Optional[AuditEventType] = None,
        user: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Search audit events with filters.

        Args:
            event_type: Filter by event type
            user: Filter by user
            since: Filter by timestamp

        Returns:
            List of matching audit events
        """
        events = self.get_recent_events(limit=1000)

        filtered = events
        if event_type:
            filtered = [e for e in filtered if e["event_type"] == event_type.value]
        if user:
            filtered = [e for e in filtered if e["user"] == user]
        if since:
            since_iso = since.isoformat()
            filtered = [e for e in filtered if e["timestamp"] >= since_iso]

        return filtered

    def get_audit_summary(self) -> Dict[str, Any]:
        """Get audit log summary statistics."""
        events = self.get_recent_events(limit=1000)

        summary = {
            "total_events": len(events),
            "events_by_type": {},
            "events_by_severity": {},
            "latest_event": events[-1] if events else None,
        }

        for event in events:
            evt_type = event.get("event_type", "unknown")
            severity = event.get("severity", "info")

            summary["events_by_type"][evt_type] = (
                summary["events_by_type"].get(evt_type, 0) + 1
            )
            summary["events_by_severity"][severity] = (
                summary["events_by_severity"].get(severity, 0) + 1
            )

        return summary
