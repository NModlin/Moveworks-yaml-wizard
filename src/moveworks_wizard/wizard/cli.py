"""
Command-line interface for the Moveworks Compound Action Wizard.

This module provides the main CLI entry point and wizard flow logic.
"""

import click
import json
from typing import Optional, List, Dict, Any
from pathlib import Path

from ..models.base import CompoundAction, BaseStep
from ..models.actions import ActionStep, ScriptStep
from ..models.control_flow import SwitchCase
from ..models.terminal import ReturnStep, RaiseStep
from ..models.common import ProgressUpdates, DelayConfig
from ..serializers import serialize_compound_action
from ..catalog import builtin_catalog
from ..templates.template_library import template_library
from ..ai.action_suggester import action_suggester
from ..bender.bender_assistant import bender_assistant
from ..utils.json_analyzer import JSONAnalyzer, VariableSuggestion


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

        # Phase 4: Enhanced start options
        click.echo("How would you like to start?")
        click.echo("  1. Create from scratch")
        click.echo("  2. Use a template")
        click.echo("  3. Get AI suggestions")
        click.echo("  4. Browse examples")

        start_choice = click.prompt("Enter choice (1-4)", type=int, default=1)

        if start_choice == 2:
            return self._start_from_template()
        elif start_choice == 3:
            return self._start_with_ai_suggestions()
        elif start_choice == 4:
            return self._start_from_examples()

        # Default: Create from scratch
        click.echo("\n📝 Creating Compound Action from scratch...")

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

        # Offer JSON analysis option
        if click.confirm("Do you have JSON test results from an HTTP connector to analyze?"):
            json_suggestions = self._analyze_json_input()
            if json_suggestions:
                return self._select_from_json_suggestions(json_suggestions)

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

    def _analyze_json_input(self) -> Optional[List[VariableSuggestion]]:
        """Analyze JSON input from HTTP connector test results."""
        click.echo("\n🔍 JSON Analysis for Variable Suggestions")
        click.echo("This will analyze your HTTP connector test results to suggest variables.")
        click.echo()

        # Get JSON input method
        input_method = click.prompt(
            "How would you like to provide the JSON?\n"
            "1. Paste JSON directly\n"
            "2. Load from file\n"
            "Choose (1-2)",
            type=click.Choice(['1', '2'])
        )

        json_data = None
        source_name = "http_response"

        if input_method == '1':
            click.echo("\nPaste your JSON data (press Ctrl+D when finished):")
            json_lines = []
            try:
                while True:
                    line = input()
                    json_lines.append(line)
            except EOFError:
                json_data = '\n'.join(json_lines)

            source_name = click.prompt("Enter a name for this data source", default="http_response")

        elif input_method == '2':
            file_path = click.prompt("Enter path to JSON file", type=click.Path(exists=True))
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_data = f.read()
                source_name = Path(file_path).stem
            except Exception as e:
                click.echo(f"❌ Error reading file: {e}")
                return None

        if not json_data or not json_data.strip():
            click.echo("❌ No JSON data provided")
            return None

        # Analyze the JSON
        try:
            analyzer = JSONAnalyzer()
            suggestions = analyzer.analyze_json(json_data, source_name)

            if not suggestions:
                click.echo("❌ No variable suggestions found in the JSON data")
                return None

            click.echo(f"\n✅ Found {len(suggestions)} variable suggestions!")

            # Display top suggestions
            display_text = analyzer.format_suggestions_for_display(suggestions, max_suggestions=10)
            click.echo(display_text)

            return suggestions

        except json.JSONDecodeError as e:
            click.echo(f"❌ Invalid JSON data: {e}")
            return None
        except Exception as e:
            click.echo(f"❌ Error analyzing JSON: {e}")
            return None

    def _select_from_json_suggestions(self, suggestions: List[VariableSuggestion]) -> Dict[str, Any]:
        """Allow user to select variables from JSON analysis suggestions."""
        click.echo("\n📋 Select Variables for Input Arguments")
        click.echo("Choose which variables you want to use as input arguments:")
        click.echo()

        input_args = {}

        while True:
            # Show available suggestions
            click.echo("Available suggestions:")
            for i, suggestion in enumerate(suggestions[:15], 1):
                click.echo(f"{i:2d}. {suggestion.path} ({suggestion.data_type}) - {suggestion.description}")

            if len(suggestions) > 15:
                click.echo(f"    ... and {len(suggestions) - 15} more")

            click.echo("\nOptions:")
            click.echo("  • Enter number to select a suggestion")
            click.echo("  • Enter 'more' to see all suggestions")
            click.echo("  • Enter 'done' to finish")
            click.echo("  • Enter 'manual' to add arguments manually")

            choice = click.prompt("Your choice", type=str)

            if choice.lower() == 'done':
                break
            elif choice.lower() == 'manual':
                # Fall back to manual input
                manual_args = self._add_manual_input_arguments()
                input_args.update(manual_args)
                break
            elif choice.lower() == 'more':
                # Show all suggestions
                analyzer = JSONAnalyzer()
                analyzer.suggestions = suggestions
                display_text = analyzer.format_suggestions_for_display(suggestions, max_suggestions=50)
                click.echo(f"\n{display_text}")
                continue

            # Try to parse as number
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(suggestions):
                    suggestion = suggestions[choice_num - 1]

                    # Suggest argument name based on path
                    suggested_name = suggestion.path.split('.')[-1].lower()
                    arg_name = click.prompt(f"Argument name for '{suggestion.path}'", default=suggested_name)

                    # Use the bender expression as the value
                    input_args[arg_name] = suggestion.bender_expression

                    click.echo(f"✅ Added: {arg_name} = {suggestion.bender_expression}")
                    click.echo(f"   Description: {suggestion.description}")
                    click.echo(f"   Example usage: {suggestion.example_usage}")
                    click.echo()

                    # Remove from suggestions to avoid duplicates
                    suggestions.pop(choice_num - 1)

                else:
                    click.echo("❌ Invalid selection number")
            except ValueError:
                click.echo("❌ Invalid input. Enter a number, 'more', 'manual', or 'done'")

        if input_args:
            click.echo(f"\n✅ Added {len(input_args)} input arguments from JSON analysis")

        return input_args

    def _add_manual_input_arguments(self) -> Dict[str, Any]:
        """Add input arguments manually (fallback method)."""
        click.echo("\n📝 Manual Input Arguments")
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

        # Offer JSON analysis for step arguments too
        if click.confirm("Use JSON analysis to help with variable selection?"):
            json_suggestions = self._analyze_json_input()
            if json_suggestions:
                return self._select_from_json_suggestions(json_suggestions)

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

    def _start_from_template(self) -> CompoundAction:
        """Start wizard using a template."""
        click.echo("\n📚 Template Library")
        click.echo("=" * 40)

        # Show available categories
        categories = template_library.get_all_categories()
        click.echo("Available template categories:")
        for i, category in enumerate(categories, 1):
            templates_in_category = template_library.get_templates_by_category(category)
            click.echo(f"  {i}. {category} ({len(templates_in_category)} templates)")

        category_choice = click.prompt("Select category (1-{})".format(len(categories)), type=int)
        if 1 <= category_choice <= len(categories):
            selected_category = categories[category_choice - 1]
            templates = template_library.get_templates_by_category(selected_category)

            click.echo(f"\nTemplates in {selected_category}:")
            for i, template in enumerate(templates, 1):
                click.echo(f"  {i}. {template.name}")
                click.echo(f"     {template.description}")
                click.echo(f"     Use case: {template.use_case}")
                click.echo()

            template_choice = click.prompt("Select template (1-{})".format(len(templates)), type=int)
            if 1 <= template_choice <= len(templates):
                selected_template = templates[template_choice - 1]

                click.echo(f"\n✅ Using template: {selected_template.name}")
                click.echo("Customization notes:")
                for note in selected_template.customization_notes:
                    click.echo(f"  • {note}")

                # Copy the template compound action
                self.compound_action = selected_template.compound_action

                # Allow user to customize
                if click.confirm("\nWould you like to customize this template?"):
                    return self._customize_template(selected_template)

                return self.compound_action

        # Fallback to scratch if invalid selection
        click.echo("Invalid selection. Starting from scratch...")
        return self._start_from_scratch()

    def _start_with_ai_suggestions(self) -> CompoundAction:
        """Start wizard with AI suggestions."""
        click.echo("\n🤖 AI Assistant")
        click.echo("=" * 40)

        description = click.prompt("Describe what you want your Compound Action to do", type=str)

        click.echo("\n🔍 Analyzing your description...")
        suggestions = action_suggester.suggest_actions(description, max_suggestions=5)

        if not suggestions:
            click.echo("❌ No suggestions found. Starting from scratch...")
            return self._start_from_scratch()

        click.echo(f"\n💡 Found {len(suggestions)} suggestions:")
        for i, suggestion in enumerate(suggestions, 1):
            click.echo(f"\n{i}. {suggestion.title}")
            click.echo(f"   {suggestion.description}")
            click.echo(f"   Confidence: {suggestion.confidence:.1%}")
            click.echo(f"   Reasoning: {suggestion.reasoning}")

        choice = click.prompt(f"Select suggestion (1-{len(suggestions)}) or 0 to start from scratch",
                             type=int, default=0)

        if choice == 0:
            return self._start_from_scratch()
        elif 1 <= choice <= len(suggestions):
            selected_suggestion = suggestions[choice - 1]
            return self._apply_ai_suggestion(selected_suggestion, description)

        return self._start_from_scratch()

    def _start_from_examples(self) -> CompoundAction:
        """Start wizard by browsing examples."""
        click.echo("\n📖 Example Gallery")
        click.echo("=" * 40)

        # Show some example patterns
        examples = [
            ("User Onboarding", "Automated new employee setup with access provisioning"),
            ("Incident Response", "Security incident handling with notifications"),
            ("Access Request", "Manager approval workflow for system access"),
            ("Ticket Escalation", "Automatic escalation based on SLA thresholds"),
            ("Data Validation", "Input validation with error reporting")
        ]

        click.echo("Common workflow examples:")
        for i, (name, desc) in enumerate(examples, 1):
            click.echo(f"  {i}. {name}")
            click.echo(f"     {desc}")

        choice = click.prompt(f"Select example (1-{len(examples)}) or 0 to start from scratch",
                             type=int, default=0)

        if choice == 0:
            return self._start_from_scratch()
        elif 1 <= choice <= len(examples):
            example_name = examples[choice - 1][0].lower().replace(" ", "_")
            # Map to template names
            template_map = {
                "user_onboarding": "user_onboarding",
                "incident_response": "incident_response",
                "access_request": "access_request",
                "ticket_escalation": "ticket_escalation",
                "data_validation": "data_validation"
            }

            template_name = template_map.get(example_name)
            if template_name:
                template = template_library.get_template(template_name)
                if template:
                    click.echo(f"\n✅ Loading example: {template.name}")
                    self.compound_action = template.compound_action
                    return self.compound_action

        return self._start_from_scratch()

    def _start_from_scratch(self) -> CompoundAction:
        """Start wizard from scratch (original flow)."""
        click.echo("\n📝 Creating from scratch...")

        name = click.prompt("Enter a name for your Compound Action", type=str)
        description = click.prompt("Enter a description (optional)", default="", show_default=False)

        self.compound_action = CompoundAction(
            name=name if name else None,
            description=description if description else None
        )

        click.echo(f"\n✅ Created Compound Action: {name}")

        # Continue with original flow
        if click.confirm("\nDo you want to add input arguments?"):
            input_args = self._add_input_arguments()
            if input_args:
                self.compound_action.input_args = input_args

        self._add_steps()

        return self.compound_action

    def _customize_template(self, template) -> CompoundAction:
        """Allow user to customize a template."""
        click.echo(f"\n🔧 Customizing template: {template.name}")

        # Allow name and description changes
        if click.confirm("Change the name?"):
            new_name = click.prompt("Enter new name", default=self.compound_action.name)
            self.compound_action.name = new_name

        if click.confirm("Change the description?"):
            new_desc = click.prompt("Enter new description", default=self.compound_action.description or "")
            self.compound_action.description = new_desc if new_desc else None

        # Allow input args modification
        if click.confirm("Modify input arguments?"):
            click.echo("Current input arguments:")
            for key, value in (self.compound_action.input_args or {}).items():
                click.echo(f"  {key}: {value}")

            additional_args = self._add_input_arguments()
            if additional_args:
                if not self.compound_action.input_args:
                    self.compound_action.input_args = {}
                self.compound_action.input_args.update(additional_args)

        # Allow step modification
        if click.confirm("Add additional steps?"):
            self._add_steps()

        return self.compound_action

    def _apply_ai_suggestion(self, suggestion, original_description: str) -> CompoundAction:
        """Apply an AI suggestion."""
        click.echo(f"\n🎯 Applying suggestion: {suggestion.title}")

        if suggestion.suggestion_type.value == "template":
            template = suggestion.details.get("template")
            if template:
                self.compound_action = template.compound_action
                click.echo(f"✅ Applied template: {template.name}")

                if click.confirm("Customize this template?"):
                    return self._customize_template(template)

                return self.compound_action

        elif suggestion.suggestion_type.value == "builtin_action":
            action = suggestion.details.get("action")
            if action:
                # Create a simple compound action with this builtin action
                name = click.prompt("Enter name for your Compound Action",
                                  default=f"Action using {action.name}")

                self.compound_action = CompoundAction(
                    name=name,
                    description=f"Compound Action based on AI suggestion: {suggestion.title}"
                )

                # Add the suggested action as a step
                click.echo(f"Adding {action.name} as the main step...")
                action_step = self._create_builtin_action_step(action)
                self.compound_action.single_step = action_step

                return self.compound_action

        # Fallback to scratch
        click.echo("Could not apply suggestion directly. Starting from scratch...")
        return self._start_from_scratch()

    def _create_builtin_action_step(self, action):
        """Create an action step from a builtin action."""
        output_key = click.prompt("Enter output key for this action",
                                default=action.name.split('.')[-1] + "_result")

        # Prompt for required parameters
        input_args = {}
        for param in action.parameters:
            if param.required:
                value = click.prompt(f"Enter value for {param.name} ({param.description})",
                                   default=param.example)
                input_args[param.name] = value

        return ActionStep(
            action_name=action.name,
            output_key=output_key,
            input_args=input_args if input_args else None
        )

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


@click.group()
def cli():
    """Moveworks Compound Action Wizard - Create valid Compound Action YAML files."""
    pass


@cli.command()
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--interactive/--no-interactive', default=True, help='Run in interactive mode')
def wizard(output: Optional[str], interactive: bool):
    """
    Moveworks Compound Action Wizard - Create valid Compound Action YAML files.
    
    This wizard guides you through creating Compound Actions for use in
    Moveworks Action Activities (post-April 2025 architecture).
    """
    try:
        wizard = CompoundActionWizard()
        
        if interactive:
            # Run interactive wizard
            wizard_instance = CompoundActionWizard()
            compound_action = wizard_instance.start_wizard()

            # Save to file
            output_path = Path(output) if output else None
            saved_path = wizard_instance.save_to_file(output_path)

            click.echo(f"\n🎉 Compound Action saved to: {saved_path}")
            click.echo("\nYou can now use this YAML file in a Moveworks Action Activity!")

        else:
            click.echo("Non-interactive mode not yet implemented")

    except KeyboardInterrupt:
        click.echo("\n\n👋 Wizard cancelled by user")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}")
        raise click.Abort()


@cli.command()
def gui():
    """Launch the graphical user interface for the wizard."""
    try:
        from ..gui.main_window import MoveworksWizardGUI
        click.echo("🖥️  Launching Moveworks Wizard GUI...")
        app = MoveworksWizardGUI()
        app.run()
    except ImportError:
        click.echo("❌ GUI dependencies not available. Install tkinter to use the GUI.")
    except Exception as e:
        click.echo(f"❌ Error launching GUI: {e}")
        raise click.Abort()


@cli.command()
def templates():
    """Browse and display available templates."""
    click.echo("📚 Available Templates")
    click.echo("=" * 50)

    categories = template_library.get_all_categories()
    for category in categories:
        click.echo(f"\n{category}:")
        templates = template_library.get_templates_by_category(category)
        for template in templates:
            click.echo(f"  • {template.name}")
            click.echo(f"    {template.description}")
            click.echo(f"    Use case: {template.use_case}")
            click.echo()


@cli.command()
@click.argument('description')
def suggest(description: str):
    """Get AI suggestions for a workflow description."""
    click.echo(f"🤖 Analyzing: {description}")
    click.echo("=" * 50)

    suggestions = action_suggester.suggest_actions(description, max_suggestions=5)

    if not suggestions:
        click.echo("❌ No suggestions found for your description.")
        return

    click.echo(f"💡 Found {len(suggestions)} suggestions:")
    for i, suggestion in enumerate(suggestions, 1):
        click.echo(f"\n{i}. {suggestion.title}")
        click.echo(f"   Type: {suggestion.suggestion_type.value}")
        click.echo(f"   Description: {suggestion.description}")
        click.echo(f"   Confidence: {suggestion.confidence:.1%}")
        click.echo(f"   Reasoning: {suggestion.reasoning}")


@cli.command()
@click.argument('expression')
def validate_bender(expression: str):
    """Validate a Bender expression."""
    click.echo(f"🔍 Validating Bender expression: {expression}")
    click.echo("=" * 50)

    result = bender_assistant.validate_expression(expression)

    if result['is_valid']:
        click.echo("✅ Expression is valid!")
    else:
        click.echo("❌ Expression has errors:")
        for error in result['errors']:
            click.echo(f"  • {error}")

    if result['warnings']:
        click.echo("\n⚠️  Warnings:")
        for warning in result['warnings']:
            click.echo(f"  • {warning}")

    if result['functions_used']:
        click.echo(f"\n🔧 Functions used: {', '.join(result['functions_used'])}")


@cli.command()
@click.option('--file', '-f', 'json_file', type=click.Path(exists=True), help='JSON file to analyze')
@click.option('--source', '-s', default='http_response', help='Name for the data source')
@click.option('--output', '-o', type=click.Path(), help='Output file for suggestions')
@click.option('--yaml-example', '-y', is_flag=True, help='Generate comprehensive YAML example for array data extraction')
def analyze_json(json_file, source, output, yaml_example):
    """Analyze JSON from HTTP connector test results to suggest variables."""
    click.echo("🔍 JSON Analysis for Variable Suggestions")
    click.echo("This analyzes HTTP connector test results to suggest variables for Compound Actions.")
    click.echo()

    json_data = None

    if json_file:
        # Load from file
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = f.read()
            click.echo(f"📁 Loaded JSON from: {json_file}")
        except Exception as e:
            click.echo(f"❌ Error reading file: {e}")
            return
    else:
        # Get JSON input interactively
        click.echo("Paste your JSON data (press Ctrl+D when finished):")
        json_lines = []
        try:
            while True:
                line = input()
                json_lines.append(line)
        except EOFError:
            json_data = '\n'.join(json_lines)

        if not json_data.strip():
            click.echo("❌ No JSON data provided")
            return

    # Analyze the JSON
    try:
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json_data, source)

        if not suggestions:
            click.echo("❌ No variable suggestions found in the JSON data")
            return

        click.echo(f"\n✅ Found {len(suggestions)} variable suggestions!")

        # Display suggestions
        display_text = analyzer.format_suggestions_for_display(suggestions)
        click.echo(display_text)

        # Generate comprehensive YAML example if requested
        if yaml_example:
            click.echo("\n" + "="*60)
            click.echo("📋 COMPREHENSIVE YAML EXAMPLE FOR ARRAY DATA EXTRACTION:")
            click.echo("="*60)

            yaml_content = analyzer.generate_comprehensive_yaml_example(source)
            click.echo(yaml_content)

            # Optionally save YAML example to file
            if output:
                yaml_output_path = Path(output).with_suffix('.yaml')
                with open(yaml_output_path, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                click.echo(f"\n💾 YAML example saved to: {yaml_output_path}")

        # Save to file if requested
        if output:
            analyzer.export_suggestions_to_json(Path(output))
            click.echo(f"\n💾 Suggestions saved to: {output}")

        # Show usage tips
        click.echo("\n💡 Usage Tips:")
        click.echo("• Use these suggestions when creating Compound Action input arguments")
        click.echo("• The 'Bender' column shows the exact expression to use")
        click.echo("• The 'Example' column shows how to use the variable in steps")
        click.echo("• Use --yaml-example flag to generate complete YAML for array data extraction")
        click.echo("• Run 'moveworks-wizard wizard' to create a Compound Action with these variables")

    except json.JSONDecodeError as e:
        click.echo(f"❌ Invalid JSON data: {e}")
    except Exception as e:
        click.echo(f"❌ Error analyzing JSON: {e}")


if __name__ == '__main__':
    cli()
