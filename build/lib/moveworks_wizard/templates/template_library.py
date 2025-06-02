"""
Template library for common Compound Action patterns.

This module provides pre-built templates that users can customize for their needs.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from ..models.base import CompoundAction
from ..models.actions import ActionStep, ScriptStep
from ..models.control_flow import SwitchStep, SwitchCase
from ..models.terminal import ReturnStep, RaiseStep
from ..models.common import ProgressUpdates, DelayConfig


@dataclass
class CompoundActionTemplate:
    """Represents a template for a Compound Action."""
    name: str
    description: str
    category: str
    use_case: str
    compound_action: CompoundAction
    customization_notes: List[str]


class TemplateLibrary:
    """
    Library of pre-built Compound Action templates.
    
    Provides common patterns and workflows that users can customize
    for their specific needs.
    """
    
    def __init__(self):
        """Initialize the template library."""
        self._templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, CompoundActionTemplate]:
        """Load all available templates."""
        templates = {}
        
        # User Management Templates
        templates["user_onboarding"] = self._create_user_onboarding_template()
        templates["user_offboarding"] = self._create_user_offboarding_template()
        templates["access_request"] = self._create_access_request_template()
        
        # Support & Ticketing Templates
        templates["ticket_escalation"] = self._create_ticket_escalation_template()
        templates["incident_response"] = self._create_incident_response_template()
        
        # Approval Workflow Templates
        templates["manager_approval"] = self._create_manager_approval_template()
        templates["multi_level_approval"] = self._create_multi_level_approval_template()
        
        # Data Processing Templates
        templates["data_validation"] = self._create_data_validation_template()
        templates["report_generation"] = self._create_report_generation_template()
        
        return templates
    
    def _create_user_onboarding_template(self) -> CompoundActionTemplate:
        """Create user onboarding workflow template."""
        # Step 1: Get user details
        get_user_step = ActionStep(
            action_name="mw.get_user_details",
            output_key="user_info",
            input_args={
                "user_id": "data.new_employee_id"
            },
            progress_updates=ProgressUpdates(
                in_progress="Retrieving user information...",
                completed="User information retrieved successfully"
            )
        )
        
        # Step 2: Grant basic access
        grant_access_step = ActionStep(
            action_name="mw.grant_access",
            output_key="access_granted",
            input_args={
                "user_id": "data.user_info.employee_id",
                "resource_id": "data.basic_systems",
                "access_level": "read"
            },
            progress_updates=ProgressUpdates(
                in_progress="Granting basic system access...",
                completed="Basic access granted successfully"
            )
        )
        
        # Step 3: Send welcome notification
        welcome_notification = ActionStep(
            action_name="mw.send_rich_chat_notification",
            output_key="welcome_sent",
            input_args={
                "user_record_id": "data.user_info.record_id",
                "card_content": "data.welcome_card"
            },
            progress_updates=ProgressUpdates(
                in_progress="Sending welcome notification...",
                completed="Welcome notification sent"
            )
        )
        
        # Step 4: Return results
        return_step = ReturnStep(
            output_mapper={
                "user_id": "data.user_info.employee_id",
                "access_granted": "data.access_granted",
                "welcome_sent": "data.welcome_sent",
                "onboarding_status": "completed"
            }
        )
        
        compound_action = CompoundAction(
            name="User Onboarding Workflow",
            description="Automated workflow for onboarding new employees",
            input_args={
                "new_employee_id": "data.employee_id",
                "basic_systems": "data.default_access_list",
                "welcome_card": "data.onboarding_welcome_card"
            },
            steps=[get_user_step, grant_access_step, welcome_notification, return_step]
        )
        
        return CompoundActionTemplate(
            name="User Onboarding Workflow",
            description="Automated workflow for onboarding new employees with access provisioning and welcome notifications",
            category="User Management",
            use_case="When a new employee joins the company and needs basic system access and welcome information",
            compound_action=compound_action,
            customization_notes=[
                "Customize 'basic_systems' to match your organization's default access requirements",
                "Modify 'welcome_card' content to include company-specific onboarding information",
                "Add additional steps for department-specific access or training materials",
                "Consider adding approval steps for sensitive system access"
            ]
        )
    
    def _create_access_request_template(self) -> CompoundActionTemplate:
        """Create access request workflow template."""
        # Step 1: Check current permissions
        check_permissions = ActionStep(
            action_name="mw.check_user_permissions",
            output_key="current_permissions",
            input_args={
                "user_id": "meta_info.requestor.employee_id",
                "resource_type": "data.requested_resource",
                "permission_level": "data.requested_access_level"
            }
        )
        
        # Step 2: Conditional approval based on access level
        approval_switch = SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.requested_access_level == 'admin'",
                    steps=[
                        ActionStep(
                            action_name="mw.request_approval",
                            output_key="approval_result",
                            input_args={
                                "approver_id": "data.security_manager_id",
                                "request_details": "data.access_request_details",
                                "timeout_hours": "48"
                            }
                        )
                    ]
                )
            ],
            default=[
                ActionStep(
                    action_name="mw.request_approval",
                    output_key="approval_result",
                    input_args={
                        "approver_id": "data.direct_manager_id",
                        "request_details": "data.access_request_details",
                        "timeout_hours": "24"
                    }
                )
            ]
        )
        
        # Step 3: Grant access if approved
        grant_access = ActionStep(
            action_name="mw.grant_access",
            output_key="access_granted",
            input_args={
                "user_id": "meta_info.requestor.employee_id",
                "resource_id": "data.requested_resource",
                "access_level": "data.requested_access_level"
            }
        )
        
        compound_action = CompoundAction(
            name="Access Request Workflow",
            description="Automated workflow for processing access requests with appropriate approvals",
            input_args={
                "requested_resource": "data.resource_name",
                "requested_access_level": "data.access_level",
                "access_request_details": "data.request_details",
                "direct_manager_id": "data.manager_id",
                "security_manager_id": "data.security_mgr_id"
            },
            steps=[check_permissions, approval_switch, grant_access]
        )
        
        return CompoundActionTemplate(
            name="Access Request Workflow",
            description="Automated access request processing with conditional approval routing",
            category="Security & Access",
            use_case="When users request access to systems or resources requiring manager approval",
            compound_action=compound_action,
            customization_notes=[
                "Adjust approval routing logic based on your organization's hierarchy",
                "Modify timeout periods to match your approval SLAs",
                "Add additional validation steps for high-security resources",
                "Consider adding notification steps to keep requestors informed"
            ]
        )

    def _create_user_offboarding_template(self) -> CompoundActionTemplate:
        """Create user offboarding workflow template."""
        # Step 1: Get user details and current access
        get_user_step = ActionStep(
            action_name="mw.get_user_details",
            output_key="user_info",
            input_args={
                "user_id": "data.departing_employee_id"
            }
        )

        # Step 2: Revoke all access
        revoke_access_step = ActionStep(
            action_name="mw.revoke_access",
            output_key="access_revoked",
            input_args={
                "user_id": "data.user_info.employee_id",
                "resource_id": "data.all_systems",
                "reason": "Employee departure"
            }
        )

        # Step 3: Create handover ticket
        create_ticket_step = ActionStep(
            action_name="mw.create_ticket",
            output_key="handover_ticket",
            input_args={
                "title": "Employee Departure - Knowledge Handover",
                "description": "data.handover_details",
                "requestor_id": "data.manager_id",
                "priority": "High"
            }
        )

        compound_action = CompoundAction(
            name="User Offboarding Workflow",
            description="Automated workflow for offboarding departing employees",
            input_args={
                "departing_employee_id": "data.employee_id",
                "all_systems": "data.system_list",
                "handover_details": "data.knowledge_transfer_info",
                "manager_id": "data.reporting_manager_id"
            },
            steps=[get_user_step, revoke_access_step, create_ticket_step]
        )

        return CompoundActionTemplate(
            name="User Offboarding Workflow",
            description="Automated workflow for securely offboarding departing employees",
            category="User Management",
            use_case="When an employee leaves the company and needs access revoked and handover processes initiated",
            compound_action=compound_action,
            customization_notes=[
                "Customize system list to include all organizational systems",
                "Add steps for equipment return tracking",
                "Include exit interview scheduling",
                "Consider adding final payroll processing steps"
            ]
        )

    def _create_ticket_escalation_template(self) -> CompoundActionTemplate:
        """Create ticket escalation workflow template."""
        # Step 1: Check ticket age and priority
        check_ticket_script = ScriptStep(
            code="""
# Check if ticket needs escalation based on age and priority
ticket_age_hours = int(data.ticket_age_hours)
priority = data.ticket_priority.lower()

escalation_thresholds = {
    'critical': 2,
    'high': 8,
    'medium': 24,
    'low': 72
}

needs_escalation = ticket_age_hours > escalation_thresholds.get(priority, 24)
escalation_level = 'manager' if ticket_age_hours < 48 else 'director'

return {
    'needs_escalation': needs_escalation,
    'escalation_level': escalation_level,
    'threshold_exceeded_by': ticket_age_hours - escalation_thresholds.get(priority, 24)
}
            """,
            output_key="escalation_check",
            input_args={
                "ticket_age_hours": "data.ticket_age",
                "ticket_priority": "data.priority"
            }
        )

        # Step 2: Escalate if needed
        escalation_switch = SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.escalation_check.needs_escalation == true",
                    steps=[
                        ActionStep(
                            action_name="mw.update_ticket_status",
                            output_key="ticket_escalated",
                            input_args={
                                "ticket_id": "data.ticket_id",
                                "status": "Escalated",
                                "resolution_notes": "Automatically escalated due to SLA breach"
                            }
                        ),
                        ActionStep(
                            action_name="mw.send_plaintext_chat_notification",
                            output_key="escalation_notification",
                            input_args={
                                "user_record_id": "data.escalation_manager_id",
                                "message": "Ticket escalated: data.ticket_summary"
                            }
                        )
                    ]
                )
            ]
        )

        compound_action = CompoundAction(
            name="Ticket Escalation Workflow",
            description="Automated ticket escalation based on age and priority",
            input_args={
                "ticket_id": "data.support_ticket_id",
                "ticket_age": "data.hours_since_creation",
                "priority": "data.ticket_priority",
                "ticket_summary": "data.ticket_title",
                "escalation_manager_id": "data.manager_record_id"
            },
            steps=[check_ticket_script, escalation_switch]
        )

        return CompoundActionTemplate(
            name="Ticket Escalation Workflow",
            description="Automated escalation of support tickets based on SLA thresholds",
            category="Support & Ticketing",
            use_case="When support tickets exceed SLA thresholds and need management attention",
            compound_action=compound_action,
            customization_notes=[
                "Adjust escalation thresholds to match your SLA requirements",
                "Customize notification messages for different escalation levels",
                "Add integration with your ticketing system",
                "Consider adding customer notification steps"
            ]
        )

    def _create_incident_response_template(self) -> CompoundActionTemplate:
        """Create incident response workflow template."""
        # Step 1: Log the incident
        log_incident = ActionStep(
            action_name="mw.log_event",
            output_key="incident_logged",
            input_args={
                "event_type": "security_incident",
                "event_data": "data.incident_details",
                "user_id": "meta_info.requestor.employee_id"
            }
        )

        # Step 2: Create high-priority ticket
        create_incident_ticket = ActionStep(
            action_name="mw.create_ticket",
            output_key="incident_ticket",
            input_args={
                "title": "Security Incident - Immediate Response Required",
                "description": "data.incident_description",
                "requestor_id": "meta_info.requestor.employee_id",
                "priority": "Critical"
            }
        )

        # Step 3: Notify security team
        notify_security = ActionStep(
            action_name="mw.send_plaintext_chat_notification",
            output_key="security_notified",
            input_args={
                "user_record_id": "data.security_team_id",
                "message": "URGENT: Security incident reported. Ticket: data.incident_ticket.ticket_id"
            }
        )

        compound_action = CompoundAction(
            name="Incident Response Workflow",
            description="Automated workflow for security incident response",
            input_args={
                "incident_details": "data.incident_info",
                "incident_description": "data.detailed_description",
                "security_team_id": "data.security_team_record_id"
            },
            steps=[log_incident, create_incident_ticket, notify_security]
        )

        return CompoundActionTemplate(
            name="Incident Response Workflow",
            description="Automated security incident response with logging and notifications",
            category="Support & Ticketing",
            use_case="When security incidents are reported and need immediate response",
            compound_action=compound_action,
            customization_notes=[
                "Customize security team notification channels",
                "Add integration with security monitoring tools",
                "Include automated containment steps if appropriate",
                "Consider adding compliance reporting steps"
            ]
        )

    def _create_manager_approval_template(self) -> CompoundActionTemplate:
        """Create manager approval workflow template."""
        # Step 1: Request approval
        request_approval = ActionStep(
            action_name="mw.request_approval",
            output_key="approval_response",
            input_args={
                "approver_id": "data.manager_id",
                "request_details": "data.approval_request",
                "timeout_hours": "24"
            },
            progress_updates=ProgressUpdates(
                in_progress="Waiting for manager approval...",
                completed="Manager approval received"
            )
        )

        # Step 2: Process based on approval result
        approval_switch = SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.approval_response.approved == true",
                    steps=[
                        ActionStep(
                            action_name="mw.send_plaintext_chat_notification",
                            output_key="approval_notification",
                            input_args={
                                "user_record_id": "meta_info.requestor.record_id",
                                "message": "Your request has been approved and is being processed."
                            }
                        )
                    ]
                )
            ],
            default=[
                ActionStep(
                    action_name="mw.send_plaintext_chat_notification",
                    output_key="rejection_notification",
                    input_args={
                        "user_record_id": "meta_info.requestor.record_id",
                        "message": "Your request has been declined. Reason: data.approval_response.reason"
                    }
                )
            ]
        )

        compound_action = CompoundAction(
            name="Manager Approval Workflow",
            description="Simple manager approval workflow with notifications",
            input_args={
                "manager_id": "data.reporting_manager_id",
                "approval_request": "data.request_details"
            },
            steps=[request_approval, approval_switch]
        )

        return CompoundActionTemplate(
            name="Manager Approval Workflow",
            description="Simple workflow for requesting manager approval with automatic notifications",
            category="Approval Workflow",
            use_case="When requests need manager approval before processing",
            compound_action=compound_action,
            customization_notes=[
                "Adjust timeout period based on your approval SLAs",
                "Customize notification messages for your organization",
                "Add escalation logic for overdue approvals",
                "Consider adding approval reason tracking"
            ]
        )

    def _create_multi_level_approval_template(self) -> CompoundActionTemplate:
        """Create multi-level approval workflow template."""
        # Step 1: First level approval (manager)
        manager_approval = ActionStep(
            action_name="mw.request_approval",
            output_key="manager_approval",
            input_args={
                "approver_id": "data.manager_id",
                "request_details": "data.approval_request",
                "timeout_hours": "24"
            }
        )

        # Step 2: Second level approval if needed
        director_approval_switch = SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.manager_approval.approved == true AND data.request_amount > 10000",
                    steps=[
                        ActionStep(
                            action_name="mw.request_approval",
                            output_key="director_approval",
                            input_args={
                                "approver_id": "data.director_id",
                                "request_details": "data.approval_request",
                                "timeout_hours": "48"
                            }
                        )
                    ]
                )
            ]
        )

        compound_action = CompoundAction(
            name="Multi-Level Approval Workflow",
            description="Multi-level approval workflow based on request value",
            input_args={
                "manager_id": "data.reporting_manager_id",
                "director_id": "data.department_director_id",
                "approval_request": "data.request_details",
                "request_amount": "data.financial_amount"
            },
            steps=[manager_approval, director_approval_switch]
        )

        return CompoundActionTemplate(
            name="Multi-Level Approval Workflow",
            description="Conditional multi-level approval workflow based on request criteria",
            category="Approval Workflow",
            use_case="When high-value requests need multiple levels of approval",
            compound_action=compound_action,
            customization_notes=[
                "Adjust approval thresholds for your organization",
                "Add more approval levels if needed",
                "Customize approval criteria beyond financial amounts",
                "Include parallel approval paths for different departments"
            ]
        )

    def _create_data_validation_template(self) -> CompoundActionTemplate:
        """Create data validation workflow template."""
        # Step 1: Validate input data
        validation_script = ScriptStep(
            code="""
# Validate input data format and completeness
import re

errors = []
warnings = []

# Email validation
email = data.user_email
if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
    errors.append("Invalid email format")

# Phone validation
phone = data.user_phone
if not re.match(r'^\+?1?[0-9]{10,15}$', phone.replace('-', '').replace(' ', '')):
    warnings.append("Phone number format may be invalid")

# Required fields check
required_fields = ['user_name', 'user_email', 'department']
for field in required_fields:
    if not data.get(field):
        errors.append(f"Missing required field: {field}")

return {
    'is_valid': len(errors) == 0,
    'errors': errors,
    'warnings': warnings,
    'validation_score': max(0, 100 - len(errors) * 25 - len(warnings) * 5)
}
            """,
            output_key="validation_result",
            input_args={
                "user_email": "data.email",
                "user_phone": "data.phone",
                "user_name": "data.name",
                "department": "data.dept"
            }
        )

        compound_action = CompoundAction(
            name="Data Validation Workflow",
            description="Comprehensive data validation with error reporting",
            input_args={
                "email": "data.user_email",
                "phone": "data.user_phone",
                "name": "data.user_name",
                "dept": "data.user_department"
            },
            steps=[validation_script]
        )

        return CompoundActionTemplate(
            name="Data Validation Workflow",
            description="Validate user input data with comprehensive error checking",
            category="Data Processing",
            use_case="When user-submitted data needs validation before processing",
            compound_action=compound_action,
            customization_notes=[
                "Customize validation rules for your data requirements",
                "Add domain-specific validation logic",
                "Include data sanitization steps",
                "Consider adding external validation services"
            ]
        )

    def _create_report_generation_template(self) -> CompoundActionTemplate:
        """Create report generation workflow template."""
        # Step 1: Generate the report
        generate_report = ActionStep(
            action_name="mw.generate_report",
            output_key="report_data",
            input_args={
                "report_type": "data.report_template",
                "date_range": "data.reporting_period",
                "filters": "data.report_filters"
            },
            progress_updates=ProgressUpdates(
                in_progress="Generating report...",
                completed="Report generated successfully"
            )
        )

        # Step 2: Upload report file
        upload_report = ActionStep(
            action_name="mw.upload_file",
            output_key="report_uploaded",
            input_args={
                "file_content": "data.report_data.content",
                "file_name": "data.report_filename",
                "folder_path": "data.reports_folder"
            }
        )

        # Step 3: Notify stakeholders
        notify_stakeholders = ActionStep(
            action_name="mw.send_rich_chat_notification",
            output_key="stakeholders_notified",
            input_args={
                "user_record_id": "data.stakeholder_list",
                "card_content": "data.report_notification_card"
            }
        )

        compound_action = CompoundAction(
            name="Report Generation Workflow",
            description="Automated report generation and distribution",
            input_args={
                "report_template": "data.template_name",
                "reporting_period": "data.date_range",
                "report_filters": "data.filter_criteria",
                "report_filename": "data.output_filename",
                "reports_folder": "data.storage_path",
                "stakeholder_list": "data.notification_recipients",
                "report_notification_card": "data.notification_content"
            },
            steps=[generate_report, upload_report, notify_stakeholders]
        )

        return CompoundActionTemplate(
            name="Report Generation Workflow",
            description="Automated report generation with file storage and stakeholder notifications",
            category="Data Processing",
            use_case="When periodic reports need to be generated and distributed to stakeholders",
            compound_action=compound_action,
            customization_notes=[
                "Customize report templates for your organization",
                "Add scheduling logic for recurring reports",
                "Include data quality checks before generation",
                "Consider adding report archival and retention policies"
            ]
        )

    def get_template(self, template_name: str) -> Optional[CompoundActionTemplate]:
        """Get a specific template by name."""
        return self._templates.get(template_name)
    
    def get_templates_by_category(self, category: str) -> List[CompoundActionTemplate]:
        """Get all templates in a specific category."""
        return [template for template in self._templates.values() if template.category == category]
    
    def get_all_categories(self) -> List[str]:
        """Get all available template categories."""
        categories = set(template.category for template in self._templates.values())
        return sorted(list(categories))
    
    def get_all_templates(self) -> List[CompoundActionTemplate]:
        """Get all available templates."""
        return list(self._templates.values())
    
    def search_templates(self, query: str) -> List[CompoundActionTemplate]:
        """Search for templates by name, description, or use case."""
        query = query.lower()
        results = []
        
        for template in self._templates.values():
            if (query in template.name.lower() or 
                query in template.description.lower() or
                query in template.use_case.lower()):
                results.append(template)
        
        return results


# Global template library instance
template_library = TemplateLibrary()
