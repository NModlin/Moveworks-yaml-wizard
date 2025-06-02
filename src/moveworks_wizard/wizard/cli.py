"""
Command-line interface for the Moveworks Compound Action Wizard.

This module provides the main CLI entry point and wizard flow logic.
"""

import click
from typing import Optional, List, Dict, Any
from pathlib import Path

from ..models.base import CompoundAction, BaseStep
from ..models.actions import ActionStep, ScriptStep
from ..models.control_flow import SwitchCase
from ..models.terminal import ReturnStep, RaiseStep
from ..models.common import ProgressUpdates, DelayConfig
from ..serializers import serialize_compound_action
from ..catalog import builtin_catalog


class CompoundActionWizard:
    """
    Main wizard class for creating Compound Actions.

    Provides an interactive command-line interface for guiding users
    through the creation of valid Compound Action YAML files.
    """

    def __init__(self):
        """Initialize the wizard."""
        self.compound_action: Optional[CompoundAction] = None
        self.steps: List[BaseStep] = []

    def start_wizard(self) -> CompoundAction:
        """
        Start the interactive wizard flow.

        Returns:
            The created CompoundAction model
        """
        click.echo("🧙 Welcome to the Moveworks Compound Action Wizard!")
        click.echo("This wizard will help you create valid Compound Action YAML for Action Activities.")
        click.echo("=" * 80)
        click.echo()

        # Phase 1: Basic information
        name = click.prompt("Enter a name for your Compound Action", type=str)
        description = click.prompt("Enter a description (optional)", default="", show_default=False)

        # Create the compound action
        self.compound_action = CompoundAction(
            name=name if name else None,
            description=description if description else None
        )

        click.echo(f"\n✅ Created Compound Action: {name}")

        # Phase 2: Input arguments
        if click.confirm("\nDo you want to add input arguments?"):
            input_args = self._add_input_arguments()
            if input_args:
                self.compound_action.input_args = input_args

        # Phase 3: Steps
        self._add_steps()

        return self.compound_action
    
    def _add_input_arguments(self) -> Dict[str, Any]:
        """Add input arguments to the compound action."""
        click.echo("\n📝 Adding input arguments...")
        click.echo("Input arguments use Moveworks Data Mapping (Bender) syntax.")
        click.echo("Examples:")
        click.echo("  • data.user_id")
        click.echo("  • meta_info.requestor.email")
        click.echo("  • data.ticket_id")
        click.echo()

        input_args = {}

        while True:
            arg_name = click.prompt("Enter argument name (or 'done' to finish)", type=str)
            if arg_name.lower() == 'done':
                break

            # Validate argument name
            if not arg_name.replace('_', '').replace('-', '').isalnum():
                click.echo("❌ Invalid argument name. Use alphanumeric characters, underscores, or hyphens.")
                continue

            arg_value = click.prompt(f"Enter value for '{arg_name}' (Bender syntax)", type=str)

            # Basic validation for Bender syntax
            if not (arg_value.startswith('data.') or arg_value.startswith('meta_info.') or
                   arg_value.startswith('constants.') or arg_value.startswith('"')):
                click.echo("⚠️  Warning: Value should typically start with 'data.', 'meta_info.', 'constants.', or be a quoted string")

            input_args[arg_name] = arg_value
            click.echo(f"✅ Added: {arg_name} = {arg_value}")

        if input_args:
            click.echo(f"\n✅ Added {len(input_args)} input arguments")

        return input_args

    def _add_steps(self):
        """Add steps to the compound action."""
        click.echo("\n🔧 Adding steps...")
        click.echo("You can create multiple types of steps:")
        click.echo("  • Action steps (HTTP requests, built-in Moveworks actions)")
        click.echo("  • Script steps (APIthon/Python code)")
        click.echo("  • Switch steps (conditional logic)")
        click.echo("  • Return/Raise steps (exit compound action)")
        click.echo()

        steps = []
        step_count = 0

        while True:
            step_count += 1
            click.echo(f"\n--- Step {step_count} ---")

            # Ask for step type
            step_type = self._prompt_step_type()

            if step_type == 'done':
                break

            # Create the appropriate step
            step = self._create_step(step_type)
            if step:
                steps.append(step)
                click.echo(f"✅ Added {step_type} step")

                # Show current step summary
                self._show_step_summary(step, step_count)
            else:
                step_count -= 1  # Don't count failed steps

        # Set steps on compound action
        if len(steps) == 1:
            self.compound_action.single_step = steps[0]
        elif len(steps) > 1:
            self.compound_action.steps = steps
        else:
            click.echo("❌ No steps added. A compound action must have at least one step.")
            # Recursively call to add steps
            self._add_steps()

    def _prompt_step_type(self) -> str:
        """Prompt user to select step type."""
        click.echo("Select step type:")
        click.echo("  1. Action step (HTTP request or built-in Moveworks action)")
        click.echo("  2. Script step (APIthon/Python code)")
        click.echo("  3. Switch step (conditional logic)")
        click.echo("  4. Return step (exit with success)")
        click.echo("  5. Raise step (exit with error)")
        click.echo("  6. Done (finish adding steps)")

        choice = click.prompt("Enter choice (1-6)", type=int)

        type_map = {
            1: 'action',
            2: 'script',
            3: 'switch',
            4: 'return',
            5: 'raise',
            6: 'done'
        }

        return type_map.get(choice, 'action')

    def _create_step(self, step_type: str) -> Optional[BaseStep]:
        """Create a step based on the specified type."""
        try:
            if step_type == 'action':
                return self._create_action_step()
            elif step_type == 'script':
                return self._create_script_step()
            elif step_type == 'switch':
                return self._create_switch_step()
            elif step_type == 'return':
                return self._create_return_step()
            elif step_type == 'raise':
                return self._create_raise_step()
            else:
                click.echo(f"❌ Unknown step type: {step_type}")
                return None
        except Exception as e:
            click.echo(f"❌ Error creating {step_type} step: {e}")
            return None

    def _create_action_step(self) -> ActionStep:
        """Create an action step with user input."""
        from ..models.actions import ActionStep

        click.echo("\n📋 Creating action step...")

        # Ask if they want to browse built-in actions
        if click.confirm("Would you like to browse built-in Moveworks actions?"):
            action_name = self._select_builtin_action()
        else:
            action_name = click.prompt("Enter action name", type=str)

        output_key = click.prompt("Enter output key", type=str)

        # Check if it's a built-in action and provide parameter suggestions
        builtin_action = builtin_catalog.get_action(action_name)
        if builtin_action:
            click.echo(f"\n✅ Using built-in action: {builtin_action.description}")
            click.echo("Suggested parameters:")
            for param in builtin_action.parameters:
                required_text = "REQUIRED" if param.required else "optional"
                click.echo(f"  • {param.name} ({param.type}, {required_text}): {param.description}")
                if param.example:
                    click.echo(f"    Example: {param.example}")

        # Input arguments
        input_args = {}
        if click.confirm("Does this action need input arguments?"):
            if builtin_action:
                input_args = self._prompt_builtin_action_args(builtin_action)
            else:
                input_args = self._prompt_input_args_for_step()

        # Progress updates
        progress_updates = None
        if click.confirm("Add progress update messages?"):
            progress_updates = self._prompt_progress_updates()

        # Delay configuration
        delay_config = None
        if click.confirm("Add delay before this action?"):
            delay_config = self._prompt_delay_config()

        return ActionStep(
            action_name=action_name,
            output_key=output_key,
            input_args=input_args if input_args else None,
            progress_updates=progress_updates,
            delay_config=delay_config
        )

    def _create_script_step(self) -> ScriptStep:
        """Create a script step with user input."""
        from ..models.actions import ScriptStep

        click.echo("\n🐍 Creating script step...")
        click.echo("Enter your APIthon (Python) code. Use 'END' on a new line to finish.")

        code_lines = []
        while True:
            line = click.prompt("", prompt_suffix="", show_default=False)
            if line.strip() == 'END':
                break
            code_lines.append(line)

        code = '\n'.join(code_lines)
        output_key = click.prompt("Enter output key", type=str)

        # Input arguments
        input_args = {}
        if click.confirm("Does this script need input arguments?"):
            input_args = self._prompt_input_args_for_step()

        return ScriptStep(
            code=code,
            output_key=output_key,
            input_args=input_args if input_args else None
        )

    def _create_switch_step(self) -> Optional[BaseStep]:
        """Create a switch step with user input."""
        from ..models.control_flow import SwitchStep, SwitchCase

        click.echo("\n🔀 Creating switch step...")
        click.echo("Switch steps allow conditional logic based on expressions.")

        cases = []

        while True:
            case_num = len(cases) + 1
            click.echo(f"\n--- Case {case_num} ---")

            condition = click.prompt("Enter condition expression", type=str)

            # For simplicity, create a single action step for each case
            click.echo("Create the step to execute when this condition is true:")
            case_step = self._create_action_step()

            cases.append(SwitchCase(
                condition=condition,
                steps=[case_step]
            ))

            if not click.confirm("Add another case?"):
                break

        # Default case
        default_steps = None
        if click.confirm("Add a default case (executed if no conditions match)?"):
            click.echo("Create the default step:")
            default_step = self._create_action_step()
            default_steps = [default_step]

        return SwitchStep(
            cases=cases,
            default=default_steps
        )

    def _create_return_step(self) -> ReturnStep:
        """Create a return step with user input."""
        from ..models.terminal import ReturnStep

        click.echo("\n↩️ Creating return step...")
        click.echo("Return steps end the compound action successfully.")

        output_mapper = {}
        if click.confirm("Do you want to return specific data?"):
            output_mapper = self._prompt_input_args_for_step("output mapping")

        return ReturnStep(
            output_mapper=output_mapper if output_mapper else None
        )

    def _create_raise_step(self) -> RaiseStep:
        """Create a raise step with user input."""
        from ..models.terminal import RaiseStep

        click.echo("\n⚠️ Creating raise step...")
        click.echo("Raise steps end the compound action with an error.")

        output_key = click.prompt("Enter output key for error information", type=str)
        message = click.prompt("Enter error message (optional)", default="", show_default=False)

        return RaiseStep(
            output_key=output_key,
            message=message if message else None
        )

    def _prompt_input_args_for_step(self, context: str = "input arguments") -> Dict[str, Any]:
        """Prompt for input arguments for a specific step."""
        click.echo(f"\nEnter {context}:")
        input_args = {}

        while True:
            arg_name = click.prompt("Argument name (or 'done' to finish)", type=str)
            if arg_name.lower() == 'done':
                break

            arg_value = click.prompt(f"Value for '{arg_name}'", type=str)
            input_args[arg_name] = arg_value
            click.echo(f"✅ Added: {arg_name} = {arg_value}")

        return input_args

    def _prompt_progress_updates(self) -> ProgressUpdates:
        """Prompt for progress update configuration."""
        on_pending = click.prompt("Message while action is pending", type=str)
        on_complete = click.prompt("Message when action completes", type=str)

        return ProgressUpdates(
            on_pending=on_pending,
            on_complete=on_complete
        )

    def _prompt_delay_config(self) -> DelayConfig:
        """Prompt for delay configuration."""
        click.echo("Enter delay amount:")
        click.echo("  1. Seconds")
        click.echo("  2. Minutes")
        click.echo("  3. Hours")

        unit_choice = click.prompt("Select time unit (1-3)", type=int)
        amount = click.prompt("Enter delay amount", type=int)

        if unit_choice == 1:
            return DelayConfig(seconds=amount)
        elif unit_choice == 2:
            return DelayConfig(minutes=amount)
        else:
            return DelayConfig(hours=amount)

    def _show_step_summary(self, step: BaseStep, step_number: int):
        """Show a summary of the created step."""
        click.echo(f"\n📋 Step {step_number} Summary:")
        click.echo(f"   Type: {step.get_step_type()}")

        if hasattr(step, 'action_name'):
            click.echo(f"   Action: {step.action_name}")
        if hasattr(step, 'output_key'):
            click.echo(f"   Output: {step.output_key}")
        if hasattr(step, 'code'):
            lines = step.code.split('\n')
            preview = lines[0][:50] + "..." if len(lines[0]) > 50 else lines[0]
            click.echo(f"   Code: {preview}")

    def _select_builtin_action(self) -> str:
        """Allow user to select from built-in actions."""
        click.echo("\n📚 Built-in Moveworks Actions")

        # Show categories
        categories = builtin_catalog.get_all_categories()
        click.echo("Available categories:")
        for i, category in enumerate(categories, 1):
            click.echo(f"  {i}. {category}")

        # Let user select category or search
        click.echo(f"  {len(categories) + 1}. Search actions")
        click.echo(f"  {len(categories) + 2}. Show all actions")

        choice = click.prompt(f"Select category (1-{len(categories) + 2})", type=int)

        if choice <= len(categories):
            # Show actions in selected category
            category = categories[choice - 1]
            actions = builtin_catalog.get_actions_by_category(category)
            return self._select_from_actions(actions, f"{category} Actions")
        elif choice == len(categories) + 1:
            # Search actions
            query = click.prompt("Enter search term", type=str)
            actions = builtin_catalog.search_actions(query)
            if not actions:
                click.echo("No actions found matching your search.")
                return self._select_builtin_action()  # Try again
            return self._select_from_actions(actions, f"Search Results for '{query}'")
        else:
            # Show all actions
            actions = builtin_catalog.get_all_actions()
            return self._select_from_actions(actions, "All Built-in Actions")

    def _select_from_actions(self, actions: List, title: str) -> str:
        """Allow user to select from a list of actions."""
        click.echo(f"\n{title}:")

        for i, action in enumerate(actions, 1):
            click.echo(f"  {i}. {action.name}")
            click.echo(f"     {action.description}")

        if len(actions) > 10:
            click.echo(f"\n... and {len(actions) - 10} more actions")
            click.echo("Consider using search to narrow down results.")

        choice = click.prompt(f"Select action (1-{len(actions)})", type=int)

        if 1 <= choice <= len(actions):
            selected_action = actions[choice - 1]
            click.echo(f"\n✅ Selected: {selected_action.name}")
            return selected_action.name
        else:
            click.echo("Invalid choice. Please try again.")
            return self._select_from_actions(actions, title)

    def _prompt_builtin_action_args(self, builtin_action) -> Dict[str, Any]:
        """Prompt for arguments specific to a built-in action."""
        click.echo(f"\nConfiguring parameters for {builtin_action.name}:")
        input_args = {}

        # Go through each parameter
        for param in builtin_action.parameters:
            required_text = " (REQUIRED)" if param.required else " (optional)"
            prompt_text = f"{param.name}{required_text}"

            if param.required:
                value = click.prompt(prompt_text, type=str)
            else:
                value = click.prompt(prompt_text, default="", show_default=False)
                if not value:
                    continue  # Skip optional parameters that are empty

            input_args[param.name] = value

            # Show example if available
            if param.example:
                click.echo(f"   💡 Example: {param.example}")

        return input_args

    def save_to_file(self, output_path: Optional[Path] = None) -> Path:
        """
        Save the compound action to a YAML file.
        
        Args:
            output_path: Optional path to save the file
            
        Returns:
            Path where the file was saved
        """
        if not self.compound_action:
            raise ValueError("No compound action to save")
        
        if not output_path:
            filename = self.compound_action.name or "compound_action"
            filename = filename.replace(" ", "_").lower()
            output_path = Path(f"{filename}.yaml")
        
        # Serialize to YAML
        yaml_content = serialize_compound_action(self.compound_action)
        
        # Write to file
        output_path.write_text(yaml_content, encoding='utf-8')
        
        return output_path


@click.command()
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--interactive/--no-interactive', default=True, help='Run in interactive mode')
def main(output: Optional[str], interactive: bool):
    """
    Moveworks Compound Action Wizard - Create valid Compound Action YAML files.
    
    This wizard guides you through creating Compound Actions for use in
    Moveworks Action Activities (post-April 2025 architecture).
    """
    try:
        wizard = CompoundActionWizard()
        
        if interactive:
            # Run interactive wizard
            compound_action = wizard.start_wizard()
            
            # Save to file
            output_path = Path(output) if output else None
            saved_path = wizard.save_to_file(output_path)
            
            click.echo(f"\n🎉 Compound Action saved to: {saved_path}")
            click.echo("\nYou can now use this YAML file in a Moveworks Action Activity!")
            
        else:
            click.echo("Non-interactive mode not yet implemented in Phase 1")
            
    except KeyboardInterrupt:
        click.echo("\n\n👋 Wizard cancelled by user")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}")
        raise click.Abort()


if __name__ == '__main__':
    main()
