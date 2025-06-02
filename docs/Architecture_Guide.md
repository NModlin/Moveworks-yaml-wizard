# Moveworks YAML Wizard - Architecture Guide

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Module Structure](#module-structure)
4. [Data Flow](#data-flow)
5. [Design Patterns](#design-patterns)
6. [Extension Points](#extension-points)
7. [Performance Considerations](#performance-considerations)

## Overview

The Moveworks YAML Wizard is designed as a modular, extensible system for creating Moveworks Compound Action YAML files. The architecture follows clean separation of concerns with distinct layers for models, business logic, user interface, and serialization.

### Core Principles

1. **Separation of Concerns**: Clear boundaries between data models, business logic, and presentation
2. **Extensibility**: Plugin architecture for custom step types, actions, and templates
3. **Validation**: Comprehensive validation at multiple layers
4. **Type Safety**: Strong typing with Pydantic models
5. **Testability**: Modular design enabling comprehensive testing

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer                     │
├─────────────────┬─────────────────┬─────────────────────────┤
│   CLI Interface │  GUI Interface  │    API Interface        │
│   (click-based) │   (tkinter)     │   (programmatic)        │
└─────────────────┴─────────────────┴─────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                      │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Wizard Engine  │   Validation    │    AI Features          │
│                 │   Framework     │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                     Service Layer                          │
├─────────────────┬─────────────────┬─────────────────────────┤
│   Catalog       │   Templates     │    Serialization        │
│   Management    │   Library       │    Engine               │
└─────────────────┴─────────────────┴─────────────────────────┘
                           │
┌─────────────────────────────────────────────────────────────┐
│                     Data Model Layer                       │
├─────────────────┬─────────────────┬─────────────────────────┤
│  Core Models    │  Action Models  │   Control Flow Models   │
│  (Pydantic)     │                 │                         │
└─────────────────┴─────────────────┴─────────────────────────┘
```

## Module Structure

### src/moveworks_wizard/

```
moveworks_wizard/
├── __init__.py                 # Package initialization
├── models/                     # Data models (Pydantic)
│   ├── __init__.py
│   ├── base.py                # Base classes and CompoundAction
│   ├── actions.py             # Action and Script steps
│   ├── control_flow.py        # Switch, For, Parallel, TryCatch
│   ├── terminal.py            # Return and Raise steps
│   └── common.py              # Common data structures
├── wizard/                     # Wizard logic and CLI
│   ├── __init__.py
│   ├── cli.py                 # Click-based CLI interface
│   ├── prompts.py             # User interaction prompts
│   └── validators.py          # Input validation
├── serializers/                # YAML serialization
│   ├── __init__.py
│   └── yaml_serializer.py     # YAML generation logic
├── catalog/                    # Built-in action catalog
│   ├── __init__.py
│   └── builtin_actions.py     # Action definitions and search
├── templates/                  # Template library
│   ├── __init__.py
│   └── template_library.py    # Pre-built workflow templates
├── ai/                        # AI-powered features
│   ├── __init__.py
│   └── action_suggester.py    # Natural language suggestions
├── bender/                    # Bender language support
│   ├── __init__.py
│   └── bender_assistant.py    # Expression validation and help
└── gui/                       # Graphical interface
    ├── __init__.py
    └── main_window.py         # Tkinter-based GUI
```

### Key Components

#### 1. Models Layer (`models/`)

**Purpose**: Define data structures using Pydantic for type safety and validation.

**Key Classes**:
- `CompoundAction`: Root container for the entire workflow
- `BaseStep`: Abstract base for all step types
- `ActionStep`: Represents action execution
- `ScriptStep`: Represents Python script execution
- `SwitchStep`: Represents conditional logic
- `ReturnStep`/`RaiseStep`: Terminal steps

**Design Pattern**: Data Transfer Objects (DTOs) with built-in validation

#### 2. Wizard Layer (`wizard/`)

**Purpose**: Handle user interaction and workflow creation logic.

**Key Components**:
- `CompoundActionWizard`: Main wizard orchestrator
- `WizardValidators`: Input validation utilities
- `PromptManager`: User interaction prompts

**Design Pattern**: Command Pattern for user actions

#### 3. Serialization Layer (`serializers/`)

**Purpose**: Convert data models to YAML format.

**Key Features**:
- Maintains Moveworks YAML compliance
- Handles special formatting (multi-line strings, DSL escaping)
- Preserves Bender expressions

**Design Pattern**: Visitor Pattern for model traversal

#### 4. Service Layer (`catalog/`, `templates/`, `ai/`, `bender/`)

**Purpose**: Provide specialized services for the wizard.

**Services**:
- **Catalog**: Built-in action discovery and search
- **Templates**: Pre-built workflow patterns
- **AI**: Natural language processing for suggestions
- **Bender**: Data mapping language assistance

**Design Pattern**: Service Locator Pattern

## Data Flow

### 1. Interactive Wizard Flow

```
User Input → Validation → Model Creation → Serialization → YAML Output
     ↓           ↓             ↓              ↓             ↓
   CLI/GUI → Validators → Pydantic Models → YAML Serializer → File
```

### 2. Template-Based Flow

```
Template Selection → Parameter Input → Model Generation → Serialization
        ↓                 ↓               ↓                ↓
   Template Library → User Values → CompoundAction → YAML Output
```

### 3. AI-Assisted Flow

```
Natural Language → NLP Processing → Action Suggestions → User Selection → Model Creation
       ↓                ↓                ↓                   ↓              ↓
   User Input → Action Suggester → Ranked Actions → User Choice → Wizard Flow
```

## Design Patterns

### 1. Builder Pattern

Used in wizard for step-by-step construction:

```python
class CompoundActionBuilder:
    def __init__(self):
        self._compound_action = CompoundAction()
    
    def with_name(self, name: str):
        self._compound_action.name = name
        return self
    
    def add_step(self, step: BaseStep):
        self._compound_action.add_step(step)
        return self
    
    def build(self) -> CompoundAction:
        return self._compound_action
```

### 2. Strategy Pattern

Used for different validation strategies:

```python
class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, value: Any) -> bool:
        pass

class BenderExpressionValidator(ValidationStrategy):
    def validate(self, expression: str) -> bool:
        # Bender-specific validation logic
        pass

class PythonCodeValidator(ValidationStrategy):
    def validate(self, code: str) -> bool:
        # Python syntax validation logic
        pass
```

### 3. Factory Pattern

Used for step creation:

```python
class StepFactory:
    @staticmethod
    def create_step(step_type: str, **kwargs) -> BaseStep:
        if step_type == "action":
            return ActionStep(**kwargs)
        elif step_type == "script":
            return ScriptStep(**kwargs)
        elif step_type == "switch":
            return SwitchStep(**kwargs)
        # ... other step types
```

### 4. Observer Pattern

Used for validation feedback:

```python
class ValidationObserver(ABC):
    @abstractmethod
    def on_validation_result(self, field: str, is_valid: bool, message: str):
        pass

class CLIValidationObserver(ValidationObserver):
    def on_validation_result(self, field: str, is_valid: bool, message: str):
        if not is_valid:
            click.echo(f"❌ {field}: {message}", err=True)
        else:
            click.echo(f"✅ {field}: Valid")
```

## Extension Points

### 1. Custom Step Types

Extend the system with new step types:

```python
# 1. Define the model
class CustomStep(BaseStep):
    step_type: str = "custom"
    custom_field: str
    
    def to_yaml_dict(self) -> Dict[str, Any]:
        return {"custom": {"field": self.custom_field}}

# 2. Register with factory
StepFactory.register_step_type("custom", CustomStep)

# 3. Add wizard support
class CustomStepWizard:
    def create_custom_step(self) -> CustomStep:
        # Interactive creation logic
        pass
```

### 2. Custom Actions

Add new built-in actions:

```python
custom_action = BuiltinAction(
    name="custom.integration.sync",
    description="Sync data with custom system",
    category="Integration",
    parameters=[
        ActionParameter(name="endpoint", type="string", required=True),
        ActionParameter(name="data", type="object", required=True)
    ]
)

builtin_catalog.register_action(custom_action)
```

### 3. Custom Templates

Create new workflow templates:

```python
custom_template = CompoundActionTemplate(
    name="custom_workflow",
    description="Custom business workflow",
    category="Business Process",
    parameters=["entity_id", "action_type"],
    template_data={
        "input_args": {
            "entity_id": "data.entity_id",
            "action_type": "data.action_type"
        },
        "steps": [
            # Template step definitions
        ]
    }
)

template_library.register_template(custom_template)
```

### 4. Custom Validators

Add domain-specific validation:

```python
class BusinessRuleValidator(ValidationStrategy):
    def validate(self, compound_action: CompoundAction) -> bool:
        # Business-specific validation logic
        return self._check_business_rules(compound_action)

# Register with validator framework
WizardValidators.register_validator("business_rules", BusinessRuleValidator())
```

## Performance Considerations

### 1. Lazy Loading

- Templates and actions are loaded on-demand
- Large catalogs use pagination
- GUI components initialize progressively

### 2. Caching

```python
from functools import lru_cache

class BuiltinActionCatalog:
    @lru_cache(maxsize=128)
    def search_actions(self, query: str) -> List[BuiltinAction]:
        # Cached search results
        pass
```

### 3. Async Operations

For future GUI enhancements:

```python
import asyncio

class AsyncWizard:
    async def validate_bender_expression(self, expression: str) -> bool:
        # Non-blocking validation
        return await self._async_validate(expression)
```

### 4. Memory Management

- Use generators for large datasets
- Implement proper cleanup in GUI
- Avoid circular references in models

### 5. Serialization Optimization

```python
class OptimizedYAMLSerializer:
    def __init__(self):
        self._yaml_dumper = yaml.SafeDumper
        self._yaml_dumper.add_representer(str, self._str_representer)
    
    def _str_representer(self, dumper, data):
        # Optimized string representation
        if '\n' in data:
            return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
        return dumper.represent_scalar('tag:yaml.org,2002:str', data)
```

## Testing Architecture

### 1. Unit Tests

- Model validation tests
- Serialization tests
- Individual component tests

### 2. Integration Tests

- End-to-end wizard flows
- Template generation tests
- CLI command tests

### 3. Performance Tests

- Large workflow generation
- Memory usage validation
- Response time benchmarks

### 4. Compliance Tests

- YAML format validation
- Moveworks standard compliance
- Action Activity integration tests

---

This architecture provides a solid foundation for the Moveworks YAML Wizard while maintaining flexibility for future enhancements and customizations.
