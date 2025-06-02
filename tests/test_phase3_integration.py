"""
Phase 3 Integration Tests for Moveworks YAML Wizard

This module contains comprehensive integration tests for Phase 3,
focusing on end-to-end wizard flows, YAML validation, and complex scenarios.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from src.moveworks_wizard.wizard.cli import CompoundActionWizard
from src.moveworks_wizard.models.base import CompoundAction
from src.moveworks_wizard.models.actions import ActionStep, ScriptStep
from src.moveworks_wizard.models.control_flow import SwitchStep, SwitchCase
from src.moveworks_wizard.models.terminal import ReturnStep, RaiseStep
from src.moveworks_wizard.serializers import serialize_compound_action


class TestEndToEndWizardFlows:
    """Test complete wizard flows from start to finish."""
    
    def test_simple_single_action_workflow(self):
        """Test creating a simple single-action compound action."""
        wizard = CompoundActionWizard()
        
        # Create a simple action step
        action_step = ActionStep(
            action_name="mw.get_user_details",
            output_key="user_info",
            input_args={"user_id": "data.user_id"},
            progress_updates={
                "on_pending": "Fetching user details...",
                "on_complete": "User details retrieved"
            }
        )
        
        # Create compound action
        compound_action = CompoundAction(
            name="Get User Details",
            description="Retrieve user information",
            input_args={"user_id": "data.user_id"},
            single_step=action_step
        )
        
        # Test YAML generation
        yaml_dict = compound_action.to_yaml_dict()
        
        # Validate structure
        assert "input_args" in yaml_dict
        assert yaml_dict["input_args"]["user_id"] == "data.user_id"
        assert "action" in yaml_dict
        assert yaml_dict["action"]["action_name"] == "mw.get_user_details"
        assert yaml_dict["action"]["output_key"] == "user_info"
        assert "progress_updates" in yaml_dict["action"]
    
    def test_multi_step_workflow_with_script(self):
        """Test creating a multi-step workflow with action and script steps."""
        wizard = CompoundActionWizard()
        
        # Create action step
        action_step = ActionStep(
            action_name="mw.get_user_details",
            output_key="user_info",
            input_args={"user_id": "data.user_id"}
        )
        
        # Create script step
        script_step = ScriptStep(
            code="processed_data = {'email': user_info['email'].lower()}",
            output_key="processed_info",
            input_args={"user_info": "data.user_info"}
        )
        
        # Create compound action
        compound_action = CompoundAction(
            name="Process User Data",
            description="Get and process user information",
            input_args={"user_id": "data.user_id"},
            steps=[action_step, script_step]
        )
        
        # Test YAML generation
        yaml_dict = compound_action.to_yaml_dict()
        
        # Validate structure
        assert "input_args" in yaml_dict
        assert "steps" in yaml_dict
        assert len(yaml_dict["steps"]) == 2
        assert "action" in yaml_dict["steps"][0]
        assert "script" in yaml_dict["steps"][1]
    
    def test_complex_workflow_with_switch_and_return(self):
        """Test creating a complex workflow with switch logic and return step."""
        wizard = CompoundActionWizard()
        
        # Create action step
        action_step = ActionStep(
            action_name="mw.get_user_details",
            output_key="user_info",
            input_args={"user_id": "data.user_id"}
        )
        
        # Create switch cases
        manager_case = SwitchCase(
            condition="data.user_info.role == 'manager'",
            steps=[
                ActionStep(
                    action_name="mw.send_rich_chat_notification",
                    output_key="manager_notification",
                    input_args={
                        "user_record_id": "data.user_info.record_id",
                        "card_content": "data.manager_card"
                    }
                )
            ]
        )
        
        default_steps = [
            ActionStep(
                action_name="mw.send_plaintext_chat_notification",
                output_key="employee_notification",
                input_args={
                    "user_record_id": "data.user_info.record_id",
                    "message": "Your request has been processed."
                }
            )
        ]

        # Create switch step
        switch_step = SwitchStep(
            cases=[manager_case],
            default=default_steps
        )
        
        # Create return step
        return_step = ReturnStep(
            output_mapper={
                "user_email": "data.user_info.email",
                "notification_sent": "true"
            }
        )
        
        # Create compound action
        compound_action = CompoundAction(
            name="User Notification Workflow",
            description="Get user details and send appropriate notification",
            input_args={
                "user_id": "data.user_id",
                "manager_card": "data.notification_card"
            },
            steps=[action_step, switch_step, return_step]
        )
        
        # Test YAML generation
        yaml_dict = compound_action.to_yaml_dict()
        
        # Validate structure
        assert "input_args" in yaml_dict
        assert "steps" in yaml_dict
        assert len(yaml_dict["steps"]) == 3
        assert "action" in yaml_dict["steps"][0]
        assert "switch" in yaml_dict["steps"][1]
        assert "return" in yaml_dict["steps"][2]
        
        # Validate switch structure
        switch_dict = yaml_dict["steps"][1]["switch"]
        assert "cases" in switch_dict
        assert "default" in switch_dict
        assert len(switch_dict["cases"]) == 1
        assert switch_dict["cases"][0]["condition"] == "data.user_info.role == 'manager'"

        # Validate default structure
        default_dict = switch_dict["default"]
        assert "steps" in default_dict
        assert len(default_dict["steps"]) == 1


class TestYAMLValidationAndCompliance:
    """Test YAML output validation and compliance with Moveworks standards."""
    
    def test_yaml_serialization_format(self):
        """Test that generated YAML follows proper formatting standards."""
        # Create a compound action with various step types
        action_step = ActionStep(
            action_name="mw.get_user_details",
            output_key="user_info",
            input_args={"user_id": "data.user_id"}
        )

        script_step = ScriptStep(
            code="result = user_info['email'].lower()",
            output_key="processed_email",
            input_args={"user_info": "data.user_info"}
        )

        compound_action = CompoundAction(
            name="Test Action",
            input_args={"user_id": "data.user_id"},
            steps=[action_step, script_step]
        )

        # Generate YAML
        yaml_content = serialize_compound_action(compound_action)

        # Validate that YAML is generated without errors
        assert yaml_content is not None
        assert len(yaml_content.strip()) > 0

        # Parse back to ensure valid YAML
        parsed = yaml.safe_load(yaml_content)

        # Validate structure
        assert isinstance(parsed, dict)
        assert "input_args" in parsed
        assert "steps" in parsed
        assert len(parsed["steps"]) == 2

        # Validate script code handling
        script_code = parsed["steps"][1]["script"]["code"]
        assert "result = user_info['email'].lower()" in script_code

    def test_bender_expression_validation_in_yaml(self):
        """Test that Bender expressions are properly preserved in YAML."""
        compound_action = CompoundAction(
            name="Bender Test",
            input_args={
                "user_id": "data.user_id",
                "email": "data.user_info.email",
                "full_name": "$CONCAT(data.first_name, ' ', data.last_name)",
                "is_manager": "data.user_info.role == 'manager'"
            },
            single_step=ActionStep(
                action_name="mw.get_user_details",
                output_key="user_info",
                input_args={"user_id": "data.user_id"}
            )
        )

        yaml_content = serialize_compound_action(compound_action)
        parsed = yaml.safe_load(yaml_content)

        # Validate Bender expressions are preserved
        input_args = parsed["input_args"]
        assert input_args["user_id"] == "data.user_id"
        assert input_args["email"] == "data.user_info.email"
        assert input_args["full_name"] == "$CONCAT(data.first_name, ' ', data.last_name)"
        assert input_args["is_manager"] == "data.user_info.role == 'manager'"

    def test_progress_updates_and_delay_config_serialization(self):
        """Test that progress updates and delay configurations are properly serialized."""
        from src.moveworks_wizard.models.common import ProgressUpdates, DelayConfig
        action_step = ActionStep(
            action_name="mw.get_user_details",
            output_key="user_info",
            input_args={"user_id": "data.user_id"},
            progress_updates=ProgressUpdates(
                on_pending="Fetching user details...",
                on_complete="User details retrieved successfully"
            ),
            delay_config=DelayConfig(
                seconds=2
            )
        )

        compound_action = CompoundAction(
            name="Test Progress Updates",
            single_step=action_step
        )

        yaml_content = serialize_compound_action(compound_action)
        parsed = yaml.safe_load(yaml_content)

        action_dict = parsed["action"]

        # Validate progress updates
        assert "progress_updates" in action_dict
        progress = action_dict["progress_updates"]
        assert progress["on_pending"] == "Fetching user details..."
        assert progress["on_complete"] == "User details retrieved successfully"

        # Validate delay config
        assert "delay_config" in action_dict
        delay = action_dict["delay_config"]
        # DelayConfig values might be serialized as strings for DSL compatibility
        assert delay["seconds"] == 2 or delay["seconds"] == "2"


class TestDataFlowValidation:
    """Test data flow validation between steps."""

    def test_input_args_to_step_data_flow(self):
        """Test that input_args properly flow to step input_args."""
        compound_action = CompoundAction(
            name="Data Flow Test",
            input_args={
                "user_id": "data.user_id",
                "notification_message": "data.message"
            },
            steps=[
                ActionStep(
                    action_name="mw.get_user_details",
                    output_key="user_info",
                    input_args={"user_id": "data.user_id"}  # References compound action input
                ),
                ActionStep(
                    action_name="mw.send_plaintext_chat_notification",
                    output_key="notification_result",
                    input_args={
                        "user_record_id": "data.user_info.record_id",  # References previous step output
                        "message": "data.notification_message"  # References compound action input
                    }
                )
            ]
        )

        yaml_dict = compound_action.to_yaml_dict()

        # Validate input_args are defined at compound action level
        assert "input_args" in yaml_dict
        assert "user_id" in yaml_dict["input_args"]
        assert "notification_message" in yaml_dict["input_args"]

        # Validate first step references compound action input
        step1 = yaml_dict["steps"][0]["action"]
        assert step1["input_args"]["user_id"] == "data.user_id"

        # Validate second step references both previous step output and compound action input
        step2 = yaml_dict["steps"][1]["action"]
        assert step2["input_args"]["user_record_id"] == "data.user_info.record_id"
        assert step2["input_args"]["message"] == "data.notification_message"

    def test_script_step_data_flow(self):
        """Test data flow through script steps."""
        compound_action = CompoundAction(
            name="Script Data Flow Test",
            input_args={"user_id": "data.user_id"},
            steps=[
                ActionStep(
                    action_name="mw.get_user_details",
                    output_key="user_info",
                    input_args={"user_id": "data.user_id"}
                ),
                ScriptStep(
                    code="processed_email = user_info['email'].lower()\nresult = {'email': processed_email}",
                    output_key="processed_data",
                    input_args={"user_info": "data.user_info"}
                ),
                ActionStep(
                    action_name="mw.send_plaintext_chat_notification",
                    output_key="notification_result",
                    input_args={
                        "user_record_id": "data.user_info.record_id",
                        "message": "Email processed: data.processed_data.email"
                    }
                )
            ]
        )

        yaml_dict = compound_action.to_yaml_dict()

        # Validate script step receives data from action step
        script_step = yaml_dict["steps"][1]["script"]
        assert script_step["input_args"]["user_info"] == "data.user_info"

        # Validate final action step can reference both original action and script outputs
        final_step = yaml_dict["steps"][2]["action"]
        assert "data.user_info.record_id" in final_step["input_args"]["user_record_id"]
        assert "data.processed_data.email" in final_step["input_args"]["message"]


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge case scenarios."""

    def test_empty_compound_action_validation(self):
        """Test validation of empty compound action."""
        from pydantic import ValidationError
        with pytest.raises(ValidationError, match="Must specify either 'steps' or 'single_step'"):
            CompoundAction(name="Empty Action")

    def test_invalid_step_combinations(self):
        """Test validation of invalid step combinations."""
        from pydantic import ValidationError
        action_step = ActionStep(
            action_name="mw.get_user_details",
            output_key="user_info",
            input_args={"user_id": "data.user_id"}
        )

        # Test that you can't have both single_step and steps
        with pytest.raises(ValidationError, match="Cannot specify both 'steps' and 'single_step'"):
            CompoundAction(
                name="Invalid Action",
                single_step=action_step,
                steps=[action_step]
            )

    def test_missing_required_fields_validation(self):
        """Test validation of missing required fields."""
        from pydantic import ValidationError
        # Test action step without action_name
        with pytest.raises(ValidationError):
            ActionStep(output_key="test")

        # Test script step without code
        with pytest.raises(ValidationError):
            ScriptStep(output_key="test")

    def test_invalid_bender_expressions(self):
        """Test handling of potentially invalid Bender expressions."""
        # These should not raise errors during model creation (validation is done at wizard level)
        compound_action = CompoundAction(
            name="Bender Edge Cases",
            input_args={
                "empty_string": "",
                "special_chars": "data.field_with-dashes",
                "complex_expression": "$MAP(data.items, $LAMBDA(item, item.name))"
            },
            single_step=ActionStep(
                action_name="mw.test_action",
                output_key="result",
                input_args={"test": "data.empty_string"}
            )
        )

        # Should be able to serialize without errors
        yaml_dict = compound_action.to_yaml_dict()
        assert "input_args" in yaml_dict
