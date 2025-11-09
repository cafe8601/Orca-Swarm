"""
Custom exception hierarchy for Big Three Agents.

Provides specific exceptions for better error handling and debugging
in production environments.
"""


class BigThreeError(Exception):
    """Base exception for all Big Three Agents errors."""

    pass


# ============================================================================
# Agent Errors
# ============================================================================


class AgentError(BigThreeError):
    """Base exception for agent-related errors."""

    pass


class AgentCreationError(AgentError):
    """Failed to create agent instance."""

    pass


class AgentExecutionError(AgentError):
    """Agent execution failed."""

    pass


class AgentNotFoundError(AgentError):
    """Requested agent not found in registry."""

    pass


class AgentTimeoutError(AgentError):
    """Agent execution timed out."""

    pass


class AgentSessionError(AgentError):
    """Agent session management error."""

    pass


# ============================================================================
# Workflow Errors
# ============================================================================


class WorkflowError(BigThreeError):
    """Base exception for workflow-related errors."""

    pass


class WorkflowPlanningError(WorkflowError):
    """Workflow planning failed."""

    pass


class WorkflowExecutionError(WorkflowError):
    """Workflow execution failed."""

    pass


class WorkflowValidationError(WorkflowError):
    """Workflow validation failed."""

    pass


class WorkflowTaskError(WorkflowError):
    """Individual task within workflow failed."""

    pass


# ============================================================================
# Memory Errors
# ============================================================================


class MemoryError(BigThreeError):
    """Base exception for memory system errors."""

    pass


class MemoryStoreError(MemoryError):
    """Failed to store data in memory system."""

    pass


class MemoryRetrieveError(MemoryError):
    """Failed to retrieve data from memory system."""

    pass


class MemoryCorruptionError(MemoryError):
    """Memory data is corrupted or invalid."""

    pass


# ============================================================================
# Security Errors
# ============================================================================


class SecurityError(BigThreeError):
    """Base exception for security-related errors."""

    pass


class AuthenticationError(SecurityError):
    """Authentication failed."""

    pass


class AuthorizationError(SecurityError):
    """User not authorized for requested operation."""

    pass


class ValidationError(SecurityError):
    """Input validation failed."""

    pass


class PathTraversalError(SecurityError):
    """Path traversal attack detected."""

    pass


# ============================================================================
# Configuration Errors
# ============================================================================


class ConfigurationError(BigThreeError):
    """Configuration error or missing required configuration."""

    pass


class APIKeyMissingError(ConfigurationError):
    """Required API key is missing."""

    pass


class InvalidConfigurationError(ConfigurationError):
    """Configuration value is invalid."""

    pass


# ============================================================================
# External Service Errors
# ============================================================================


class ExternalServiceError(BigThreeError):
    """Base exception for external service (API) errors."""

    pass


class OpenAIError(ExternalServiceError):
    """OpenAI API error."""

    pass


class ClaudeError(ExternalServiceError):
    """Claude/Anthropic API error."""

    pass


class GeminiError(ExternalServiceError):
    """Google Gemini API error."""

    pass


class WebSocketError(ExternalServiceError):
    """WebSocket connection error."""

    pass


# ============================================================================
# Pool Errors
# ============================================================================


class PoolError(BigThreeError):
    """Base exception for Agent Pool errors."""

    pass


class ExpertNotFoundError(PoolError):
    """Requested expert type not found in pool."""

    pass


class PoolExhaustedError(PoolError):
    """Agent pool exhausted, cannot allocate more instances."""

    pass


class InstanceError(PoolError):
    """Agent instance error."""

    pass


# ============================================================================
# RAG Errors
# ============================================================================


class RAGError(BigThreeError):
    """Base exception for RAG system errors."""

    pass


class EmbeddingError(RAGError):
    """Failed to generate embeddings."""

    pass


class VectorSearchError(RAGError):
    """Vector search operation failed."""

    pass


class IndexingError(RAGError):
    """Code or experience indexing failed."""

    pass


# ============================================================================
# Browser Errors
# ============================================================================


class BrowserError(BigThreeError):
    """Base exception for browser automation errors."""

    pass


class BrowserLaunchError(BrowserError):
    """Failed to launch browser."""

    pass


class BrowserNavigationError(BrowserError):
    """Browser navigation failed."""

    pass


class BrowserActionError(BrowserError):
    """Browser action (click, type, etc.) failed."""

    pass


# ============================================================================
# Learning Errors
# ============================================================================


class LearningError(BigThreeError):
    """Base exception for learning system errors."""

    pass


class OutcomeTrackingError(LearningError):
    """Failed to track outcome."""

    pass


class PatternAnalysisError(LearningError):
    """Pattern analysis failed."""

    pass
