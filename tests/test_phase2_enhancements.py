"""
Tests for Phase 2 enhancements to the Moveworks Compound Action Wizard.

This module tests the enhanced wizard functionality including:
- Built-in action catalog
- Enhanced validation
- Improved user experience
"""

import pytest
from unittest.mock import patch, MagicMock

from src.moveworks_wizard.catalog import builtin_catalog, BuiltinAction, ActionParameter
from src.moveworks_wizard.wizard.validators import WizardValidators
from src.moveworks_wizard.wizard.cli import CompoundActionWizard
from src.moveworks_wizard.models.actions import ActionStep
from src.moveworks_wizard.models.base import CompoundAction


class TestBuiltinActionCatalog:
    """Test the built-in action catalog functionality."""
    
    def test_catalog_initialization(self):
        """Test that the catalog initializes with actions."""
        assert len(builtin_catalog.get_all_actions()) > 0
        assert len(builtin_catalog.get_all_categories()) > 0
    
    def test_get_builtin_action(self):
        """Test retrieving a specific built-in action."""
        action = builtin_catalog.get_action("mw.send_plaintext_chat_notification")
        assert action is not None
        assert action.name == "mw.send_plaintext_chat_notification"
        assert action.category == "Communication"
        assert len(action.parameters) > 0
    
    def test_get_actions_by_category(self):
        """Test filtering actions by category."""
        communication_actions = builtin_catalog.get_actions_by_category("Communication")
        assert len(communication_actions) > 0
        
        for action in communication_actions:
            assert action.category == "Communication"
    
    def test_search_actions(self):
        """Test searching for actions."""
        # Search by name
        results = builtin_catalog.search_actions("notification")
        assert len(results) > 0
        
        # Search by description
        results = builtin_catalog.search_actions("user")
        assert len(results) > 0
        
        # Search with no results
        results = builtin_catalog.search_actions("nonexistent_action")
        assert len(results) == 0
    
    def test_is_builtin_action(self):
        """Test checking if an action is built-in."""
        assert builtin_catalog.is_builtin_action("mw.send_plaintext_chat_notification")
        assert not builtin_catalog.is_builtin_action("custom_action")
        assert not builtin_catalog.is_builtin_action("some.external.action")


class TestEnhancedValidation:
    """Test enhanced validation functionality."""
    
    def test_validate_compound_action_name(self):
        """Test compound action name validation."""
        # Valid names
        assert WizardValidators.validate_compound_action_name("Valid Name")[0]
        assert WizardValidators.validate_compound_action_name("Test Action 123")[0]
        
        # Invalid names
        assert not WizardValidators.validate_compound_action_name("")[0]
        assert not WizardValidators.validate_compound_action_name("   ")[0]
        assert not WizardValidators.validate_compound_action_name("x" * 101)[0]
    
    def test_validate_output_key(self):
        """Test output key validation."""
        # Valid keys
        assert WizardValidators.validate_output_key("valid_key")[0]
        assert WizardValidators.validate_output_key("user_info")[0]
        assert WizardValidators.validate_output_key("result-data")[0]
        
        # Invalid keys
        assert not WizardValidators.validate_output_key("")[0]
        assert not WizardValidators.validate_output_key("123invalid")[0]
        assert not WizardValidators.validate_output_key("invalid key")[0]
        assert not WizardValidators.validate_output_key("x" * 51)[0]
    
    def test_validate_action_name(self):
        """Test action name validation."""
        # Valid built-in actions
        assert WizardValidators.validate_action_name("mw.send_notification")[0]
        assert WizardValidators.validate_action_name("mw.get_user_details")[0]
        
        # Valid external actions
        assert WizardValidators.validate_action_name("custom_action")[0]
        assert WizardValidators.validate_action_name("external-service-call")[0]
        
        # Invalid names
        assert not WizardValidators.validate_action_name("")[0]
        assert not WizardValidators.validate_action_name("mw.")[0]
        assert not WizardValidators.validate_action_name("mw.123invalid")[0]
    
    def test_validate_bender_expression(self):
        """Test Bender expression validation."""
        # Valid expressions
        assert WizardValidators.validate_bender_expression("data.user_id")[0]
        assert WizardValidators.validate_bender_expression("meta_info.requestor.email")[0]
        assert WizardValidators.validate_bender_expression('"string literal"')[0]
        assert WizardValidators.validate_bender_expression("123")[0]
        assert WizardValidators.validate_bender_expression("true")[0]
        
        # Invalid expressions
        assert not WizardValidators.validate_bender_expression("")[0]
        assert not WizardValidators.validate_bender_expression("   ")[0]
    
    def test_validate_python_code(self):
        """Test Python code validation."""
        # Valid code (expressions)
        assert WizardValidators.validate_python_code("'hello'")[0]
        assert WizardValidators.validate_python_code("user_info.get('email', '')")[0]

        # Valid code (statements)
        assert WizardValidators.validate_python_code("x = 1")[0]
        assert WizardValidators.validate_python_code("result = data.get('value')\nprocessed = result.upper()")[0]

        # Invalid code
        assert not WizardValidators.validate_python_code("")[0]
        assert not WizardValidators.validate_python_code("invalid syntax ][")[0]
    
    def test_validate_input_args(self):
        """Test input arguments validation."""
        # Valid input args
        valid_args = {
            "user_id": "data.employee_id",
            "message": '"Hello World"'
        }
        assert WizardValidators.validate_input_args(valid_args)[0]
        
        # Empty args (valid)
        assert WizardValidators.validate_input_args({})[0]
        assert WizardValidators.validate_input_args(None)[0]
        
        # Invalid args
        invalid_args = {
            "123invalid": "data.user_id"  # Invalid argument name
        }
        assert not WizardValidators.validate_input_args(invalid_args)[0]
    
    def test_validate_progress_updates(self):
        """Test progress updates validation."""
        # Valid progress updates
        valid_updates = {
            "on_pending": "Processing request...",
            "on_complete": "Request completed successfully"
        }
        assert WizardValidators.validate_progress_updates(valid_updates)[0]
        
        # Empty updates (valid)
        assert WizardValidators.validate_progress_updates({})[0]
        assert WizardValidators.validate_progress_updates(None)[0]
        
        # Invalid updates
        invalid_updates = {
            "on_pending": "",  # Empty message
            "on_complete": "Valid message"
        }
        assert not WizardValidators.validate_progress_updates(invalid_updates)[0]


class TestEnhancedWizard:
    """Test enhanced wizard functionality."""
    
    def test_wizard_initialization(self):
        """Test wizard initializes correctly."""
        wizard = CompoundActionWizard()
        assert wizard.compound_action is None
        assert wizard.steps == []
    
    @patch('click.prompt')
    @patch('click.confirm')
    def test_enhanced_input_validation(self, mock_confirm, mock_prompt):
        """Test enhanced input validation in wizard."""
        wizard = CompoundActionWizard()
        
        # Mock user inputs
        mock_prompt.side_effect = [
            "Test Action",  # name
            "Test description",  # description
            "user_id",  # arg name
            "data.employee_id",  # arg value
            "done"  # finish args
        ]
        mock_confirm.side_effect = [True, False]  # add args, no steps yet
        
        # Test input argument validation
        input_args = wizard._add_input_arguments()
        
        assert "user_id" in input_args
        assert input_args["user_id"] == "data.employee_id"
    
    def test_builtin_action_integration(self):
        """Test that built-in actions are properly integrated."""
        wizard = CompoundActionWizard()
        
        # Test that catalog is accessible
        action = builtin_catalog.get_action("mw.send_plaintext_chat_notification")
        assert action is not None
        
        # Test action parameter structure
        assert hasattr(action, 'parameters')
        assert len(action.parameters) > 0
        
        for param in action.parameters:
            assert hasattr(param, 'name')
            assert hasattr(param, 'type')
            assert hasattr(param, 'required')
            assert hasattr(param, 'description')


class TestActionStepEnhancements:
    """Test enhancements to action step creation."""
    
    def test_action_step_with_builtin_validation(self):
        """Test action step creation with built-in action validation."""
        # Create action step with built-in action
        step = ActionStep(
            action_name="mw.send_plaintext_chat_notification",
            output_key="notification_result",
            input_args={
                "user_record_id": "data.user_info.record_id",
                "message": "Your request has been processed"
            }
        )
        
        assert step.action_name == "mw.send_plaintext_chat_notification"
        assert step.output_key == "notification_result"
        assert "user_record_id" in step.input_args
        assert "message" in step.input_args
    
    def test_action_step_yaml_generation(self):
        """Test YAML generation for enhanced action steps."""
        step = ActionStep(
            action_name="mw.get_user_details",
            output_key="user_info",
            input_args={"user_id": "data.employee_id"},
            progress_updates={
                "on_pending": "Fetching user details...",
                "on_complete": "User details retrieved successfully"
            }
        )
        
        yaml_dict = step.to_yaml_dict()
        
        assert "action" in yaml_dict
        action_data = yaml_dict["action"]
        assert action_data["action_name"] == "mw.get_user_details"
        assert action_data["output_key"] == "user_info"
        assert "input_args" in action_data
        assert "progress_updates" in action_data


class TestCompoundActionEnhancements:
    """Test enhancements to compound action creation."""
    
    def test_compound_action_with_multiple_step_types(self):
        """Test compound action with various step types."""
        # Create action step
        action_step = ActionStep(
            action_name="mw.get_user_details",
            output_key="user_info",
            input_args={"user_id": "data.employee_id"}
        )
        
        # Create compound action with multiple steps
        compound_action = CompoundAction(
            name="Enhanced User Processing",
            description="Process user with enhanced features",
            input_args={"employee_id": "data.user_id"},
            steps=[action_step]
        )
        
        assert compound_action.name == "Enhanced User Processing"
        assert len(compound_action.steps) == 1
        assert compound_action.input_args["employee_id"] == "data.user_id"
    
    def test_compound_action_yaml_generation(self):
        """Test YAML generation for enhanced compound actions."""
        action_step = ActionStep(
            action_name="mw.send_plaintext_chat_notification",
            output_key="notification_result",
            input_args={
                "user_record_id": "data.user_info.record_id",
                "message": "Processing complete"
            }
        )
        
        compound_action = CompoundAction(
            input_args={"user_id": "data.employee_id"},
            steps=[action_step]
        )
        
        yaml_dict = compound_action.to_yaml_dict()
        
        assert "input_args" in yaml_dict
        assert "steps" in yaml_dict
        assert len(yaml_dict["steps"]) == 1
        assert "action" in yaml_dict["steps"][0]
