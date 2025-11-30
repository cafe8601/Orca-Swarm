"""
Profile Manager - Handles loading and switching between system profiles.

Each profile defines:
- Default agents to activate
- Available tools
- Workflow templates
- System prompt customizations
- Domain-specific configurations
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

PROFILES_DIR = Path(__file__).parent / "configs"


@dataclass
class Profile:
    """Represents a system operation profile."""

    name: str
    display_name: str
    description: str

    # Agent configuration
    primary_agents: List[str] = field(default_factory=list)
    secondary_agents: List[str] = field(default_factory=list)
    disabled_agents: List[str] = field(default_factory=list)

    # Tool configuration
    enabled_tools: List[str] = field(default_factory=list)
    tool_priorities: Dict[str, int] = field(default_factory=dict)

    # Workflow templates
    workflow_templates: List[str] = field(default_factory=list)
    default_workflow: Optional[str] = None

    # System prompt additions
    system_prompt_prefix: str = ""
    system_prompt_suffix: str = ""

    # Domain-specific settings
    domain_settings: Dict[str, Any] = field(default_factory=dict)

    # Output preferences
    output_format: str = "markdown"  # markdown, latex, docx, html
    output_directory: str = "output"

    def get_all_agents(self) -> List[str]:
        """Get all enabled agents (primary + secondary)."""
        return self.primary_agents + self.secondary_agents

    def is_agent_enabled(self, agent_id: str) -> bool:
        """Check if an agent is enabled in this profile."""
        if agent_id in self.disabled_agents:
            return False
        return agent_id in self.primary_agents or agent_id in self.secondary_agents


class ProfileManager:
    """
    Manages system profiles for different use cases.

    Handles profile loading, switching, and configuration merging.
    """

    def __init__(self, profiles_dir: Optional[Path] = None):
        """
        Initialize profile manager.

        Args:
            profiles_dir: Directory containing profile YAML files
        """
        self.profiles_dir = profiles_dir or PROFILES_DIR
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

        self._profiles: Dict[str, Profile] = {}
        self._active_profile: Optional[Profile] = None

        # Load all available profiles
        self._load_profiles()

        logger.info(f"ProfileManager initialized with {len(self._profiles)} profiles")

    def _load_profiles(self):
        """Load all profile configurations from YAML files."""
        for yaml_file in self.profiles_dir.glob("*.yaml"):
            try:
                profile = self._load_profile_file(yaml_file)
                self._profiles[profile.name] = profile
                logger.info(f"Loaded profile: {profile.name}")
            except Exception as e:
                logger.error(f"Failed to load profile {yaml_file}: {e}")

    def _load_profile_file(self, file_path: Path) -> Profile:
        """Load a single profile from YAML file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        return Profile(
            name=data.get('name', file_path.stem),
            display_name=data.get('display_name', data.get('name', file_path.stem)),
            description=data.get('description', ''),
            primary_agents=data.get('primary_agents', []),
            secondary_agents=data.get('secondary_agents', []),
            disabled_agents=data.get('disabled_agents', []),
            enabled_tools=data.get('enabled_tools', []),
            tool_priorities=data.get('tool_priorities', {}),
            workflow_templates=data.get('workflow_templates', []),
            default_workflow=data.get('default_workflow'),
            system_prompt_prefix=data.get('system_prompt_prefix', ''),
            system_prompt_suffix=data.get('system_prompt_suffix', ''),
            domain_settings=data.get('domain_settings', {}),
            output_format=data.get('output_format', 'markdown'),
            output_directory=data.get('output_directory', 'output'),
        )

    def list_profiles(self) -> List[Dict[str, str]]:
        """List all available profiles."""
        return [
            {
                "name": p.name,
                "display_name": p.display_name,
                "description": p.description,
            }
            for p in self._profiles.values()
        ]

    def get_profile(self, name: str) -> Optional[Profile]:
        """Get a profile by name."""
        return self._profiles.get(name)

    def set_active_profile(self, name: str) -> bool:
        """
        Set the active profile.

        Args:
            name: Profile name to activate

        Returns:
            True if successful, False if profile not found
        """
        profile = self._profiles.get(name)
        if profile:
            self._active_profile = profile
            logger.info(f"Activated profile: {name}")
            return True
        logger.warning(f"Profile not found: {name}")
        return False

    def get_active_profile(self) -> Optional[Profile]:
        """Get the currently active profile."""
        return self._active_profile

    def get_active_profile_name(self) -> str:
        """Get the name of the active profile."""
        if self._active_profile:
            return self._active_profile.name
        return "none"

    def get_system_prompt_additions(self) -> Dict[str, str]:
        """Get system prompt additions from active profile."""
        if not self._active_profile:
            return {"prefix": "", "suffix": ""}
        return {
            "prefix": self._active_profile.system_prompt_prefix,
            "suffix": self._active_profile.system_prompt_suffix,
        }

    def get_recommended_agents(self, task: str) -> List[str]:
        """
        Get recommended agents for a task based on active profile.

        Args:
            task: Task description

        Returns:
            List of recommended agent IDs
        """
        if not self._active_profile:
            return []

        # Start with primary agents
        recommended = list(self._active_profile.primary_agents)

        # Add relevant secondary agents based on task keywords
        task_lower = task.lower()
        for agent in self._active_profile.secondary_agents:
            agent_lower = agent.lower()
            # Simple keyword matching
            if any(kw in task_lower for kw in agent_lower.split('-')):
                recommended.append(agent)

        return recommended

    def get_domain_setting(self, key: str, default: Any = None) -> Any:
        """Get a domain-specific setting from active profile."""
        if not self._active_profile:
            return default
        return self._active_profile.domain_settings.get(key, default)

    def create_profile(self, profile_data: Dict[str, Any]) -> Profile:
        """
        Create a new profile from data.

        Args:
            profile_data: Profile configuration dict

        Returns:
            Created Profile instance
        """
        profile = Profile(
            name=profile_data['name'],
            display_name=profile_data.get('display_name', profile_data['name']),
            description=profile_data.get('description', ''),
            primary_agents=profile_data.get('primary_agents', []),
            secondary_agents=profile_data.get('secondary_agents', []),
            disabled_agents=profile_data.get('disabled_agents', []),
            enabled_tools=profile_data.get('enabled_tools', []),
            tool_priorities=profile_data.get('tool_priorities', {}),
            workflow_templates=profile_data.get('workflow_templates', []),
            default_workflow=profile_data.get('default_workflow'),
            system_prompt_prefix=profile_data.get('system_prompt_prefix', ''),
            system_prompt_suffix=profile_data.get('system_prompt_suffix', ''),
            domain_settings=profile_data.get('domain_settings', {}),
            output_format=profile_data.get('output_format', 'markdown'),
            output_directory=profile_data.get('output_directory', 'output'),
        )

        self._profiles[profile.name] = profile

        # Save to file
        self._save_profile(profile)

        return profile

    def _save_profile(self, profile: Profile):
        """Save a profile to YAML file."""
        file_path = self.profiles_dir / f"{profile.name}.yaml"

        data = {
            'name': profile.name,
            'display_name': profile.display_name,
            'description': profile.description,
            'primary_agents': profile.primary_agents,
            'secondary_agents': profile.secondary_agents,
            'disabled_agents': profile.disabled_agents,
            'enabled_tools': profile.enabled_tools,
            'tool_priorities': profile.tool_priorities,
            'workflow_templates': profile.workflow_templates,
            'default_workflow': profile.default_workflow,
            'system_prompt_prefix': profile.system_prompt_prefix,
            'system_prompt_suffix': profile.system_prompt_suffix,
            'domain_settings': profile.domain_settings,
            'output_format': profile.output_format,
            'output_directory': profile.output_directory,
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

        logger.info(f"Saved profile to {file_path}")
