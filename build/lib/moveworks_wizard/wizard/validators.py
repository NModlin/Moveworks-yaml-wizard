"""
Validation utilities for the Moveworks Compound Action Wizard.

This module provides validation functions for user inputs and
compound action configurations.
"""

import re
from typing import Any, Dict, List, Optional, Tuple


class WizardValidators:
    """
    Collection of validation functions for wizard inputs.
    
    Provides consistent validation logic across the wizard interface.
    """
    
    @staticmethod
    def validate_compound_action_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate compound action name.
        
        Args:
            name: The name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Compound action name cannot be empty"
        
        # Check length
        if len(name.strip()) > 100:
            return False, "Compound action name must be 100 characters or less"
        
        return True, None
    
    @staticmethod
    def validate_output_key(output_key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate output key format.
        
        Args:
            output_key: The output key to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not output_key or not output_key.strip():
            return False, "Output key cannot be empty"
        
        # Check format - should be alphanumeric with underscores/hyphens
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', output_key.strip()):
            return False, "Output key must start with a letter and contain only letters, numbers, underscores, and hyphens"
        
        # Check length
        if len(output_key.strip()) > 50:
            return False, "Output key must be 50 characters or less"
        
        return True, None
    
    @staticmethod
    def validate_action_name(action_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate action name format.
        
        Args:
            action_name: The action name to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not action_name or not action_name.strip():
            return False, "Action name cannot be empty"
        
        action_name = action_name.strip()
        
        # Check if it's a built-in action
        if action_name.startswith('mw.'):
            # Built-in action validation
            if len(action_name) < 4:  # "mw." + at least one character
                return False, "Built-in action name must have content after 'mw.'"
            
            # Check format after mw.
            suffix = action_name[3:]
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', suffix):
                return False, "Built-in action name must be alphanumeric with underscores after 'mw.'"
        else:
            # External action validation (could be UUID or other identifier)
            if len(action_name) > 100:
                return False, "Action name must be 100 characters or less"
        
        return True, None
    
    @staticmethod
    def validate_bender_expression(expression: str) -> Tuple[bool, Optional[str]]:
        """
        Basic validation for Bender expressions.
        
        Args:
            expression: The Bender expression to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not expression or not expression.strip():
            return False, "Bender expression cannot be empty"
        
        expression = expression.strip()
        
        # Check for common Bender patterns
        valid_patterns = [
            r'^data\.',           # data.field
            r'^meta_info\.',      # meta_info.field
            r'^requestor\.',      # requestor.field
            r'^\$[A-Z_]+\(',     # $FUNCTION()
            r'^["\'].*["\']$',   # String literals
            r'^\d+$',            # Numbers
            r'^true|false$',     # Booleans
        ]
        
        # Check if expression matches any valid pattern
        for pattern in valid_patterns:
            if re.match(pattern, expression, re.IGNORECASE):
                return True, None
        
        # If it doesn't match common patterns, give a warning but allow it
        # (since Bender syntax is complex and we can't validate everything)
        return True, None
    
    @staticmethod
    def validate_python_code(code: str) -> Tuple[bool, Optional[str]]:
        """
        Basic validation for Python/APIthon code.

        Args:
            code: The Python code to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not code or not code.strip():
            return False, "Python code cannot be empty"

        # Basic syntax check - try both as expression and as statement
        try:
            # First try as expression (for simple return values)
            try:
                compile(code, '<string>', 'eval')
                return True, None
            except SyntaxError:
                # If that fails, try as statement
                compile(code, '<string>', 'exec')
                return True, None
        except SyntaxError as e:
            return False, f"Python syntax error: {e.msg}"
        except Exception as e:
            return False, f"Code validation error: {str(e)}"
    
    @staticmethod
    def validate_input_args(input_args: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate input arguments dictionary.
        
        Args:
            input_args: Dictionary of input arguments
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not input_args:
            return True, None  # Empty input args are valid
        
        for arg_name, arg_value in input_args.items():
            # Validate argument name
            if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', arg_name):
                return False, f"Invalid argument name '{arg_name}': must start with letter and contain only letters, numbers, and underscores"
            
            # Validate argument value (basic check)
            if arg_value is None:
                return False, f"Argument '{arg_name}' cannot have null value"
            
            if isinstance(arg_value, str):
                # For string values, do basic Bender validation
                is_valid, error = WizardValidators.validate_bender_expression(arg_value)
                if not is_valid:
                    return False, f"Invalid value for argument '{arg_name}': {error}"
        
        return True, None
    
    @staticmethod
    def validate_progress_updates(progress_updates: Dict[str, str]) -> Tuple[bool, Optional[str]]:
        """
        Validate progress updates configuration.
        
        Args:
            progress_updates: Dictionary with progress update messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not progress_updates:
            return True, None
        
        # Check required fields
        for field in ['on_pending', 'on_complete']:
            if field in progress_updates:
                message = progress_updates[field]
                if not message or not message.strip():
                    return False, f"Progress update message '{field}' cannot be empty"
                
                if len(message.strip()) > 200:
                    return False, f"Progress update message '{field}' must be 200 characters or less"
        
        return True, None
    
    @staticmethod
    def validate_compound_action_structure(compound_action_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate the overall compound action structure.
        
        Args:
            compound_action_dict: Dictionary representation of compound action
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check that we have either steps or a single step
        has_steps = 'steps' in compound_action_dict
        has_single_step = any(key in compound_action_dict for key in ['action', 'script', 'switch', 'for', 'parallel', 'try_catch', 'return', 'raise'])
        
        if not has_steps and not has_single_step:
            return False, "Compound action must have either 'steps' or a single step (action, script, etc.)"
        
        if has_steps and has_single_step:
            return False, "Compound action cannot have both 'steps' and a single step at the root level"
        
        # Validate steps structure
        if has_steps:
            steps = compound_action_dict['steps']
            if not isinstance(steps, list):
                return False, "'steps' must be a list"
            
            if len(steps) == 0:
                return False, "'steps' list cannot be empty"
        
        return True, None
    
    @staticmethod
    def get_validation_summary(errors: List[str]) -> str:
        """
        Generate a summary of validation errors.
        
        Args:
            errors: List of error messages
            
        Returns:
            Formatted error summary
        """
        if not errors:
            return "✅ All validations passed"
        
        summary = f"❌ Found {len(errors)} validation error(s):\n"
        for i, error in enumerate(errors, 1):
            summary += f"  {i}. {error}\n"
        
        return summary.strip()


# Standalone validator functions for CLI compatibility
def validate_bender_expression(expression: str) -> Tuple[bool, Optional[str]]:
    """Basic validation for Bender expressions."""
    return WizardValidators.validate_bender_expression(expression)


def validate_action_name(action_name: str) -> Tuple[bool, Optional[str]]:
    """Validate action name format."""
    return WizardValidators.validate_action_name(action_name)
