"""
Workflow Template Registry - Predefined workflow templates for different use cases.

Each template defines:
- Steps and their order
- Required agents for each step
- Expected outputs
- Quality gates
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class WorkflowStepType(Enum):
    """Types of workflow steps."""
    RESEARCH = "research"
    ANALYSIS = "analysis"
    PLANNING = "planning"
    IMPLEMENTATION = "implementation"
    REVIEW = "review"
    SYNTHESIS = "synthesis"
    VALIDATION = "validation"
    OUTPUT = "output"


@dataclass
class WorkflowStep:
    """Represents a single step in a workflow."""

    name: str
    step_type: WorkflowStepType
    description: str
    required_agents: List[str] = field(default_factory=list)
    optional_agents: List[str] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    quality_gates: Dict[str, Any] = field(default_factory=dict)
    parallel: bool = False
    timeout_seconds: int = 300


@dataclass
class WorkflowTemplate:
    """Represents a complete workflow template."""

    name: str
    display_name: str
    description: str
    category: str  # developer, researcher, business
    steps: List[WorkflowStep] = field(default_factory=list)
    estimated_duration_minutes: int = 30
    complexity: str = "medium"  # simple, medium, complex

    def get_all_required_agents(self) -> List[str]:
        """Get all unique required agents across all steps."""
        agents = set()
        for step in self.steps:
            agents.update(step.required_agents)
        return list(agents)


class WorkflowTemplateRegistry:
    """
    Registry of predefined workflow templates.

    Provides templates for common tasks in different domains.
    """

    def __init__(self):
        self._templates: Dict[str, WorkflowTemplate] = {}
        self._load_default_templates()
        logger.info(f"WorkflowTemplateRegistry initialized with {len(self._templates)} templates")

    def _load_default_templates(self):
        """Load all default workflow templates."""
        # Developer templates
        self._register_developer_templates()
        # Researcher templates
        self._register_researcher_templates()
        # Business templates
        self._register_business_templates()

    def _register_developer_templates(self):
        """Register developer-focused workflow templates."""

        # Feature Development
        self.register(WorkflowTemplate(
            name="feature_development",
            display_name="Feature Development",
            description="Complete workflow for implementing a new feature",
            category="developer",
            estimated_duration_minutes=60,
            complexity="medium",
            steps=[
                WorkflowStep(
                    name="requirements_analysis",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Analyze and clarify feature requirements",
                    required_agents=["requirements-analyst"],
                    outputs=["requirements_spec"],
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="architecture_design",
                    step_type=WorkflowStepType.PLANNING,
                    description="Design the feature architecture",
                    required_agents=["system-architect"],
                    inputs=["requirements_spec"],
                    outputs=["architecture_design"],
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="implementation",
                    step_type=WorkflowStepType.IMPLEMENTATION,
                    description="Implement the feature",
                    required_agents=["python-expert", "backend-architect"],
                    optional_agents=["frontend-architect"],
                    inputs=["architecture_design"],
                    outputs=["source_code"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="testing",
                    step_type=WorkflowStepType.VALIDATION,
                    description="Write and run tests",
                    required_agents=["quality-engineer"],
                    inputs=["source_code"],
                    outputs=["test_results"],
                    quality_gates={"coverage_threshold": 0.8},
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="code_review",
                    step_type=WorkflowStepType.REVIEW,
                    description="Review code quality and standards",
                    required_agents=["refactoring-expert"],
                    inputs=["source_code", "test_results"],
                    outputs=["review_report"],
                    timeout_seconds=300
                )
            ]
        ))

        # Bug Fix
        self.register(WorkflowTemplate(
            name="bug_fix",
            display_name="Bug Fix",
            description="Systematic approach to fixing bugs",
            category="developer",
            estimated_duration_minutes=30,
            complexity="simple",
            steps=[
                WorkflowStep(
                    name="root_cause_analysis",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Identify the root cause of the bug",
                    required_agents=["root-cause-analyst"],
                    outputs=["root_cause_report"],
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="fix_implementation",
                    step_type=WorkflowStepType.IMPLEMENTATION,
                    description="Implement the bug fix",
                    required_agents=["python-expert"],
                    inputs=["root_cause_report"],
                    outputs=["fix_code"],
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="regression_testing",
                    step_type=WorkflowStepType.VALIDATION,
                    description="Test to ensure fix works and no regressions",
                    required_agents=["quality-engineer"],
                    inputs=["fix_code"],
                    outputs=["test_results"],
                    timeout_seconds=300
                )
            ]
        ))

        # Code Review
        self.register(WorkflowTemplate(
            name="code_review",
            display_name="Code Review",
            description="Comprehensive code review workflow",
            category="developer",
            estimated_duration_minutes=20,
            complexity="simple",
            steps=[
                WorkflowStep(
                    name="static_analysis",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Run static analysis tools",
                    required_agents=["quality-engineer"],
                    outputs=["static_analysis_report"],
                    timeout_seconds=180
                ),
                WorkflowStep(
                    name="quality_review",
                    step_type=WorkflowStepType.REVIEW,
                    description="Review code quality and patterns",
                    required_agents=["refactoring-expert"],
                    inputs=["static_analysis_report"],
                    outputs=["quality_report"],
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="security_review",
                    step_type=WorkflowStepType.REVIEW,
                    description="Review security considerations",
                    required_agents=["security-engineer"],
                    outputs=["security_report"],
                    parallel=True,
                    timeout_seconds=300
                )
            ]
        ))

        # Refactoring
        self.register(WorkflowTemplate(
            name="refactoring",
            display_name="Code Refactoring",
            description="Safe code refactoring with testing",
            category="developer",
            estimated_duration_minutes=45,
            complexity="medium",
            steps=[
                WorkflowStep(
                    name="analysis",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Analyze code for refactoring opportunities",
                    required_agents=["refactoring-expert"],
                    outputs=["refactoring_plan"],
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="baseline_tests",
                    step_type=WorkflowStepType.VALIDATION,
                    description="Ensure existing tests pass",
                    required_agents=["quality-engineer"],
                    outputs=["baseline_results"],
                    timeout_seconds=180
                ),
                WorkflowStep(
                    name="refactoring",
                    step_type=WorkflowStepType.IMPLEMENTATION,
                    description="Apply refactoring changes",
                    required_agents=["refactoring-expert", "python-expert"],
                    inputs=["refactoring_plan"],
                    outputs=["refactored_code"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="verification",
                    step_type=WorkflowStepType.VALIDATION,
                    description="Verify all tests still pass",
                    required_agents=["quality-engineer"],
                    inputs=["refactored_code"],
                    outputs=["verification_results"],
                    quality_gates={"all_tests_pass": True},
                    timeout_seconds=300
                )
            ]
        ))

    def _register_researcher_templates(self):
        """Register researcher-focused workflow templates."""

        # Literature Review
        self.register(WorkflowTemplate(
            name="literature_review",
            display_name="Literature Review",
            description="Systematic literature review workflow",
            category="researcher",
            estimated_duration_minutes=120,
            complexity="complex",
            steps=[
                WorkflowStep(
                    name="search_strategy",
                    step_type=WorkflowStepType.PLANNING,
                    description="Define search strategy and keywords",
                    required_agents=["deep-research-agent"],
                    outputs=["search_strategy"],
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="source_discovery",
                    step_type=WorkflowStepType.RESEARCH,
                    description="Search and collect relevant sources",
                    required_agents=["deep-research-agent"],
                    inputs=["search_strategy"],
                    outputs=["source_collection"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="source_screening",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Screen and filter sources for relevance",
                    required_agents=["deep-research-agent"],
                    inputs=["source_collection"],
                    outputs=["filtered_sources"],
                    quality_gates={"min_sources": 10},
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="content_analysis",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Analyze and extract key information",
                    required_agents=["deep-research-agent", "root-cause-analyst"],
                    inputs=["filtered_sources"],
                    outputs=["analysis_results"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="synthesis",
                    step_type=WorkflowStepType.SYNTHESIS,
                    description="Synthesize findings into coherent narrative",
                    required_agents=["technical-writer"],
                    inputs=["analysis_results"],
                    outputs=["literature_review_draft"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="review_formatting",
                    step_type=WorkflowStepType.OUTPUT,
                    description="Format and finalize the review",
                    required_agents=["technical-writer"],
                    inputs=["literature_review_draft"],
                    outputs=["final_literature_review"],
                    timeout_seconds=300
                )
            ]
        ))

        # Paper Writing
        self.register(WorkflowTemplate(
            name="paper_writing",
            display_name="Academic Paper Writing",
            description="Complete academic paper writing workflow",
            category="researcher",
            estimated_duration_minutes=180,
            complexity="complex",
            steps=[
                WorkflowStep(
                    name="outline_creation",
                    step_type=WorkflowStepType.PLANNING,
                    description="Create paper outline and structure",
                    required_agents=["technical-writer"],
                    outputs=["paper_outline"],
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="background_research",
                    step_type=WorkflowStepType.RESEARCH,
                    description="Research background and related work",
                    required_agents=["deep-research-agent"],
                    inputs=["paper_outline"],
                    outputs=["background_content"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="methodology_section",
                    step_type=WorkflowStepType.IMPLEMENTATION,
                    description="Write methodology section",
                    required_agents=["technical-writer"],
                    inputs=["paper_outline"],
                    outputs=["methodology_draft"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="results_analysis",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Analyze and present results",
                    required_agents=["root-cause-analyst", "technical-writer"],
                    outputs=["results_draft"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="discussion_synthesis",
                    step_type=WorkflowStepType.SYNTHESIS,
                    description="Write discussion and conclusions",
                    required_agents=["technical-writer"],
                    inputs=["background_content", "results_draft"],
                    outputs=["discussion_draft"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="paper_assembly",
                    step_type=WorkflowStepType.OUTPUT,
                    description="Assemble and format final paper",
                    required_agents=["technical-writer"],
                    inputs=["methodology_draft", "results_draft", "discussion_draft"],
                    outputs=["final_paper"],
                    timeout_seconds=600
                )
            ]
        ))

        # Technical Report
        self.register(WorkflowTemplate(
            name="technical_report",
            display_name="Technical Report",
            description="Technical documentation and reporting",
            category="researcher",
            estimated_duration_minutes=90,
            complexity="medium",
            steps=[
                WorkflowStep(
                    name="scope_definition",
                    step_type=WorkflowStepType.PLANNING,
                    description="Define report scope and objectives",
                    required_agents=["requirements-analyst"],
                    outputs=["report_scope"],
                    timeout_seconds=300
                ),
                WorkflowStep(
                    name="technical_analysis",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Perform technical analysis",
                    required_agents=["system-architect", "root-cause-analyst"],
                    inputs=["report_scope"],
                    outputs=["technical_findings"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="report_writing",
                    step_type=WorkflowStepType.IMPLEMENTATION,
                    description="Write the technical report",
                    required_agents=["technical-writer"],
                    inputs=["technical_findings"],
                    outputs=["report_draft"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="review_finalize",
                    step_type=WorkflowStepType.REVIEW,
                    description="Review and finalize report",
                    required_agents=["quality-engineer"],
                    inputs=["report_draft"],
                    outputs=["final_report"],
                    timeout_seconds=300
                )
            ]
        ))

    def _register_business_templates(self):
        """Register business-focused workflow templates."""

        # Market Analysis
        self.register(WorkflowTemplate(
            name="market_analysis",
            display_name="Market Analysis",
            description="Comprehensive market analysis workflow",
            category="business",
            estimated_duration_minutes=120,
            complexity="complex",
            steps=[
                WorkflowStep(
                    name="market_research",
                    step_type=WorkflowStepType.RESEARCH,
                    description="Research market size, trends, and dynamics",
                    required_agents=["deep-research-agent"],
                    outputs=["market_data"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="competitive_analysis",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Analyze competitors and market positioning",
                    required_agents=["deep-research-agent", "business-panel-experts"],
                    inputs=["market_data"],
                    outputs=["competitive_insights"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="expert_panel_review",
                    step_type=WorkflowStepType.REVIEW,
                    description="Multi-expert strategic analysis",
                    required_agents=["business-panel-experts"],
                    inputs=["market_data", "competitive_insights"],
                    outputs=["expert_analysis"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="synthesis_recommendations",
                    step_type=WorkflowStepType.SYNTHESIS,
                    description="Synthesize findings and recommendations",
                    required_agents=["technical-writer"],
                    inputs=["expert_analysis"],
                    outputs=["market_report"],
                    timeout_seconds=600
                )
            ]
        ))

        # Strategic Plan
        self.register(WorkflowTemplate(
            name="strategic_plan",
            display_name="Strategic Planning",
            description="Strategic planning and roadmap development",
            category="business",
            estimated_duration_minutes=150,
            complexity="complex",
            steps=[
                WorkflowStep(
                    name="situation_analysis",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Analyze current situation (SWOT, etc.)",
                    required_agents=["business-panel-experts"],
                    outputs=["situation_report"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="vision_goals",
                    step_type=WorkflowStepType.PLANNING,
                    description="Define vision, mission, and goals",
                    required_agents=["business-panel-experts", "requirements-analyst"],
                    inputs=["situation_report"],
                    outputs=["strategic_goals"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="strategy_development",
                    step_type=WorkflowStepType.PLANNING,
                    description="Develop strategic initiatives",
                    required_agents=["business-panel-experts"],
                    inputs=["strategic_goals"],
                    outputs=["strategic_initiatives"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="roadmap_creation",
                    step_type=WorkflowStepType.IMPLEMENTATION,
                    description="Create implementation roadmap",
                    required_agents=["system-architect", "technical-writer"],
                    inputs=["strategic_initiatives"],
                    outputs=["implementation_roadmap"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="document_assembly",
                    step_type=WorkflowStepType.OUTPUT,
                    description="Assemble strategic plan document",
                    required_agents=["technical-writer"],
                    inputs=["situation_report", "strategic_goals", "implementation_roadmap"],
                    outputs=["strategic_plan_document"],
                    timeout_seconds=600
                )
            ]
        ))

        # Business Report
        self.register(WorkflowTemplate(
            name="business_report",
            display_name="Business Report",
            description="Professional business reporting",
            category="business",
            estimated_duration_minutes=60,
            complexity="medium",
            steps=[
                WorkflowStep(
                    name="data_gathering",
                    step_type=WorkflowStepType.RESEARCH,
                    description="Gather relevant business data",
                    required_agents=["deep-research-agent"],
                    outputs=["business_data"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="analysis",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Analyze data and identify insights",
                    required_agents=["root-cause-analyst", "business-panel-experts"],
                    inputs=["business_data"],
                    outputs=["analysis_results"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="report_writing",
                    step_type=WorkflowStepType.IMPLEMENTATION,
                    description="Write the business report",
                    required_agents=["technical-writer"],
                    inputs=["analysis_results"],
                    outputs=["report_draft"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="executive_summary",
                    step_type=WorkflowStepType.OUTPUT,
                    description="Create executive summary and finalize",
                    required_agents=["technical-writer"],
                    inputs=["report_draft"],
                    outputs=["final_report"],
                    timeout_seconds=300
                )
            ]
        ))

        # SWOT Analysis
        self.register(WorkflowTemplate(
            name="swot_analysis",
            display_name="SWOT Analysis",
            description="Comprehensive SWOT analysis workflow",
            category="business",
            estimated_duration_minutes=45,
            complexity="simple",
            steps=[
                WorkflowStep(
                    name="strengths_weaknesses",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Analyze internal strengths and weaknesses",
                    required_agents=["business-panel-experts"],
                    outputs=["internal_analysis"],
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="opportunities_threats",
                    step_type=WorkflowStepType.ANALYSIS,
                    description="Analyze external opportunities and threats",
                    required_agents=["business-panel-experts", "deep-research-agent"],
                    outputs=["external_analysis"],
                    parallel=True,
                    timeout_seconds=600
                ),
                WorkflowStep(
                    name="synthesis",
                    step_type=WorkflowStepType.SYNTHESIS,
                    description="Synthesize SWOT matrix and strategies",
                    required_agents=["business-panel-experts"],
                    inputs=["internal_analysis", "external_analysis"],
                    outputs=["swot_report"],
                    timeout_seconds=600
                )
            ]
        ))

    def register(self, template: WorkflowTemplate):
        """Register a workflow template."""
        self._templates[template.name] = template
        logger.debug(f"Registered workflow template: {template.name}")

    def get(self, name: str) -> Optional[WorkflowTemplate]:
        """Get a workflow template by name."""
        return self._templates.get(name)

    def list_templates(self, category: Optional[str] = None) -> List[Dict[str, str]]:
        """List all available templates, optionally filtered by category."""
        templates = []
        for template in self._templates.values():
            if category is None or template.category == category:
                templates.append({
                    "name": template.name,
                    "display_name": template.display_name,
                    "description": template.description,
                    "category": template.category,
                    "complexity": template.complexity,
                    "estimated_duration": f"{template.estimated_duration_minutes} minutes"
                })
        return templates

    def get_templates_for_profile(self, profile_name: str) -> List[WorkflowTemplate]:
        """Get all templates suitable for a profile."""
        category_map = {
            "developer": "developer",
            "researcher": "researcher",
            "business": "business"
        }
        category = category_map.get(profile_name)
        if not category:
            return list(self._templates.values())

        return [t for t in self._templates.values() if t.category == category]

    def get_required_agents(self, template_name: str) -> List[str]:
        """Get all required agents for a workflow template."""
        template = self.get(template_name)
        if template:
            return template.get_all_required_agents()
        return []
