# Moveworks YAML Wizard - API Documentation

## Table of Contents
1. [Core Models](#core-models)
2. [Wizard Interface](#wizard-interface)
3. [Serialization](#serialization)
4. [Built-in Actions](#built-in-actions)
5. [Templates](#templates)
6. [AI Features](#ai-features)
7. [Validation](#validation)

## Core Models

### CompoundAction

The root model representing a complete Moveworks Compound Action.

```python
from moveworks_wizard.models.base import CompoundAction

compound_action = CompoundAction(
    name="My Workflow",
    description="Description of the workflow",
    input_args={"user_id": "data.user_id"},
    steps=[...]  # List of steps
)
```

**Attributes:**
- `name` (Optional[str]): Human-readable name
- `description` (Optional[str]): Description of the workflow
- `input_args` (Optional[Dict[str, Any]]): Input arguments using Bender syntax
- `steps` (Optional[List[BaseStep]]): List of workflow steps
- `single_step` (Optional[BaseStep]): Single step (alternative to steps list)

**Methods:**
- `add_step(step: BaseStep)`: Add a step to the workflow
- `to_yaml_dict() -> Dict[str, Any]`: Convert to YAML-serializable dictionary

### ActionStep

Represents an action step in a Compound Action.

```python
from moveworks_wizard.models.actions import ActionStep

action = ActionStep(
    action_name="mw.user.create",
    output_key="new_user",
    input_args={"email": "data.user_email"},
    progress_updates={
        "starting": "Creating user...",
        "completed": "User created successfully"
    }
)
```

**Attributes:**
- `action_name` (str): Unique identifier for the action
- `output_key` (str): Variable name to store the result
- `input_args` (Optional[Dict[str, Any]]): Input arguments
- `delay_config` (Optional[DelayConfig]): Delay configuration
- `progress_updates` (Optional[ProgressUpdates]): Progress messages

### ScriptStep

Represents a script step using APIthon.

```python
from moveworks_wizard.models.actions import ScriptStep

script = ScriptStep(
    output_key="processed_data",
    code="""
# Process the data
result = {
    'processed': True,
    'timestamp': str(datetime.now())
}
""",
    progress_updates={"starting": "Processing data..."}
)
```

**Attributes:**
- `output_key` (str): Variable name to store the result
- `code` (str): Python code to execute
- `progress_updates` (Optional[ProgressUpdates]): Progress messages

### SwitchStep

Represents conditional logic with switch/case statements.

```python
from moveworks_wizard.models.control_flow import SwitchStep, SwitchCase

switch = SwitchStep(
    switch_on="data.user_type",
    cases=[
        SwitchCase(
            case="employee",
            steps=[ActionStep(action_name="mw.user.create_employee", output_key="result")]
        ),
        SwitchCase(
            case="contractor", 
            steps=[ActionStep(action_name="mw.user.create_contractor", output_key="result")]
        )
    ],
    default_steps=[
        RaiseStep(error_code="INVALID_TYPE", message="Invalid user type")
    ]
)
```

### Terminal Steps

**ReturnStep**: Return a value from the workflow
```python
from moveworks_wizard.models.terminal import ReturnStep

return_step = ReturnStep(value="processed_data")
```

**RaiseStep**: Raise an error
```python
from moveworks_wizard.models.terminal import RaiseStep

raise_step = RaiseStep(
    error_code="VALIDATION_ERROR",
    message="Invalid input: {{data.field_name}}"
)
```

## Wizard Interface

### CompoundActionWizard

Main wizard class for interactive creation.

```python
from moveworks_wizard.wizard.cli import CompoundActionWizard

wizard = CompoundActionWizard()

# Create steps interactively
action_step = wizard.create_action_step(
    action_name="mw.user.create",
    output_key="new_user",
    input_args={"email": "data.user_email"}
)

# Create compound action
compound_action = wizard.create_compound_action(
    name="User Creation",
    steps=[action_step]
)

# Save to file
wizard.save_compound_action(compound_action, "user_creation.yaml")
```

**Methods:**
- `create_action_step()`: Create an action step interactively
- `create_script_step()`: Create a script step interactively
- `create_switch_step()`: Create a switch step interactively
- `create_compound_action()`: Create a compound action
- `save_compound_action()`: Save to YAML file

### CLI Commands

Access wizard functionality through CLI:

```python
from moveworks_wizard.wizard.cli import cli

# Programmatically invoke CLI commands
import click
from click.testing import CliRunner

runner = CliRunner()
result = runner.invoke(cli, ['wizard', '--output', 'test.yaml'])
```

## Serialization

### YAML Serialization

Convert models to YAML format:

```python
from moveworks_wizard.serializers import serialize_compound_action

yaml_content = serialize_compound_action(compound_action)
print(yaml_content)
```

**Functions:**
- `serialize_compound_action(compound_action: CompoundAction) -> str`: Convert to YAML string
- `serialize_step(step: BaseStep) -> Dict[str, Any]`: Convert step to dictionary

### Custom Serialization

Extend serialization for custom step types:

```python
from moveworks_wizard.serializers.yaml_serializer import YAMLSerializer

class CustomSerializer(YAMLSerializer):
    def serialize_custom_step(self, step: CustomStep) -> Dict[str, Any]:
        return {
            "custom": {
                "type": step.step_type,
                "config": step.config
            }
        }
```

## Built-in Actions

### BuiltinActionCatalog

Access the catalog of built-in Moveworks actions:

```python
from moveworks_wizard.catalog.builtin_actions import builtin_catalog

# Get all actions
all_actions = builtin_catalog.get_all_actions()

# Get actions by category
user_actions = builtin_catalog.get_actions_by_category("User Management")

# Search actions
search_results = builtin_catalog.search_actions("create user")

# Get specific action
action = builtin_catalog.get_builtin_action("mw.user.create")
```

### BuiltinAction Model

```python
from moveworks_wizard.catalog.builtin_actions import BuiltinAction, ActionParameter

action = BuiltinAction(
    name="mw.user.create",
    description="Create a new user account",
    category="User Management",
    parameters=[
        ActionParameter(
            name="email",
            type="string",
            required=True,
            description="User's email address",
            example="user@company.com"
        )
    ]
)
```

## Templates

### TemplateLibrary

Access pre-built workflow templates:

```python
from moveworks_wizard.templates.template_library import template_library

# Get all templates
templates = template_library.get_all_templates()

# Get specific template
template = template_library.get_template("user_management")

# Search templates
results = template_library.search_templates("user")

# Generate compound action from template
compound_action = template.generate_compound_action({
    "user_email": "test@company.com",
    "department": "Engineering"
})
```

### CompoundActionTemplate

```python
from moveworks_wizard.templates.template_library import CompoundActionTemplate

template = CompoundActionTemplate(
    name="custom_template",
    description="Custom workflow template",
    category="Custom",
    parameters=["user_email", "department"],
    template_data={
        "input_args": {
            "user_email": "data.user_email",
            "department": "data.department"
        },
        "steps": [...]
    }
)
```

## AI Features

### ActionSuggester

Get AI-powered action suggestions:

```python
from moveworks_wizard.ai.action_suggester import action_suggester

# Get suggestions
suggestions = action_suggester.suggest_actions(
    "create a user and send welcome email"
)

for suggestion in suggestions:
    print(f"{suggestion.action_name} (confidence: {suggestion.confidence}%)")
```

### BenderAssistant

Validate and get help with Bender expressions:

```python
from moveworks_wizard.bender.bender_assistant import bender_assistant

# Validate expression
is_valid = bender_assistant.validate_expression("RENDER('Hello {{name}}', data)")

# Get function details
render_func = bender_assistant.get_function_details("RENDER")

# Get common patterns
patterns = bender_assistant.get_common_patterns()
```

## Validation

### WizardValidators

Comprehensive validation utilities:

```python
from moveworks_wizard.wizard.validators import WizardValidators

validators = WizardValidators()

# Validate compound action name
is_valid = validators.validate_compound_action_name("My Workflow")

# Validate output key
is_valid = validators.validate_output_key("user_result")

# Validate Bender expression
is_valid = validators.validate_bender_expression("data.user_email")

# Validate Python code
is_valid = validators.validate_python_code("result = {'status': 'success'}")
```

**Validation Methods:**
- `validate_compound_action_name(name: str) -> bool`
- `validate_output_key(key: str) -> bool`
- `validate_action_name(name: str) -> bool`
- `validate_bender_expression(expression: str) -> bool`
- `validate_python_code(code: str) -> bool`
- `validate_input_args(args: Dict[str, Any]) -> bool`
- `validate_progress_updates(updates: Dict[str, str]) -> bool`

### Custom Validation

Extend validation for custom requirements:

```python
class CustomValidators(WizardValidators):
    def validate_custom_field(self, value: str) -> bool:
        # Custom validation logic
        return len(value) > 0 and value.startswith("custom_")
```

## Error Handling

### Common Exceptions

```python
from moveworks_wizard.exceptions import (
    ValidationError,
    SerializationError,
    WizardError
)

try:
    compound_action = CompoundAction(name="")  # Invalid name
except ValidationError as e:
    print(f"Validation failed: {e}")

try:
    yaml_content = serialize_compound_action(invalid_action)
except SerializationError as e:
    print(f"Serialization failed: {e}")
```

## Extension Points

### Custom Step Types

Create custom step types by extending BaseStep:

```python
from moveworks_wizard.models.base import BaseStep

class CustomStep(BaseStep):
    step_type: str = "custom"
    custom_field: str
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        return {
            "custom": {
                "type": self.step_type,
                "field": self.custom_field
            }
        }
```

### Custom Actions

Register custom actions with the catalog:

```python
from moveworks_wizard.catalog.builtin_actions import BuiltinAction

custom_action = BuiltinAction(
    name="custom.action.name",
    description="Custom action description",
    category="Custom",
    parameters=[]
)

builtin_catalog.register_action(custom_action)
```

---

For usage examples, see the [User Guide](User_Guide.md) and [examples/](../examples/) directory.
