"""
Built-in action catalog for Moveworks Compound Actions.

This module provides a comprehensive catalog of built-in Moveworks actions
with their expected input arguments and descriptions.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ActionParameter:
    """Represents a parameter for a built-in action."""
    name: str
    type: str
    required: bool
    description: str
    example: Optional[str] = None


@dataclass
class BuiltinAction:
    """Represents a built-in Moveworks action."""
    name: str
    description: str
    category: str
    parameters: List[ActionParameter]
    example_usage: Optional[str] = None


class BuiltinActionCatalog:
    """
    Catalog of built-in Moveworks actions.
    
    Provides information about available actions, their parameters,
    and usage examples for the wizard.
    """
    
    def __init__(self):
        """Initialize the catalog with built-in actions."""
        self._actions = self._load_builtin_actions()
    
    def _load_builtin_actions(self) -> Dict[str, BuiltinAction]:
        """Load the catalog of built-in actions."""
        actions = {}
        
        # Communication actions
        actions["mw.send_plaintext_chat_notification"] = BuiltinAction(
            name="mw.send_plaintext_chat_notification",
            description="Send a plain text chat notification to a user",
            category="Communication",
            parameters=[
                ActionParameter(
                    name="user_record_id",
                    type="string",
                    required=True,
                    description="The record ID of the user to notify",
                    example="data.user_info.record_id"
                ),
                ActionParameter(
                    name="message",
                    type="string", 
                    required=True,
                    description="The message to send",
                    example="Your request has been processed successfully."
                )
            ],
            example_usage="Send notifications to users about request status"
        )
        
        actions["mw.send_rich_chat_notification"] = BuiltinAction(
            name="mw.send_rich_chat_notification",
            description="Send a rich formatted chat notification with cards and buttons",
            category="Communication",
            parameters=[
                ActionParameter(
                    name="user_record_id",
                    type="string",
                    required=True,
                    description="The record ID of the user to notify",
                    example="data.user_info.record_id"
                ),
                ActionParameter(
                    name="card_content",
                    type="object",
                    required=True,
                    description="Rich card content with formatting",
                    example="data.formatted_card"
                )
            ],
            example_usage="Send formatted notifications with interactive elements"
        )
        
        # User management actions
        actions["mw.get_user_details"] = BuiltinAction(
            name="mw.get_user_details",
            description="Retrieve detailed information about a user",
            category="User Management",
            parameters=[
                ActionParameter(
                    name="user_id",
                    type="string",
                    required=True,
                    description="The user ID to look up",
                    example="data.employee_id"
                )
            ],
            example_usage="Get user information for processing requests"
        )
        
        actions["mw.update_user_profile"] = BuiltinAction(
            name="mw.update_user_profile",
            description="Update user profile information",
            category="User Management",
            parameters=[
                ActionParameter(
                    name="user_record_id",
                    type="string",
                    required=True,
                    description="The record ID of the user to update",
                    example="data.user_info.record_id"
                ),
                ActionParameter(
                    name="profile_updates",
                    type="object",
                    required=True,
                    description="Object containing profile fields to update",
                    example="data.profile_changes"
                )
            ],
            example_usage="Update user information in the system"
        )
        
        # Ticket management actions
        actions["mw.create_ticket"] = BuiltinAction(
            name="mw.create_ticket",
            description="Create a new support ticket",
            category="Ticket Management",
            parameters=[
                ActionParameter(
                    name="title",
                    type="string",
                    required=True,
                    description="The ticket title",
                    example="data.issue_summary"
                ),
                ActionParameter(
                    name="description",
                    type="string",
                    required=True,
                    description="Detailed description of the issue",
                    example="data.issue_details"
                ),
                ActionParameter(
                    name="requestor_id",
                    type="string",
                    required=True,
                    description="ID of the user requesting support",
                    example="meta_info.requestor.employee_id"
                ),
                ActionParameter(
                    name="priority",
                    type="string",
                    required=False,
                    description="Ticket priority level",
                    example="Medium"
                )
            ],
            example_usage="Create tickets for issues that require manual intervention"
        )
        
        actions["mw.update_ticket_status"] = BuiltinAction(
            name="mw.update_ticket_status",
            description="Update the status of an existing ticket",
            category="Ticket Management",
            parameters=[
                ActionParameter(
                    name="ticket_id",
                    type="string",
                    required=True,
                    description="The ID of the ticket to update",
                    example="data.ticket_number"
                ),
                ActionParameter(
                    name="status",
                    type="string",
                    required=True,
                    description="New status for the ticket",
                    example="Resolved"
                ),
                ActionParameter(
                    name="resolution_notes",
                    type="string",
                    required=False,
                    description="Notes about the resolution",
                    example="data.resolution_summary"
                )
            ],
            example_usage="Update ticket status when issues are resolved"
        )
        
        # Approval workflow actions
        actions["mw.request_approval"] = BuiltinAction(
            name="mw.request_approval",
            description="Request approval from a manager or approver",
            category="Approval Workflow",
            parameters=[
                ActionParameter(
                    name="approver_id",
                    type="string",
                    required=True,
                    description="ID of the person who should approve",
                    example="data.manager_id"
                ),
                ActionParameter(
                    name="request_details",
                    type="object",
                    required=True,
                    description="Details of what needs approval",
                    example="data.approval_request"
                ),
                ActionParameter(
                    name="timeout_hours",
                    type="number",
                    required=False,
                    description="Hours to wait before timeout",
                    example="24"
                )
            ],
            example_usage="Get manager approval for requests requiring authorization"
        )
        
        # Data retrieval actions
        actions["mw.query_database"] = BuiltinAction(
            name="mw.query_database",
            description="Execute a database query to retrieve information",
            category="Data Retrieval",
            parameters=[
                ActionParameter(
                    name="query_id",
                    type="string",
                    required=True,
                    description="ID of the predefined query to execute",
                    example="data.query_identifier"
                ),
                ActionParameter(
                    name="query_parameters",
                    type="object",
                    required=False,
                    description="Parameters to pass to the query",
                    example="data.search_criteria"
                )
            ],
            example_usage="Retrieve data from enterprise systems"
        )
        
        return actions
    
    def get_action(self, action_name: str) -> Optional[BuiltinAction]:
        """Get information about a specific built-in action."""
        return self._actions.get(action_name)
    
    def get_actions_by_category(self, category: str) -> List[BuiltinAction]:
        """Get all actions in a specific category."""
        return [action for action in self._actions.values() if action.category == category]
    
    def get_all_categories(self) -> List[str]:
        """Get all available action categories."""
        categories = set(action.category for action in self._actions.values())
        return sorted(list(categories))
    
    def get_all_actions(self) -> List[BuiltinAction]:
        """Get all available built-in actions."""
        return list(self._actions.values())
    
    def search_actions(self, query: str) -> List[BuiltinAction]:
        """Search for actions by name or description."""
        query = query.lower()
        results = []
        
        for action in self._actions.values():
            if (query in action.name.lower() or 
                query in action.description.lower() or
                query in action.category.lower()):
                results.append(action)
        
        return results
    
    def is_builtin_action(self, action_name: str) -> bool:
        """Check if an action name is a built-in Moveworks action."""
        return action_name in self._actions


# Global catalog instance
builtin_catalog = BuiltinActionCatalog()
