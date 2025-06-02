"""
AI-powered action suggestion system for Compound Action workflows.

This module provides intelligent suggestions for actions and workflows
based on natural language descriptions from users.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re
from enum import Enum

from ..catalog.builtin_actions import builtin_catalog, BuiltinAction
from ..templates.template_library import template_library, CompoundActionTemplate


class SuggestionType(Enum):
    """Types of suggestions that can be made."""
    BUILTIN_ACTION = "builtin_action"
    TEMPLATE = "template"
    WORKFLOW_PATTERN = "workflow_pattern"
    SCRIPT_SNIPPET = "script_snippet"


@dataclass
class ActionSuggestion:
    """Represents a suggested action or workflow."""
    suggestion_type: SuggestionType
    title: str
    description: str
    confidence: float  # 0.0 to 1.0
    details: Dict[str, Any]
    reasoning: str


class ActionSuggester:
    """
    AI-powered action suggester using keyword matching and pattern recognition.
    
    Provides intelligent suggestions for actions, templates, and workflows
    based on user descriptions.
    """
    
    def __init__(self):
        """Initialize the action suggester."""
        self._keywords = self._load_keyword_mappings()
        self._patterns = self._load_workflow_patterns()
    
    def _load_keyword_mappings(self) -> Dict[str, Dict[str, float]]:
        """Load keyword mappings for different action types."""
        return {
            # Communication keywords
            "communication": {
                "notify": 0.9, "notification": 0.9, "send": 0.8, "message": 0.8,
                "email": 0.7, "chat": 0.8, "alert": 0.8, "inform": 0.7,
                "communicate": 0.8, "tell": 0.6, "update": 0.6
            },
            
            # User management keywords
            "user_management": {
                "user": 0.8, "employee": 0.8, "person": 0.6, "profile": 0.7,
                "account": 0.7, "onboard": 0.9, "offboard": 0.9, "hire": 0.8,
                "terminate": 0.8, "create": 0.6, "update": 0.6, "manage": 0.7
            },
            
            # Security and access keywords
            "security_access": {
                "access": 0.9, "permission": 0.9, "grant": 0.8, "revoke": 0.8,
                "security": 0.8, "authorize": 0.8, "authenticate": 0.7,
                "role": 0.7, "privilege": 0.8, "rights": 0.7
            },
            
            # Ticket management keywords
            "ticket_management": {
                "ticket": 0.9, "issue": 0.8, "problem": 0.7, "request": 0.7,
                "support": 0.8, "help": 0.6, "escalate": 0.9, "resolve": 0.8,
                "close": 0.7, "assign": 0.7
            },
            
            # Approval workflow keywords
            "approval_workflow": {
                "approve": 0.9, "approval": 0.9, "manager": 0.8, "supervisor": 0.7,
                "authorize": 0.8, "review": 0.7, "sign": 0.6, "confirm": 0.7,
                "reject": 0.8, "decline": 0.7
            },
            
            # Data processing keywords
            "data_processing": {
                "data": 0.8, "process": 0.7, "validate": 0.8, "transform": 0.7,
                "report": 0.8, "generate": 0.7, "export": 0.7, "import": 0.7,
                "analyze": 0.7, "calculate": 0.6
            },
            
            # Integration keywords
            "integration": {
                "integrate": 0.9, "webhook": 0.9, "api": 0.8, "external": 0.7,
                "system": 0.6, "connect": 0.7, "sync": 0.8, "trigger": 0.8,
                "schedule": 0.8, "automate": 0.8
            }
        }
    
    def _load_workflow_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load common workflow patterns."""
        return {
            "user_lifecycle": {
                "keywords": ["onboard", "offboard", "hire", "terminate", "employee", "new user"],
                "templates": ["user_onboarding", "user_offboarding"],
                "description": "User lifecycle management workflows"
            },
            
            "access_management": {
                "keywords": ["access", "permission", "grant", "revoke", "security"],
                "templates": ["access_request"],
                "description": "Access and permission management workflows"
            },
            
            "incident_handling": {
                "keywords": ["incident", "emergency", "security", "breach", "urgent"],
                "templates": ["incident_response"],
                "description": "Incident response and emergency handling workflows"
            },
            
            "approval_processes": {
                "keywords": ["approve", "manager", "supervisor", "review", "authorize"],
                "templates": ["manager_approval", "multi_level_approval"],
                "description": "Approval and authorization workflows"
            },
            
            "support_operations": {
                "keywords": ["ticket", "support", "help", "escalate", "resolve"],
                "templates": ["ticket_escalation"],
                "description": "Support and ticketing workflows"
            },
            
            "data_operations": {
                "keywords": ["report", "data", "validate", "process", "generate"],
                "templates": ["data_validation", "report_generation"],
                "description": "Data processing and reporting workflows"
            }
        }
    
    def suggest_actions(self, description: str, max_suggestions: int = 5) -> List[ActionSuggestion]:
        """
        Suggest actions based on a natural language description.
        
        Args:
            description: User's description of what they want to accomplish
            max_suggestions: Maximum number of suggestions to return
            
        Returns:
            List of action suggestions sorted by confidence
        """
        suggestions = []
        description_lower = description.lower()
        
        # Get builtin action suggestions
        builtin_suggestions = self._suggest_builtin_actions(description_lower)
        suggestions.extend(builtin_suggestions)
        
        # Get template suggestions
        template_suggestions = self._suggest_templates(description_lower)
        suggestions.extend(template_suggestions)
        
        # Get workflow pattern suggestions
        pattern_suggestions = self._suggest_workflow_patterns(description_lower)
        suggestions.extend(pattern_suggestions)
        
        # Sort by confidence and return top suggestions
        suggestions.sort(key=lambda x: x.confidence, reverse=True)
        return suggestions[:max_suggestions]
    
    def _suggest_builtin_actions(self, description: str) -> List[ActionSuggestion]:
        """Suggest built-in actions based on description."""
        suggestions = []
        
        # Calculate scores for each category
        category_scores = {}
        for category, keywords in self._keywords.items():
            score = 0.0
            matched_keywords = []
            
            for keyword, weight in keywords.items():
                if keyword in description:
                    score += weight
                    matched_keywords.append(keyword)
            
            if score > 0:
                category_scores[category] = (score, matched_keywords)
        
        # Get actions for top-scoring categories
        for category, (score, keywords) in category_scores.items():
            if score >= 0.5:  # Minimum threshold
                category_map = {
                    "communication": "Communication",
                    "user_management": "User Management", 
                    "security_access": "Security & Access",
                    "ticket_management": "Ticket Management",
                    "approval_workflow": "Approval Workflow",
                    "data_processing": ["Data Retrieval", "Analytics & Reporting"],
                    "integration": "Integration & Automation"
                }
                
                mapped_categories = category_map.get(category, [])
                if isinstance(mapped_categories, str):
                    mapped_categories = [mapped_categories]
                
                for cat in mapped_categories:
                    actions = builtin_catalog.get_actions_by_category(cat)
                    for action in actions[:2]:  # Top 2 actions per category
                        confidence = min(0.9, score / len(keywords))
                        suggestions.append(ActionSuggestion(
                            suggestion_type=SuggestionType.BUILTIN_ACTION,
                            title=f"Use {action.name}",
                            description=action.description,
                            confidence=confidence,
                            details={
                                "action": action,
                                "matched_keywords": keywords
                            },
                            reasoning=f"Matched keywords: {', '.join(keywords)}"
                        ))
        
        return suggestions
    
    def _suggest_templates(self, description: str) -> List[ActionSuggestion]:
        """Suggest templates based on description."""
        suggestions = []
        
        # Search templates directly
        matching_templates = template_library.search_templates(description)
        
        for template in matching_templates[:3]:  # Top 3 templates
            # Calculate confidence based on keyword matches
            confidence = self._calculate_template_confidence(description, template)
            
            if confidence >= 0.3:  # Minimum threshold
                suggestions.append(ActionSuggestion(
                    suggestion_type=SuggestionType.TEMPLATE,
                    title=f"Use template: {template.name}",
                    description=template.description,
                    confidence=confidence,
                    details={
                        "template": template,
                        "use_case": template.use_case
                    },
                    reasoning=f"Template matches your use case: {template.use_case}"
                ))
        
        return suggestions
    
    def _suggest_workflow_patterns(self, description: str) -> List[ActionSuggestion]:
        """Suggest workflow patterns based on description."""
        suggestions = []
        
        for pattern_name, pattern_info in self._patterns.items():
            score = 0.0
            matched_keywords = []
            
            for keyword in pattern_info["keywords"]:
                if keyword in description:
                    score += 1.0
                    matched_keywords.append(keyword)
            
            if score > 0:
                confidence = min(0.8, score / len(pattern_info["keywords"]))
                
                suggestions.append(ActionSuggestion(
                    suggestion_type=SuggestionType.WORKFLOW_PATTERN,
                    title=f"Consider {pattern_info['description']}",
                    description=f"Pattern for {pattern_name.replace('_', ' ')} workflows",
                    confidence=confidence,
                    details={
                        "pattern": pattern_name,
                        "templates": pattern_info["templates"],
                        "matched_keywords": matched_keywords
                    },
                    reasoning=f"Detected {pattern_name.replace('_', ' ')} pattern from keywords: {', '.join(matched_keywords)}"
                ))
        
        return suggestions
    
    def _calculate_template_confidence(self, description: str, template: CompoundActionTemplate) -> float:
        """Calculate confidence score for a template match."""
        score = 0.0
        
        # Check description match
        desc_words = description.split()
        template_words = (template.description + " " + template.use_case).lower().split()
        
        matches = sum(1 for word in desc_words if word in template_words)
        if len(desc_words) > 0:
            score += (matches / len(desc_words)) * 0.7
        
        # Check category relevance
        category_keywords = {
            "User Management": ["user", "employee", "onboard", "offboard"],
            "Security & Access": ["access", "permission", "security", "grant"],
            "Support & Ticketing": ["ticket", "support", "incident", "escalate"],
            "Approval Workflow": ["approve", "manager", "review", "authorize"],
            "Data Processing": ["data", "report", "validate", "process"]
        }
        
        if template.category in category_keywords:
            category_matches = sum(1 for keyword in category_keywords[template.category] 
                                 if keyword in description)
            score += (category_matches / len(category_keywords[template.category])) * 0.3
        
        return min(1.0, score)


# Global action suggester instance
action_suggester = ActionSuggester()
