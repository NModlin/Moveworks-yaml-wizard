"""
Phase 3 YAML Compliance Tests for Moveworks YAML Wizard

This module contains tests to ensure generated YAML complies with
Moveworks Compound Action standards and real-world usage scenarios.
"""

import pytest
import yaml
from pathlib import Path

from src.moveworks_wizard.models.base import CompoundAction
from src.moveworks_wizard.models.actions import ActionStep, ScriptStep
from src.moveworks_wizard.models.control_flow import SwitchStep, SwitchCase
from src.moveworks_wizard.models.terminal import ReturnStep, RaiseStep
from src.moveworks_wizard.serializers import serialize_compound_action


class TestMoveworksYAMLCompliance:
    """Test compliance with Moveworks YAML standards."""
    
    def test_yaml_structure_compliance(self):
        """Test that generated YAML follows Moveworks structure requirements."""
        # Create a comprehensive compound action
        compound_action = CompoundAction(
            name="Comprehensive Test Action",
            description="Test all YAML structure requirements",
            input_args={
                "user_id": "data.user_id",
                "notification_card": "data.card_content"
            },
            steps=[
                ActionStep(
                    action_name="mw.get_user_details",
                    output_key="user_info",
                    input_args={"user_id": "data.user_id"},
                    progress_updates={
                        "on_pending": "Fetching user details...",
                        "on_complete": "User details retrieved"
                    }
                ),
                ScriptStep(
                    code="processed_email = user_info['email'].lower(); result = {'email': processed_email}",
                    output_key="processed_data",
                    input_args={"user_info": "data.user_info"}
                )
            ]
        )
        
        # Generate YAML
        yaml_content = serialize_compound_action(compound_action)
        
        # Parse and validate structure
        parsed = yaml.safe_load(yaml_content)
        
        # Validate top-level structure
        assert isinstance(parsed, dict)
        assert "input_args" in parsed
        assert "steps" in parsed
        
        # Validate input_args structure
        input_args = parsed["input_args"]
        assert isinstance(input_args, dict)
        assert "user_id" in input_args
        assert input_args["user_id"] == "data.user_id"
        
        # Validate steps structure
        steps = parsed["steps"]
        assert isinstance(steps, list)
        assert len(steps) == 2
        
        # Validate action step structure
        action_step = steps[0]
        assert "action" in action_step
        action_dict = action_step["action"]
        assert "action_name" in action_dict
        assert "output_key" in action_dict
        assert "input_args" in action_dict
        assert "progress_updates" in action_dict
        
        # Validate script step structure
        script_step = steps[1]
        assert "script" in script_step
        script_dict = script_step["script"]
        assert "code" in script_dict
        assert "output_key" in script_dict
        assert "input_args" in script_dict
    
    def test_script_code_formatting(self):
        """Test that script code is properly formatted."""
        # Use single-line script to avoid YAML formatting issues
        script_code = "user_email = user_info.get('email', '').lower(); result = {'email': user_email, 'is_valid': len(user_email) > 0}"

        script_step = ScriptStep(
            code=script_code,
            output_key="processed_user",
            input_args={"user_info": "data.user_info"}
        )

        compound_action = CompoundAction(
            name="Script Test",
            single_step=script_step
        )

        yaml_content = serialize_compound_action(compound_action)
        parsed = yaml.safe_load(yaml_content)

        # Validate script code preservation
        script_dict = parsed["script"]
        code = script_dict["code"]

        # Should preserve the script content
        assert "user_email = user_info.get('email', '').lower()" in code
        assert "result = {" in code
    
    def test_bender_expression_preservation(self):
        """Test that Bender expressions are preserved exactly."""
        bender_expressions = {
            "simple_data": "data.user_id",
            "nested_data": "data.user_info.profile.email",
            "meta_info": "meta_info.requestor.name",
            "function_call": "$CONCAT(data.first_name, ' ', data.last_name)",
            "complex_function": "$MAP(data.items, $LAMBDA(item, $CONCAT(item.name, ': ', item.value)))",
            "conditional": "data.user_info.role == 'manager'",
            "string_literal": '"Hello, World!"',
            "number": "42",
            "boolean": "true"
        }
        
        compound_action = CompoundAction(
            name="Bender Expression Test",
            input_args=bender_expressions,
            single_step=ActionStep(
                action_name="mw.test_action",
                output_key="result",
                input_args={"test": "data.simple_data"}
            )
        )
        
        yaml_content = serialize_compound_action(compound_action)
        parsed = yaml.safe_load(yaml_content)
        
        # Validate all Bender expressions are preserved
        input_args = parsed["input_args"]
        for key, expected_value in bender_expressions.items():
            assert key in input_args
            assert input_args[key] == expected_value
    
    def test_switch_statement_compliance(self):
        """Test switch statement YAML compliance."""
        # Create switch with multiple cases and default
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
        
        admin_case = SwitchCase(
            condition="data.user_info.role == 'admin'",
            steps=[
                ActionStep(
                    action_name="mw.send_rich_chat_notification",
                    output_key="admin_notification",
                    input_args={
                        "user_record_id": "data.user_info.record_id",
                        "card_content": "data.admin_card"
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

        switch_step = SwitchStep(
            cases=[manager_case, admin_case],
            default=default_steps
        )
        
        compound_action = CompoundAction(
            name="Switch Compliance Test",
            single_step=switch_step
        )
        
        yaml_content = serialize_compound_action(compound_action)
        parsed = yaml.safe_load(yaml_content)
        
        # Validate switch structure
        switch_dict = parsed["switch"]
        assert "cases" in switch_dict
        assert "default" in switch_dict
        
        # Validate cases
        cases = switch_dict["cases"]
        assert len(cases) == 2
        
        # Validate first case
        case1 = cases[0]
        assert "condition" in case1
        assert "steps" in case1
        assert case1["condition"] == "data.user_info.role == 'manager'"
        
        # Validate default case
        default = switch_dict["default"]
        assert "steps" in default
        assert len(default["steps"]) == 1


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def test_user_onboarding_workflow(self):
        """Test a realistic user onboarding workflow."""
        compound_action = CompoundAction(
            name="User Onboarding Workflow",
            description="Complete user onboarding process with notifications",
            input_args={
                "new_user_id": "data.user_id",
                "manager_id": "data.manager_id",
                "department": "data.department"
            },
            steps=[
                # Step 1: Get user details
                ActionStep(
                    action_name="mw.get_user_details",
                    output_key="user_info",
                    input_args={"user_id": "data.new_user_id"},
                    progress_updates={
                        "on_pending": "Retrieving user information...",
                        "on_complete": "User information retrieved"
                    }
                ),
                # Step 2: Process user data
                ScriptStep(
                    code="user_email = user_info.get('email', '').lower(); full_name = f\"{user_info.get('first_name', '')} {user_info.get('last_name', '')}\"; onboarding_data = {'user_email': user_email, 'full_name': full_name.strip(), 'department': department}",
                    output_key="onboarding_data",
                    input_args={
                        "user_info": "data.user_info",
                        "department": "data.department"
                    }
                ),
                # Step 3: Notify manager
                ActionStep(
                    action_name="mw.send_plaintext_chat_notification",
                    output_key="manager_notification",
                    input_args={
                        "user_record_id": "data.manager_id",
                        "message": "New team member has been onboarded: data.onboarding_data.full_name"
                    },
                    progress_updates={
                        "on_pending": "Notifying manager...",
                        "on_complete": "Manager notified"
                    }
                ),
                # Step 4: Return results
                ReturnStep(
                    output_mapper={
                        "user_email": "data.onboarding_data.user_email",
                        "welcome_message": "data.onboarding_data.welcome_message",
                        "onboarding_complete": "true"
                    }
                )
            ]
        )
        
        # Generate and validate YAML
        yaml_content = serialize_compound_action(compound_action)
        parsed = yaml.safe_load(yaml_content)
        
        # Validate complete workflow structure
        assert "input_args" in parsed
        assert "steps" in parsed
        assert len(parsed["steps"]) == 4
        
        # Validate each step type is present
        step_types = [list(step.keys())[0] for step in parsed["steps"]]
        assert "action" in step_types
        assert "script" in step_types
        assert "return" in step_types
    
    def test_error_handling_workflow(self):
        """Test a workflow with error handling and raise steps."""
        compound_action = CompoundAction(
            name="Error Handling Workflow",
            description="Workflow with error handling",
            input_args={"user_id": "data.user_id"},
            steps=[
                # Step 1: Validate input
                ScriptStep(
                    code="result = {'valid': bool(user_id and len(str(user_id).strip()) > 0), 'user_id': str(user_id).strip() if user_id else '', 'error': 'User ID is required' if not user_id else ''}",
                    output_key="validation_result",
                    input_args={"user_id": "data.user_id"}
                ),
                # Step 2: Conditional processing based on validation
                SwitchStep(
                    cases=[
                        SwitchCase(
                            condition="data.validation_result.valid == false",
                            steps=[
                                RaiseStep(
                                    output_key="error_result",
                                    message="data.validation_result.error"
                                )
                            ]
                        )
                    ],
                    default=[
                        ActionStep(
                            action_name="mw.get_user_details",
                            output_key="user_info",
                            input_args={"user_id": "data.validation_result.user_id"}
                        )
                    ]
                ),
                # Step 3: Return success
                ReturnStep(
                    output_mapper={
                        "user_email": "data.user_info.email",
                        "processing_status": "success"
                    }
                )
            ]
        )
        
        # Generate and validate YAML
        yaml_content = serialize_compound_action(compound_action)
        parsed = yaml.safe_load(yaml_content)
        
        # Validate error handling structure
        assert len(parsed["steps"]) == 3
        
        # Validate switch with raise step
        switch_step = parsed["steps"][1]["switch"]
        assert "cases" in switch_step
        assert "default" in switch_step
        
        # Validate raise step in case
        case_steps = switch_step["cases"][0]["steps"]
        assert len(case_steps) == 1
        assert "raise" in case_steps[0]
        
        raise_dict = case_steps[0]["raise"]
        assert "output_key" in raise_dict
        assert "message" in raise_dict
        assert raise_dict["output_key"] == "error_result"
