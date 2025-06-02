"""
Phase 5 Comprehensive Tests for Moveworks YAML Wizard

This module contains comprehensive tests for Phase 5, focusing on:
- Action Activity integration context
- Real-world deployment scenarios
- Performance and stress testing
- End-to-end production workflows
"""

import pytest
import tempfile
import yaml
import time
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from src.moveworks_wizard.wizard.cli import CompoundActionWizard
from src.moveworks_wizard.models.base import CompoundAction
from src.moveworks_wizard.models.actions import ActionStep, ScriptStep
from src.moveworks_wizard.models.control_flow import SwitchStep, SwitchCase
from src.moveworks_wizard.models.terminal import ReturnStep, RaiseStep
from src.moveworks_wizard.serializers import serialize_compound_action
from src.moveworks_wizard.catalog.builtin_actions import builtin_catalog
from src.moveworks_wizard.templates.template_library import template_library
from src.moveworks_wizard.ai.action_suggester import action_suggester
from src.moveworks_wizard.bender.bender_assistant import bender_assistant


class TestActionActivityIntegration:
    """Test integration with Action Activity context."""
    
    def test_compound_action_for_action_activity_context(self):
        """Test that generated YAML is suitable for Action Activity usage."""
        # Add steps that demonstrate Action Activity integration
        steps = [
            ActionStep(
                action_name="mw.user.create",
                output_key="new_user",
                input_args={
                    "email": "data.user_email",
                    "department": "data.department"
                }
            ),
            ActionStep(
                action_name="mw.notification.send",
                output_key="notification_result",
                input_args={
                    "recipient": "data.manager_id",
                    "message": "RENDER('New user {{user_email}} has been created', data)"
                }
            )
        ]

        # Create a compound action that would be used in an Action Activity
        compound_action = CompoundAction(
            name="User Onboarding Workflow",
            description="Complete user onboarding process for Action Activity",
            input_args={
                "user_email": "data.user_email",
                "department": "data.department",
                "manager_id": "data.manager_id"
            },
            steps=steps
        )
        
        # Generate YAML
        yaml_content = serialize_compound_action(compound_action)
        
        # Validate YAML structure for Action Activity compatibility
        yaml_data = yaml.safe_load(yaml_content)
        
        # Check input_args use proper data.* references
        assert "input_args" in yaml_data
        for key, value in yaml_data["input_args"].items():
            assert isinstance(value, str)
            assert value.startswith("data."), f"Input arg {key} should reference data.*"
        
        # Check steps have proper structure
        assert "steps" in yaml_data
        assert len(yaml_data["steps"]) == 2
        
        # Validate first step
        first_step = yaml_data["steps"][0]
        assert "action" in first_step
        assert first_step["action"]["action_name"] == "mw.user.create"
        assert first_step["action"]["output_key"] == "new_user"
        
        # Validate second step uses RENDER function
        second_step = yaml_data["steps"][1]
        assert "RENDER(" in str(second_step["action"]["input_args"]["message"])
    
    def test_data_flow_validation_for_action_activity(self):
        """Test data flow patterns suitable for Action Activity mappers."""
        steps = [
            ActionStep(
                action_name="mw.user.get",
                output_key="user_details",
                input_args={"id": "data.user_id"}
            ),
            ScriptStep(
                output_key="processed_data",
                code="result = {'processed': True, 'timestamp': str(datetime.now())}"
            ),
            ActionStep(
                action_name="mw.database.update",
                output_key="update_result",
                input_args={
                    "table": "user_processing",
                    "data": "processed_data"
                }
            )
        ]

        # Create compound action with complex data flow
        compound_action = CompoundAction(
            name="Complex Data Flow",
            input_args={
                "user_id": "data.user_id",
                "metadata": "meta_info.request_context"
            },
            steps=steps
        )
        yaml_content = serialize_compound_action(compound_action)
        yaml_data = yaml.safe_load(yaml_content)
        
        # Validate data flow references
        assert yaml_data["input_args"]["user_id"] == "data.user_id"
        assert yaml_data["input_args"]["metadata"] == "meta_info.request_context"
        
        # Validate step data references
        step1 = yaml_data["steps"][0]["action"]
        assert step1["input_args"]["id"] == "data.user_id"
        
        step3 = yaml_data["steps"][2]["action"]
        assert step3["input_args"]["data"] == "processed_data"
    
    def test_progress_updates_for_async_execution(self):
        """Test progress updates suitable for asynchronous Action Activity execution."""
        from src.moveworks_wizard.models.common import ProgressUpdates

        progress_updates = ProgressUpdates(
            on_pending="Initiating long-running task...",
            on_complete="Task completed successfully"
        )

        action = ActionStep(
            action_name="mw.integration.long_running_task",
            output_key="task_result",
            input_args={"task_id": "data.task_id"},
            progress_updates=progress_updates
        )

        compound_action = CompoundAction(
            name="Long Running Task",
            single_step=action
        )

        yaml_content = serialize_compound_action(compound_action)
        yaml_data = yaml.safe_load(yaml_content)

        # Validate progress updates structure
        progress = yaml_data["action"]["progress_updates"]
        assert "on_pending" in progress
        assert "on_complete" in progress

        # Validate progress messages
        assert "Initiating long-running task" in progress["on_pending"]
        assert "Task completed successfully" in progress["on_complete"]


class TestRealWorldScenarios:
    """Test real-world deployment scenarios."""
    
    def test_employee_offboarding_workflow(self):
        """Test complete employee offboarding workflow."""
        # Create comprehensive offboarding workflow
        steps = [
            ActionStep(
                action_name="mw.user.disable",
                output_key="disable_result",
                input_args={"user_id": "data.employee_id"}
            ),
            ActionStep(
                action_name="mw.access.revoke_all",
                output_key="access_revoke_result",
                input_args={"user_id": "data.employee_id"}
            ),
            ScriptStep(
                output_key="offboarding_summary",
                code="result = {'status': 'completed', 'timestamp': str(datetime.now())}"
            ),
            ActionStep(
                action_name="mw.notification.send",
                output_key="notification_result",
                input_args={
                    "recipient": "data.manager_email",
                    "subject": "Employee Offboarding Complete",
                    "message": "RENDER('Employee {{employee_id}} offboarding completed on {{last_day}}', data)"
                }
            )
        ]

        compound_action = CompoundAction(
            name="Employee Offboarding",
            description="Complete employee offboarding process",
            input_args={
                "employee_id": "data.employee_id",
                "last_day": "data.last_day",
                "manager_email": "data.manager_email"
            },
            steps=steps
        )
        yaml_content = serialize_compound_action(compound_action)
        
        # Validate complete workflow
        yaml_data = yaml.safe_load(yaml_content)
        assert len(yaml_data["steps"]) == 4
        assert yaml_data["input_args"]["employee_id"] == "data.employee_id"
        
        # Validate each step type
        assert "action" in yaml_data["steps"][0]  # Action step
        assert "action" in yaml_data["steps"][1]  # Action step
        assert "script" in yaml_data["steps"][2]  # Script step
        assert "action" in yaml_data["steps"][3]  # Action step
    
    def test_incident_response_workflow(self):
        """Test incident response workflow with error handling."""
        # Create incident response with switch logic
        switch_step = SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.severity == 'critical'",
                    steps=[
                        ActionStep(
                            action_name="mw.alert.page_oncall",
                            output_key="page_result",
                            input_args={"message": "CRITICAL: {{data.incident_title}}"}
                        ),
                        ActionStep(
                            action_name="mw.ticket.escalate",
                            output_key="escalate_result",
                            input_args={"ticket_id": "data.ticket_id", "priority": "P1"}
                        )
                    ]
                ),
                SwitchCase(
                    condition="data.severity == 'high'",
                    steps=[
                        ActionStep(
                            action_name="mw.notification.send_team",
                            output_key="team_notify_result",
                            input_args={"team": "data.assigned_team", "message": "High priority incident: {{data.incident_title}}"}
                        )
                    ]
                )
            ],
            default=[
                ActionStep(
                    action_name="mw.ticket.assign",
                    output_key="assign_result",
                    input_args={"ticket_id": "data.ticket_id", "assignee": "data.default_assignee"}
                )
            ]
        )

        compound_action = CompoundAction(
            name="Incident Response",
            description="Automated incident response workflow",
            single_step=switch_step
        )
        yaml_content = serialize_compound_action(compound_action)
        yaml_data = yaml.safe_load(yaml_content)
        
        # Validate switch structure
        assert "switch" in yaml_data
        switch_data = yaml_data["switch"]
        assert len(switch_data["cases"]) == 2
        assert "default" in switch_data

        # Validate case conditions
        first_case = switch_data["cases"][0]
        assert "condition" in first_case
        assert "data.severity == 'critical'" in first_case["condition"]


class TestPerformanceAndStress:
    """Test performance and stress scenarios."""
    
    def test_large_compound_action_generation(self):
        """Test generation of large compound actions."""
        steps = []
        for i in range(50):  # Create 50 steps
            steps.append(ActionStep(
                action_name=f"mw.test.action_{i}",
                output_key=f"result_{i}",
                input_args={"step_number": str(i), "data": f"data.input_{i}"}
            ))

        # Create a compound action with many steps
        compound_action = CompoundAction(
            name="Large Workflow",
            description="Workflow with many steps for stress testing",
            steps=steps
        )
        
        # Measure generation time
        start_time = time.time()
        yaml_content = serialize_compound_action(compound_action)
        generation_time = time.time() - start_time
        
        # Validate performance (should complete in reasonable time)
        assert generation_time < 5.0, f"Generation took too long: {generation_time}s"
        
        # Validate output
        yaml_data = yaml.safe_load(yaml_content)
        assert len(yaml_data["steps"]) == 50
    
    def test_complex_nested_structures(self):
        """Test complex nested switch and conditional structures."""
        # Create deeply nested switch structure
        inner_switch = SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.sub_category == 'type_a'",
                    steps=[ActionStep(action_name="mw.process.type_a", output_key="type_a_result")]
                ),
                SwitchCase(
                    condition="data.sub_category == 'type_b'",
                    steps=[ActionStep(action_name="mw.process.type_b", output_key="type_b_result")]
                )
            ]
        )

        outer_switch = SwitchStep(
            cases=[
                SwitchCase(
                    condition="data.category == 'category_1'",
                    steps=[inner_switch]
                ),
                SwitchCase(
                    condition="data.category == 'category_2'",
                    steps=[
                        ActionStep(action_name="mw.simple.action", output_key="simple_result"),
                        ReturnStep(value="simple_result")
                    ]
                )
            ]
        )

        compound_action = CompoundAction(
            name="Nested Workflow",
            single_step=outer_switch
        )
        
        yaml_content = serialize_compound_action(compound_action)
        yaml_data = yaml.safe_load(yaml_content)
        
        # Validate nested structure
        assert "switch" in yaml_data
        outer_switch_data = yaml_data["switch"]
        assert len(outer_switch_data["cases"]) == 2
        
        # Validate inner switch in first case
        first_case_steps = outer_switch_data["cases"][0]["steps"]
        assert len(first_case_steps) == 1
        assert "switch" in first_case_steps[0]


class TestProductionReadiness:
    """Test production readiness scenarios."""
    
    def test_error_handling_patterns(self):
        """Test error handling patterns for production use."""
        # Test that models handle various error scenarios gracefully

        # Test invalid CompoundAction creation
        with pytest.raises(ValueError):
            CompoundAction(name="Test")  # Missing steps or single_step

        # Test invalid ActionStep creation
        with pytest.raises(ValueError):
            ActionStep(action_name="", output_key="output")  # Empty action name

        with pytest.raises(ValueError):
            ActionStep(action_name="valid_action", output_key="")  # Empty output key
    
    def test_yaml_compliance_edge_cases(self):
        """Test YAML compliance with edge cases."""
        # Test special characters in strings
        action = ActionStep(
            action_name="mw.test.special_chars",
            output_key="special_result",
            input_args={
                "message": "Test with 'quotes' and \"double quotes\" and newlines\nand tabs\t",
                "template": "RENDER('User: {{user.name}} - Status: {{status}}', data)"
            }
        )
        
        compound_action = CompoundAction(single_step=action)
        yaml_content = serialize_compound_action(compound_action)
        
        # Validate YAML can be parsed
        yaml_data = yaml.safe_load(yaml_content)
        assert yaml_data is not None
        
        # Validate special characters are preserved
        message = yaml_data["action"]["input_args"]["message"]
        assert "'" in message
        assert '"' in message
        assert "\n" in message or "\\n" in message
    
    def test_template_integration_production(self):
        """Test template integration for production scenarios."""
        # Get a template and validate it generates production-ready YAML
        templates = template_library.get_all_templates()
        assert len(templates) > 0, "Should have templates available"

        # Test the first available template
        first_template = templates[0]
        assert first_template is not None

        # Use the template's compound action directly
        compound_action = first_template.compound_action

        yaml_content = serialize_compound_action(compound_action)
        yaml_data = yaml.safe_load(yaml_content)

        # Validate template generates valid structure
        assert "input_args" in yaml_data or "steps" in yaml_data or "action" in yaml_data
