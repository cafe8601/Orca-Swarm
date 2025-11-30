"""
Profile-based system configuration for Multi-Agent Platform.

Provides specialized modes (developer, researcher, business, etc.)
while sharing the core orchestration engine.
"""

from .profile_manager import ProfileManager, Profile
from .workflow_templates import WorkflowTemplateRegistry

__all__ = ["ProfileManager", "Profile", "WorkflowTemplateRegistry"]
