"""
Prompt utilities for the Moveworks Compound Action Wizard.

This module provides standardized prompts and user interaction utilities
for the wizard interface.
"""

import click
from typing import Any, Dict, List, Optional


class WizardPrompts:
    """
    Collection of standardized prompts for the wizard interface.
    
    Provides consistent user interaction patterns and input validation.
    """
    
    @staticmethod
    def welcome_message():
        """Display the welcome message for the wizard."""
        click.echo("🧙 Welcome to the Moveworks Compound Action Wizard!")
        click.echo("This wizard will help you create valid Compound Action YAML for Action Activities.")
        click.echo("The generated YAML is designed for use in the post-April 2025 Plugin architecture.")
        click.echo()
    
    @staticmethod
    def prompt_basic_info() -> Dict[str, Optional[str]]:
        """
        Prompt for basic compound action information.
        
        Returns:
            Dictionary with name and description
        """
        click.echo("📝 Let's start with basic information about your Compound Action:")
        
        name = click.prompt("Enter a name for your Compound Action", type=str)
        description = click.prompt(
            "Enter a description (optional)", 
            default="", 
            show_default=False
        )
        
        return {
            "name": name if name.strip() else None,
            "description": description if description.strip() else None
        }
    
    @staticmethod
    def confirm_input_args() -> bool:
        """Ask if user wants to add input arguments."""
        return click.confirm("Do you want to add input arguments?")
    
    @staticmethod
    def prompt_input_args() -> Dict[str, Any]:
        """
        Prompt for input arguments using Bender syntax.
        
        Returns:
            Dictionary of input arguments
        """
        click.echo("\n📝 Adding input arguments...")
        click.echo("Input arguments use Moveworks Data Mapping (Bender) syntax.")
        click.echo("Examples:")
        click.echo("  - data.user_id")
        click.echo("  - meta_info.requestor.email") 
        click.echo("  - data.ticket.priority")
        click.echo()
        
        input_args = {}
        
        while True:
            arg_name = click.prompt(
                "Enter argument name (or 'done' to finish)", 
                type=str
            )
            
            if arg_name.lower() == 'done':
                break
            
            # Validate argument name
            if not arg_name.replace('_', '').replace('-', '').isalnum():
                click.echo("❌ Invalid argument name. Use alphanumeric characters with underscores/hyphens.")
                continue
            
            arg_value = click.prompt(
                f"Enter value for '{arg_name}' (Bender syntax)", 
                type=str
            )
            
            input_args[arg_name] = arg_value
            click.echo(f"✅ Added: {arg_name} = {arg_value}")
        
        return input_args
    
    @staticmethod
    def prompt_step_type() -> str:
        """
        Prompt for step type selection.
        
        Returns:
            Selected step type
        """
        click.echo("\n🔧 What type of step would you like to add?")
        click.echo("1. Action (HTTP request or built-in Moveworks action)")
        click.echo("2. Script (APIthon/Python code)")
        click.echo("3. Switch (conditional logic)")
        
        choice = click.prompt(
            "Enter your choice (1-3)", 
            type=click.Choice(['1', '2', '3'])
        )
        
        type_map = {
            '1': 'action',
            '2': 'script', 
            '3': 'switch'
        }
        
        return type_map[choice]
    
    @staticmethod
    def prompt_action_details() -> Dict[str, Any]:
        """
        Prompt for action step details.
        
        Returns:
            Dictionary with action configuration
        """
        click.echo("\n⚡ Configuring Action Step:")
        
        action_name = click.prompt("Enter action name", type=str)
        output_key = click.prompt("Enter output key (variable name)", type=str)
        
        # Check if it's a built-in action
        is_builtin = action_name.startswith('mw.')
        if is_builtin:
            click.echo(f"✅ Detected built-in Moveworks action: {action_name}")
        
        # Ask for input arguments
        has_input_args = click.confirm("Does this action need input arguments?")
        input_args = {}
        
        if has_input_args:
            click.echo("Enter input arguments (Bender syntax):")
            while True:
                arg_name = click.prompt(
                    "Argument name (or 'done' to finish)", 
                    type=str
                )
                if arg_name.lower() == 'done':
                    break
                
                arg_value = click.prompt(f"Value for '{arg_name}'", type=str)
                input_args[arg_name] = arg_value
        
        # Ask for progress updates
        has_progress = click.confirm("Add progress update messages?")
        progress_updates = None
        
        if has_progress:
            on_pending = click.prompt("Message while pending", type=str)
            on_complete = click.prompt("Message when complete", type=str)
            progress_updates = {
                "on_pending": on_pending,
                "on_complete": on_complete
            }
        
        return {
            "action_name": action_name,
            "output_key": output_key,
            "input_args": input_args if input_args else None,
            "progress_updates": progress_updates
        }
    
    @staticmethod
    def prompt_script_details() -> Dict[str, Any]:
        """
        Prompt for script step details.
        
        Returns:
            Dictionary with script configuration
        """
        click.echo("\n🐍 Configuring Script Step (APIthon):")
        click.echo("Enter your Python code. For multi-line code, end with an empty line.")
        
        code_lines = []
        while True:
            line = click.prompt("Code", default="", show_default=False)
            if not line and code_lines:  # Empty line and we have some code
                break
            if line:  # Non-empty line
                code_lines.append(line)
        
        code = '\n'.join(code_lines)
        output_key = click.prompt("Enter output key (variable name)", type=str)
        
        # Ask for input arguments
        has_input_args = click.confirm("Does this script need input arguments?")
        input_args = {}
        
        if has_input_args:
            click.echo("Enter input arguments (Bender syntax):")
            while True:
                arg_name = click.prompt(
                    "Argument name (or 'done' to finish)", 
                    type=str
                )
                if arg_name.lower() == 'done':
                    break
                
                arg_value = click.prompt(f"Value for '{arg_name}'", type=str)
                input_args[arg_name] = arg_value
        
        return {
            "code": code,
            "output_key": output_key,
            "input_args": input_args if input_args else None
        }
    
    @staticmethod
    def confirm_add_another_step() -> bool:
        """Ask if user wants to add another step."""
        return click.confirm("Would you like to add another step?")
    
    @staticmethod
    def prompt_output_filename(default_name: str) -> str:
        """
        Prompt for output filename.
        
        Args:
            default_name: Default filename suggestion
            
        Returns:
            Chosen filename
        """
        return click.prompt(
            "Enter output filename", 
            default=f"{default_name}.yaml",
            type=str
        )
    
    @staticmethod
    def display_success(filepath: str):
        """Display success message with file path."""
        click.echo(f"\n🎉 Compound Action saved to: {filepath}")
        click.echo("\nYou can now use this YAML file in a Moveworks Action Activity!")
        click.echo("Remember to configure the Input/Output Mappers in your Action Activity.")
    
    @staticmethod
    def display_error(error_msg: str):
        """Display error message."""
        click.echo(f"\n❌ Error: {error_msg}")
    
    @staticmethod
    def display_validation_error(field: str, error_msg: str):
        """Display field validation error."""
        click.echo(f"❌ {field}: {error_msg}")
        click.echo("Please try again.")


# Standalone prompt functions for CLI compatibility
def prompt_for_input_arguments() -> Dict[str, Any]:
    """Prompt for input arguments using Bender syntax."""
    return WizardPrompts.prompt_input_args()


def prompt_for_step_type() -> str:
    """Prompt for step type selection."""
    return WizardPrompts.prompt_step_type()


def prompt_for_action_step() -> Dict[str, Any]:
    """Prompt for action step details."""
    return WizardPrompts.prompt_action_details()


def prompt_for_script_step() -> Dict[str, Any]:
    """Prompt for script step details."""
    return WizardPrompts.prompt_script_details()


def prompt_for_switch_step() -> Dict[str, Any]:
    """Prompt for switch step details."""
    click.echo("\n🔀 Configuring Switch Step:")
    click.echo("Switch steps allow conditional logic based on expressions.")

    cases = []

    while True:
        case_num = len(cases) + 1
        click.echo(f"\n--- Case {case_num} ---")

        condition = click.prompt("Enter condition expression", type=str)

        # For now, just collect the condition - step creation handled in CLI
        cases.append({"condition": condition})

        if not click.confirm("Add another case?"):
            break

    # Default case
    has_default = click.confirm("Add a default case (executed if no conditions match)?")

    return {
        "cases": cases,
        "has_default": has_default
    }


def prompt_for_return_step() -> Dict[str, Any]:
    """Prompt for return step details."""
    click.echo("\n↩️ Configuring Return Step:")
    click.echo("Return steps end the compound action successfully.")

    has_output = click.confirm("Do you want to return specific data?")
    output_mapper = {}

    if has_output:
        click.echo("Enter output mapping (Bender syntax):")
        while True:
            key = click.prompt("Output key (or 'done' to finish)", type=str)
            if key.lower() == 'done':
                break

            value = click.prompt(f"Value for '{key}'", type=str)
            output_mapper[key] = value

    return {
        "output_mapper": output_mapper if output_mapper else None
    }


def prompt_for_raise_step() -> Dict[str, Any]:
    """Prompt for raise step details."""
    click.echo("\n⚠️ Configuring Raise Step:")
    click.echo("Raise steps end the compound action with an error.")

    output_key = click.prompt("Enter output key for error information", type=str)
    message = click.prompt("Enter error message (optional)", default="", show_default=False)

    return {
        "output_key": output_key,
        "message": message if message else None
    }
