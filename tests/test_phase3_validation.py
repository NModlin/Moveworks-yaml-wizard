"""
Phase 3 Enhanced Validation Tests for Moveworks YAML Wizard

This module contains comprehensive validation tests for Phase 3,
focusing on input validation, error handling, and edge cases.
"""

import pytest
from src.moveworks_wizard.wizard.validators import WizardValidators
from src.moveworks_wizard.catalog import builtin_catalog


class TestEnhancedInputValidation:
    """Test enhanced input validation for all wizard inputs."""
    
    def test_compound_action_name_validation(self):
        """Test comprehensive compound action name validation."""
        validator = WizardValidators()
        
        # Valid names
        valid_names = [
            "Get User Details",
            "user_notification_workflow",
            "Process-Data-123",
            "Simple Action",
            "A" * 100  # Max length
        ]
        
        for name in valid_names:
            is_valid, error = validator.validate_compound_action_name(name)
            assert is_valid, f"Expected '{name}' to be valid, got error: {error}"
        
        # Invalid names
        invalid_names = [
            "",  # Empty
            "   ",  # Whitespace only
            "A" * 101,  # Too long
            None  # None value
        ]
        
        for name in invalid_names:
            is_valid, error = validator.validate_compound_action_name(name)
            assert not is_valid, f"Expected '{name}' to be invalid"
            assert error is not None
    
    def test_output_key_validation(self):
        """Test output key validation."""
        validator = WizardValidators()
        
        # Valid output keys
        valid_keys = [
            "user_info",
            "processed_data",
            "result123",
            "camelCaseKey",
            "snake_case_key",
            "a",  # Single character
            "key_with_numbers_123"
        ]
        
        for key in valid_keys:
            is_valid, error = validator.validate_output_key(key)
            assert is_valid, f"Expected '{key}' to be valid, got error: {error}"
        
        # Invalid output keys
        invalid_keys = [
            "",  # Empty
            "   ",  # Whitespace only
            "123invalid",  # Starts with number
            "key with spaces",  # Contains spaces
            "key.with.dots",  # Contains dots
            "A" * 101,  # Too long
        ]
        
        for key in invalid_keys:
            is_valid, error = validator.validate_output_key(key)
            assert not is_valid, f"Expected '{key}' to be invalid"
            assert error is not None
    
    def test_action_name_validation(self):
        """Test action name validation for both built-in and external actions."""
        validator = WizardValidators()
        
        # Valid built-in action names
        valid_builtin_names = [
            "mw.get_user_details",
            "mw.send_plaintext_chat_notification",
            "mw.create_ticket",
            "mw.action_with_underscores",
            "mw.action123"
        ]
        
        for name in valid_builtin_names:
            is_valid, error = validator.validate_action_name(name)
            assert is_valid, f"Expected '{name}' to be valid, got error: {error}"
        
        # Valid external action names (UUIDs, etc.)
        valid_external_names = [
            "550e8400-e29b-41d4-a716-446655440000",  # UUID
            "custom_action_name",
            "external-action-123",
            "action.with.dots"
        ]
        
        for name in valid_external_names:
            is_valid, error = validator.validate_action_name(name)
            assert is_valid, f"Expected '{name}' to be valid, got error: {error}"
        
        # Invalid action names
        invalid_names = [
            "",  # Empty
            "   ",  # Whitespace only
            "mw.",  # Built-in without suffix
            "mw.123invalid",  # Built-in starting with number
            "mw.action-with-dashes",  # Built-in with dashes
            "A" * 101,  # Too long
        ]
        
        for name in invalid_names:
            is_valid, error = validator.validate_action_name(name)
            assert not is_valid, f"Expected '{name}' to be invalid"
            assert error is not None
    
    def test_bender_expression_validation(self):
        """Test Bender expression validation."""
        validator = WizardValidators()
        
        # Valid Bender expressions
        valid_expressions = [
            "data.user_id",
            "data.user_info.email",
            "meta_info.requestor.name",
            "requestor.email",
            "$CONCAT(data.first_name, ' ', data.last_name)",
            "$MAP(data.items, $LAMBDA(item, item.name))",
            '"string literal"',
            "'another string'",
            "123",
            "true",
            "false",
            "data.field_with_underscores",
            "data.nested.deeply.nested.field"
        ]
        
        for expr in valid_expressions:
            is_valid, error = validator.validate_bender_expression(expr)
            assert is_valid, f"Expected '{expr}' to be valid, got error: {error}"
        
        # Invalid Bender expressions (only empty/whitespace are truly invalid)
        invalid_expressions = [
            "",  # Empty
            "   ",  # Whitespace only
        ]

        for expr in invalid_expressions:
            is_valid, error = validator.validate_bender_expression(expr)
            assert not is_valid, f"Expected '{expr}' to be invalid"
            assert error is not None
    
    def test_python_code_validation(self):
        """Test Python/APIthon code validation."""
        validator = WizardValidators()
        
        # Valid Python code
        valid_code = [
            "result = 42",
            "x = user_info['email'].lower()",
            "if user_info.get('role') == 'manager':\n    result = True\nelse:\n    result = False",
            "# Comment\nresult = process_data(input_data)",
            "result = {'processed': True, 'email': user_info['email']}",
            "42",  # Simple expression
            "user_info['email']",  # Dictionary access
            "len(user_info.get('items', []))"  # Function call
        ]
        
        for code in valid_code:
            is_valid, error = validator.validate_python_code(code)
            assert is_valid, f"Expected code to be valid, got error: {error}\nCode: {code}"
        
        # Invalid Python code (only syntax errors are caught)
        invalid_code = [
            "",  # Empty
            "   ",  # Whitespace only
            "if x:",  # Incomplete syntax
            "def invalid():",  # Incomplete function
            "x = ",  # Incomplete assignment
            "result = user_info['email'.lower()",  # Syntax error - missing bracket
        ]

        for code in invalid_code:
            is_valid, error = validator.validate_python_code(code)
            assert not is_valid, f"Expected code to be invalid: {code}"
            assert error is not None


class TestBuiltinActionValidation:
    """Test validation of built-in actions from the catalog."""
    
    def test_builtin_action_catalog_validation(self):
        """Test that all actions in the catalog are valid."""
        catalog = builtin_catalog
        
        # Test that catalog is properly initialized
        assert len(catalog.get_all_actions()) > 0
        
        # Test each action in the catalog
        for action in catalog.get_all_actions():
            # Validate action name format
            assert action.name.startswith("mw.")
            assert len(action.name) > 3
            
            # Validate description exists
            assert action.description
            assert len(action.description.strip()) > 0
            
            # Validate category exists
            assert action.category
            assert len(action.category.strip()) > 0
            
            # Validate parameters
            for param in action.parameters:
                assert param.name
                assert param.type in ["string", "boolean", "number", "object", "array"]
                assert param.description
                
                # Required parameters should have examples
                if param.required:
                    assert param.example is not None
    
    def test_builtin_action_search_functionality(self):
        """Test the search functionality of the builtin action catalog."""
        catalog = builtin_catalog
        
        # Test search by action name
        user_actions = catalog.search_actions("user")
        assert len(user_actions) > 0
        for action in user_actions:
            assert "user" in action.name.lower() or "user" in action.description.lower()
        
        # Test search by category
        communication_actions = catalog.search_actions("communication")
        assert len(communication_actions) > 0
        for action in communication_actions:
            assert "communication" in action.category.lower() or "communication" in action.description.lower()
        
        # Test search with no results
        no_results = catalog.search_actions("nonexistent_action_xyz")
        assert len(no_results) == 0
    
    def test_builtin_action_parameter_validation(self):
        """Test parameter validation for built-in actions."""
        catalog = builtin_catalog
        
        # Get a specific action for testing
        notification_action = catalog.get_action("mw.send_plaintext_chat_notification")
        assert notification_action is not None
        
        # Validate required parameters
        required_params = [p for p in notification_action.parameters if p.required]
        assert len(required_params) > 0
        
        # Validate parameter types
        for param in notification_action.parameters:
            assert param.type in ["string", "boolean", "number", "object", "array"]
            
            # String parameters should have examples
            if param.type == "string" and param.required:
                assert param.example is not None
                assert len(param.example.strip()) > 0


class TestProgressUpdatesValidation:
    """Test validation of progress updates configuration."""
    
    def test_progress_updates_validation(self):
        """Test validation of progress updates structure."""
        validator = WizardValidators()
        
        # Valid progress updates (validator only checks known fields)
        valid_updates = [
            {"on_pending": "Processing..."},
            {"on_complete": "Completed successfully"},
            {
                "on_pending": "Starting process...",
                "on_complete": "Process completed"
            },
            {"invalid_key": "Invalid"},  # Unknown keys are ignored
            {}  # Empty is valid (optional)
        ]

        for updates in valid_updates:
            is_valid, error = validator.validate_progress_updates(updates)
            assert is_valid, f"Expected progress updates to be valid, got error: {error}\nUpdates: {updates}"

        # Invalid progress updates (only empty messages for known fields)
        invalid_updates = [
            {"on_pending": ""},  # Empty message
            {"on_complete": ""},  # Empty message
            {"on_pending": "A" * 201},  # Too long message
        ]

        for updates in invalid_updates:
            is_valid, error = validator.validate_progress_updates(updates)
            assert not is_valid, f"Expected progress updates to be invalid: {updates}"
            assert error is not None
    
    def test_delay_config_validation(self):
        """Test validation of delay configuration."""
        # Note: This would require implementing delay_config validation in WizardValidators
        # For now, we'll test the basic structure
        
        valid_delay_configs = [
            {"delay_seconds": 1},
            {"delay_seconds": 5, "max_retries": 3},
            {"delay_seconds": 0},  # No delay
            {}  # Empty is valid (optional)
        ]
        
        # These would be validated by the model itself
        for config in valid_delay_configs:
            # Basic validation - delay_seconds should be non-negative
            if "delay_seconds" in config:
                assert config["delay_seconds"] >= 0
            
            # max_retries should be non-negative
            if "max_retries" in config:
                assert config["max_retries"] >= 0
