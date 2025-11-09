"""
RAG (Retrieval-Augmented Generation) System.

Provides semantic search capabilities for code and experience retrieval
using vector embeddings (ChromaDB) based on refactoring.md design.
"""

import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class RAGSystem:
    """
    Retrieval-Augmented Generation System.

    Provides:
    - Code semantic search via vector embeddings
    - Experience-based learning and retrieval
    - Context augmentation for queries
    """

    def __init__(self, memory_manager, embedding_model=None, logger_instance=None):
        """
        Initialize RAG system.

        Args:
            memory_manager: MemoryManager instance
            embedding_model: Optional embedding model (defaults to sentence-transformers)
            logger_instance: Logger instance
        """
        self.memory = memory_manager
        self.logger = logger_instance or logger

        # Initialize embedding model
        try:
            if embedding_model:
                self.embedding_model = embedding_model
            else:
                from sentence_transformers import SentenceTransformer

                self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
                self.logger.info("Loaded sentence-transformers model: all-MiniLM-L6-v2")
        except ImportError:
            self.logger.warning(
                "sentence-transformers not installed. RAG features disabled."
            )
            self.embedding_model = None

        # Initialize ChromaDB collections
        try:
            import chromadb

            self.chroma_client = chromadb.Client()
            self.code_collection = self.chroma_client.get_or_create_collection(
                name="code_embeddings"
            )
            self.experience_collection = self.chroma_client.get_or_create_collection(
                name="experience_embeddings"
            )
            self.logger.info("ChromaDB collections initialized")
        except ImportError:
            self.logger.warning("ChromaDB not installed. Vector search disabled.")
            self.chroma_client = None
            self.code_collection = None
            self.experience_collection = None

    async def augment_query(
        self, user_query: str, context_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Augment user query with relevant context.

        Args:
            user_query: User query/request
            context_type: "auto", "code", "experience", or "project"

        Returns:
            {
                "original_query": str,
                "augmented_query": str,
                "context": {
                    "relevant_code": [...],
                    "similar_experiences": [...],
                    "project_info": {...},
                    "conversation_context": [...]
                }
            }
        """
        self.logger.info(f"Augmenting query: {user_query[:100]}...")

        context = {}

        # 1. Conversation context (Working Memory)
        try:
            context["conversation_context"] = self.memory.get_recent_conversation(count=5)
        except AttributeError:
            context["conversation_context"] = []

        # 2. Project context inference
        project_info = await self._infer_project_context(user_query)
        if project_info:
            context["project_info"] = project_info

        # 3. Codebase search (Vector DB)
        if context_type in ["auto", "code"] and self.code_collection:
            relevant_code = self.search_code(user_query, limit=3)
            context["relevant_code"] = relevant_code

        # 4. Similar experience search
        if context_type in ["auto", "experience"] and self.experience_collection:
            similar_experiences = self.search_similar_experiences(user_query, limit=3)
            context["similar_experiences"] = similar_experiences

        # 5. Learning patterns search
        try:
            patterns = self.memory.query_similar_patterns(user_query, limit=3)
            context["learned_patterns"] = patterns
        except AttributeError:
            context["learned_patterns"] = []

        # 6. Build augmented query
        augmented_query = self._build_augmented_query(user_query, context)

        return {
            "original_query": user_query,
            "augmented_query": augmented_query,
            "context": context,
        }

    async def _infer_project_context(self, query: str) -> Optional[Dict]:
        """Infer project context from query."""
        keywords = ["blog", "project", "app", "api", "webapp", "platform"]

        for keyword in keywords:
            if keyword.lower() in query.lower():
                # Find recently accessed project
                try:
                    project = self.memory.get_project(name=f"{keyword}-platform")
                    if project:
                        return project
                except AttributeError:
                    pass

        return None

    def _build_augmented_query(self, original: str, context: Dict[str, Any]) -> str:
        """Build augmented query with context."""
        parts = [f"User Request: {original}\n"]

        # Project context
        if context.get("project_info"):
            proj = context["project_info"]
            parts.append("\nProject Context:")
            parts.append(f"- Name: {proj.get('name', 'Unknown')}")
            parts.append(f"- Tech Stack: {', '.join(proj.get('tech_stack', []))}")

        # Recent conversation
        if context.get("conversation_context"):
            parts.append("\nRecent Conversation:")
            for conv in context["conversation_context"][-3:]:
                parts.append(f"- {conv['role']}: {conv['content'][:100]}")

        # Relevant code
        if context.get("relevant_code"):
            parts.append("\nRelevant Code:")
            for code in context["relevant_code"][:2]:
                parts.append(f"- {code['path']}: {code['content'][:200]}...")

        # Similar experiences
        if context.get("similar_experiences"):
            parts.append("\nSimilar Past Experiences:")
            for exp in context["similar_experiences"]:
                parts.append(
                    f"- {exp['description'][:80]} (similarity: {exp['similarity']:.2f})"
                )

        # Learned patterns
        if context.get("learned_patterns"):
            parts.append("\nLearned Patterns:")
            for pattern in context["learned_patterns"]:
                parts.append(
                    f"- {pattern['context']}: {pattern['action_taken']} "
                    f"(success: {pattern.get('success', False)})"
                )

        return "\n".join(parts)

    def index_code(self, code_path: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Index code with embeddings.

        Args:
            code_path: Relative code path
            content: Code content
            metadata: Optional metadata
        """
        if not self.embedding_model or not self.code_collection:
            return

        try:
            embedding = self.embedding_model.encode(content).tolist()

            self.code_collection.add(
                ids=[code_path],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata or {}],
            )

            self.logger.debug(f"Indexed code: {code_path}")
        except Exception as exc:
            self.logger.error(f"Failed to index code {code_path}: {exc}")

    def index_codebase(self, codebase_path: Path) -> None:
        """
        Index entire codebase.

        Args:
            codebase_path: Path to codebase directory
        """
        self.logger.info(f"Indexing codebase: {codebase_path}")

        if not self.embedding_model:
            self.logger.warning("Embedding model not available, skipping indexing")
            return

        # Supported file extensions
        extensions = [".py", ".js", ".ts", ".tsx", ".vue", ".jsx"]

        for ext in extensions:
            for file_path in codebase_path.rglob(f"*{ext}"):
                # Skip certain directories
                if any(
                    skip in str(file_path)
                    for skip in ["node_modules", "__pycache__", ".git", "venv"]
                ):
                    continue

                try:
                    content = file_path.read_text(encoding="utf-8")
                    relative_path = str(file_path.relative_to(codebase_path))

                    self.index_code(
                        code_path=relative_path,
                        content=content,
                        metadata={
                            "file_type": ext,
                            "size": len(content),
                            "indexed_at": datetime.now(timezone.utc).isoformat(),
                        },
                    )
                except Exception as exc:
                    self.logger.warning(f"Failed to index {file_path}: {exc}")

        self.logger.info("Codebase indexing complete")

    def search_code(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Semantic code search.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching code snippets
        """
        if not self.embedding_model or not self.code_collection:
            return []

        try:
            query_embedding = self.embedding_model.encode(query).tolist()

            results = self.code_collection.query(
                query_embeddings=[query_embedding], n_results=limit
            )

            search_results = []
            if results and results.get("ids"):
                for i in range(len(results["ids"][0])):
                    search_results.append(
                        {
                            "path": results["ids"][0][i],
                            "content": results["documents"][0][i],
                            "distance": (
                                results["distances"][0][i]
                                if "distances" in results
                                else 0
                            ),
                            "metadata": results["metadatas"][0][i],
                        }
                    )

            return search_results

        except Exception as exc:
            self.logger.error(f"Code search failed: {exc}")
            return []

    def index_experience(self, experience: Dict[str, Any]) -> None:
        """
        Index workflow experience.

        Args:
            experience: Experience dict with id, goal, description, success, duration
        """
        if not self.embedding_model or not self.experience_collection:
            return

        try:
            # Convert experience to text
            text = f"{experience['goal']} - {experience['description']}"
            embedding = self.embedding_model.encode(text).tolist()

            self.experience_collection.add(
                ids=[experience["experience_id"]],
                embeddings=[embedding],
                documents=[text],
                metadatas=[
                    {
                        "goal": experience["goal"],
                        "success": experience.get("success", False),
                        "duration": experience.get("duration", 0),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                ],
            )

            self.logger.debug(f"Indexed experience: {experience['experience_id']}")

        except Exception as exc:
            self.logger.error(f"Failed to index experience: {exc}")

    def search_similar_experiences(self, query: str, limit: int = 3) -> List[Dict]:
        """
        Search similar past experiences.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of similar experiences
        """
        if not self.embedding_model or not self.experience_collection:
            return []

        try:
            query_embedding = self.embedding_model.encode(query).tolist()

            results = self.experience_collection.query(
                query_embeddings=[query_embedding], n_results=limit
            )

            experiences = []
            if results and results.get("ids"):
                for i in range(len(results["ids"][0])):
                    experiences.append(
                        {
                            "experience_id": results["ids"][0][i],
                            "description": results["documents"][0][i],
                            "metadata": results["metadatas"][0][i],
                            "similarity": 1 - results["distances"][0][i],  # Distance to similarity
                        }
                    )

            return experiences

        except Exception as exc:
            self.logger.error(f"Experience search failed: {exc}")
            return []

    async def retrieve_for_task(
        self, task_description: str, expert_type: str
    ) -> Dict[str, Any]:
        """
        Retrieve context for specific task and expert type.

        Args:
            task_description: Task description
            expert_type: Expert type (e.g., "BackendExpert")

        Returns:
            Dict with relevant context
        """
        context = {}

        # Expert-specific code search
        if expert_type == "BackendExpert":
            context["relevant_code"] = self.search_code(
                f"backend API {task_description}", limit=5
            )
        elif expert_type == "FrontendExpert":
            context["relevant_code"] = self.search_code(
                f"frontend component {task_description}", limit=5
            )
        else:
            context["relevant_code"] = self.search_code(task_description, limit=3)

        # Similar task experiences
        context["similar_tasks"] = self.search_similar_experiences(
            f"{expert_type} {task_description}", limit=3
        )

        return context
