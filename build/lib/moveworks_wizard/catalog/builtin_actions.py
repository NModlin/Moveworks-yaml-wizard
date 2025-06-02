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

        # Additional Data Retrieval actions
        actions["mw.search_knowledge_base"] = BuiltinAction(
            name="mw.search_knowledge_base",
            description="Search the knowledge base for relevant articles",
            category="Data Retrieval",
            parameters=[
                ActionParameter(
                    name="search_query",
                    type="string",
                    required=True,
                    description="Search terms to find relevant articles",
                    example="data.user_question"
                ),
                ActionParameter(
                    name="max_results",
                    type="number",
                    required=False,
                    description="Maximum number of results to return",
                    example="5"
                )
            ],
            example_usage="Find relevant knowledge base articles for user questions"
        )

        actions["mw.get_system_status"] = BuiltinAction(
            name="mw.get_system_status",
            description="Check the status of enterprise systems",
            category="Data Retrieval",
            parameters=[
                ActionParameter(
                    name="system_name",
                    type="string",
                    required=True,
                    description="Name of the system to check",
                    example="data.target_system"
                )
            ],
            example_usage="Monitor system health and availability"
        )

        # Security & Access Management actions
        actions["mw.check_user_permissions"] = BuiltinAction(
            name="mw.check_user_permissions",
            description="Verify user permissions for specific resources",
            category="Security & Access",
            parameters=[
                ActionParameter(
                    name="user_id",
                    type="string",
                    required=True,
                    description="ID of the user to check",
                    example="meta_info.requestor.employee_id"
                ),
                ActionParameter(
                    name="resource_type",
                    type="string",
                    required=True,
                    description="Type of resource to check access for",
                    example="data.resource_name"
                ),
                ActionParameter(
                    name="permission_level",
                    type="string",
                    required=False,
                    description="Required permission level",
                    example="read"
                )
            ],
            example_usage="Validate user access before performing sensitive operations"
        )

        actions["mw.grant_access"] = BuiltinAction(
            name="mw.grant_access",
            description="Grant access permissions to a user",
            category="Security & Access",
            parameters=[
                ActionParameter(
                    name="user_id",
                    type="string",
                    required=True,
                    description="ID of the user to grant access",
                    example="data.target_user_id"
                ),
                ActionParameter(
                    name="resource_id",
                    type="string",
                    required=True,
                    description="ID of the resource to grant access to",
                    example="data.resource_identifier"
                ),
                ActionParameter(
                    name="access_level",
                    type="string",
                    required=True,
                    description="Level of access to grant",
                    example="data.requested_access_level"
                ),
                ActionParameter(
                    name="expiry_date",
                    type="string",
                    required=False,
                    description="When the access should expire",
                    example="data.access_expiry"
                )
            ],
            example_usage="Provision access to systems and resources"
        )

        actions["mw.revoke_access"] = BuiltinAction(
            name="mw.revoke_access",
            description="Revoke access permissions from a user",
            category="Security & Access",
            parameters=[
                ActionParameter(
                    name="user_id",
                    type="string",
                    required=True,
                    description="ID of the user to revoke access from",
                    example="data.target_user_id"
                ),
                ActionParameter(
                    name="resource_id",
                    type="string",
                    required=True,
                    description="ID of the resource to revoke access from",
                    example="data.resource_identifier"
                ),
                ActionParameter(
                    name="reason",
                    type="string",
                    required=False,
                    description="Reason for revoking access",
                    example="data.revocation_reason"
                )
            ],
            example_usage="Remove access when no longer needed"
        )

        # Integration & Automation actions
        actions["mw.trigger_webhook"] = BuiltinAction(
            name="mw.trigger_webhook",
            description="Trigger an external webhook with data",
            category="Integration & Automation",
            parameters=[
                ActionParameter(
                    name="webhook_url",
                    type="string",
                    required=True,
                    description="URL of the webhook to trigger",
                    example="data.webhook_endpoint"
                ),
                ActionParameter(
                    name="payload",
                    type="object",
                    required=True,
                    description="Data to send to the webhook",
                    example="data.webhook_payload"
                ),
                ActionParameter(
                    name="headers",
                    type="object",
                    required=False,
                    description="Additional headers to include",
                    example="data.custom_headers"
                )
            ],
            example_usage="Integrate with external systems via webhooks"
        )

        actions["mw.schedule_task"] = BuiltinAction(
            name="mw.schedule_task",
            description="Schedule a task to be executed later",
            category="Integration & Automation",
            parameters=[
                ActionParameter(
                    name="task_type",
                    type="string",
                    required=True,
                    description="Type of task to schedule",
                    example="data.task_category"
                ),
                ActionParameter(
                    name="execution_time",
                    type="string",
                    required=True,
                    description="When to execute the task",
                    example="data.scheduled_time"
                ),
                ActionParameter(
                    name="task_parameters",
                    type="object",
                    required=False,
                    description="Parameters for the scheduled task",
                    example="data.task_config"
                )
            ],
            example_usage="Schedule follow-up actions or reminders"
        )

        # Analytics & Reporting actions
        actions["mw.log_event"] = BuiltinAction(
            name="mw.log_event",
            description="Log an event for analytics and reporting",
            category="Analytics & Reporting",
            parameters=[
                ActionParameter(
                    name="event_type",
                    type="string",
                    required=True,
                    description="Type of event being logged",
                    example="data.event_category"
                ),
                ActionParameter(
                    name="event_data",
                    type="object",
                    required=True,
                    description="Data associated with the event",
                    example="data.event_details"
                ),
                ActionParameter(
                    name="user_id",
                    type="string",
                    required=False,
                    description="ID of the user associated with the event",
                    example="meta_info.requestor.employee_id"
                )
            ],
            example_usage="Track user interactions and system events"
        )

        actions["mw.generate_report"] = BuiltinAction(
            name="mw.generate_report",
            description="Generate a report based on specified criteria",
            category="Analytics & Reporting",
            parameters=[
                ActionParameter(
                    name="report_type",
                    type="string",
                    required=True,
                    description="Type of report to generate",
                    example="data.report_template"
                ),
                ActionParameter(
                    name="date_range",
                    type="object",
                    required=True,
                    description="Date range for the report",
                    example="data.reporting_period"
                ),
                ActionParameter(
                    name="filters",
                    type="object",
                    required=False,
                    description="Additional filters for the report",
                    example="data.report_filters"
                )
            ],
            example_usage="Create reports for management and compliance"
        )

        # File & Document Management actions
        actions["mw.upload_file"] = BuiltinAction(
            name="mw.upload_file",
            description="Upload a file to the document management system",
            category="File & Document Management",
            parameters=[
                ActionParameter(
                    name="file_content",
                    type="string",
                    required=True,
                    description="Content of the file to upload",
                    example="data.file_data"
                ),
                ActionParameter(
                    name="file_name",
                    type="string",
                    required=True,
                    description="Name of the file",
                    example="data.document_name"
                ),
                ActionParameter(
                    name="folder_path",
                    type="string",
                    required=False,
                    description="Path where the file should be stored",
                    example="data.storage_location"
                )
            ],
            example_usage="Store documents and files in the system"
        )

        actions["mw.download_file"] = BuiltinAction(
            name="mw.download_file",
            description="Download a file from the document management system",
            category="File & Document Management",
            parameters=[
                ActionParameter(
                    name="file_id",
                    type="string",
                    required=True,
                    description="ID of the file to download",
                    example="data.document_id"
                ),
                ActionParameter(
                    name="include_metadata",
                    type="boolean",
                    required=False,
                    description="Whether to include file metadata",
                    example="true"
                )
            ],
            example_usage="Retrieve documents and files from the system"
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
