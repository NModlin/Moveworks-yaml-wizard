"""
AI assistance module for intelligent action suggestions and workflow generation.

This module provides NLP-based suggestions for actions and workflows
based on user descriptions.
"""

from .action_suggester import ActionSuggester, ActionSuggestion

__all__ = [
    "ActionSuggester",
    "ActionSuggestion",
]
