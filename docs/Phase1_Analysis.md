# Phase 1: Discovery & Foundational Planning - Analysis Report

## Overview

This document summarizes the analysis and foundational work completed in Phase 1 of the Moveworks YAML Wizard project.

## YAML Schema Analysis

### Core Compound Action Structure

Based on the documentation analysis, a Moveworks Compound Action has the following structure:

```yaml
# Optional: Input arguments using Bender syntax
input_args:
  arg_name: "bender_expression"

# Either single step (for simple actions)
action:
  action_name: "action_identifier"
  output_key: "variable_name"
  # ... other fields

# OR multiple steps (for complex workflows)
steps:
  - action:
      action_name: "action1"
      output_key: "output1"
  - script:
      code: "python_code"
      output_key: "output2"
  # ... more steps
```

### Identified YAML Constructs

#### 1. Action Steps (`action`)
- **Purpose**: Execute HTTP requests or built-in Moveworks actions
- **Required Fields**: `action_name`, `output_key`
- **Optional Fields**: `input_args`, `delay_config`, `progress_updates`
- **Built-in Actions**: Prefixed with `mw.` (e.g., `mw.create_ticket`)

#### 2. Script Steps (`script`)
- **Purpose**: Execute APIthon (Python) code for custom logic
- **Required Fields**: `code`, `output_key`
- **Optional Fields**: `input_args`
- **Multi-line Support**: Uses YAML literal block scalar (`|`) for multi-line code

#### 3. Control Flow Constructs

##### Switch Statements (`switch`)
- **Purpose**: Conditional execution based on boolean expressions
- **Structure**: `cases` (list of condition/steps pairs) + optional `default`
- **Conditions**: Use Bender syntax for boolean expressions

##### For Loops (`for`)
- **Purpose**: Iterate over collections
- **Required Fields**: `each`, `index`, `in`, `output_key`, `steps`
- **Use Case**: Process lists of items

##### Parallel Execution (`parallel`)
- **Purpose**: Concurrent execution of independent tasks
- **Two Modes**: 
  - `branches`: List of independent step sequences
  - `for`: Parallel iteration over collections

##### Try/Catch (`try_catch`)
- **Purpose**: Error handling and recovery
- **Structure**: `try` block with `catch` block
- **Optional**: `on_status_code` for specific error handling

#### 4. Terminal Steps

##### Return (`return`)
- **Purpose**: Graceful exit with structured output
- **Uses**: `output_mapper` with Bender syntax
- **Note**: Avoid reserved keywords like "result"

##### Raise (`raise`)
- **Purpose**: Error exit with error information
- **Required**: `output_key`
- **Optional**: `message`

### Data Mapping (Bender) Integration

Compound Actions heavily use Moveworks Data Mapping Language (Bender) for:
- Input argument values (`data.user_id`, `meta_info.requestor.email`)
- Conditional expressions in switch statements
- Output mapping in return statements
- Dynamic values throughout the workflow

## MVP Feature Definition

### Core MVP Features (Phase 2 Target)

1. **Basic Compound Action Creation**
   - Support for `input_args` definition
   - Single step and multi-step workflows

2. **Essential Step Types**
   - Action steps (HTTP and built-in)
   - Script steps (APIthon)
   - Basic switch statements

3. **Core Fields Support**
   - `progress_updates` for user feedback
   - `delay_config` for timing control
   - Basic input argument handling

4. **YAML Generation**
   - Proper formatting and indentation
   - Multi-line string handling for scripts
   - Validation of required fields

5. **CLI Interface**
   - Interactive wizard flow
   - File output generation
   - Basic validation and error handling

### Advanced Features (Future Phases)

1. **Complete Control Flow**
   - For loops and parallel execution
   - Try/catch error handling
   - Return and raise statements

2. **Enhanced Bender Support**
   - Advanced data mapping assistance
   - Template suggestions for common patterns
   - Validation of Bender expressions

3. **Built-in Action Catalog**
   - Complete list of available `mw.*` actions
   - Parameter suggestions and validation
   - Documentation integration

4. **GUI Interface**
   - Visual workflow builder
   - Drag-and-drop step creation
   - Real-time YAML preview

## Technical Architecture

### Data Model Design

The architecture uses Pydantic models for type safety and validation:

```
BaseStep (Abstract)
├── ActionStep
├── ScriptStep  
├── SwitchStep
├── ForStep
├── ParallelStep
├── TryCatchStep
├── ReturnStep
└── RaiseStep

CompoundAction (Root)
├── input_args: Dict[str, Any]
├── steps: List[BaseStep] 
└── single_step: BaseStep
```

### Key Design Decisions

1. **Pydantic Models**: Chosen for validation, type safety, and serialization
2. **Abstract Base Classes**: Ensure consistent interface across step types
3. **Flexible Step Structure**: Support both single-step and multi-step actions
4. **YAML Serialization**: Custom serializer for Moveworks-specific formatting
5. **CLI Framework**: Click for robust command-line interface

### Project Structure

```
Moveworks-yaml-wizard/
├── src/moveworks_wizard/
│   ├── models/           # Pydantic data models
│   │   ├── base.py       # Base classes
│   │   ├── actions.py    # Action and script steps
│   │   ├── control_flow.py # Control flow constructs
│   │   ├── terminal.py   # Return and raise steps
│   │   └── common.py     # Shared utilities
│   ├── serializers/      # YAML serialization
│   └── wizard/           # CLI and wizard logic
├── tests/                # Unit tests
├── docs/                 # Documentation
└── examples/             # Example YAML files
```

## Key Challenges Identified

### 1. YAML Formatting Complexity
- Multi-line strings require literal block scalars (`|`)
- Proper indentation is critical
- DSL expressions need careful escaping

### 2. Bender Syntax Integration
- Complex data mapping expressions
- Validation of Bender syntax
- Context-aware suggestions

### 3. Action Activity Integration
- Compound Actions are components within Action Activities
- Input/Output mapper coordination
- Data flow understanding (Plugin → Action Activity → Compound Action)

### 4. APIthon Limitations
- Restricted Python subset
- Specific syntax requirements
- Error handling constraints

## Next Steps (Phase 2)

1. **Complete Model Implementation**
   - Finish all step type models
   - Add comprehensive validation
   - Implement remaining common utilities

2. **YAML Serialization Enhancement**
   - Handle multi-line strings properly
   - Add Moveworks-specific formatting
   - Implement validation

3. **Wizard Logic Development**
   - Interactive step creation
   - Input validation and suggestions
   - Error handling and recovery

4. **Testing Infrastructure**
   - Unit tests for all models
   - Integration tests for wizard flow
   - YAML validation tests

5. **Documentation**
   - User guide for wizard
   - Developer documentation
   - Example compound actions

## Conclusion

Phase 1 has successfully established:
- ✅ Comprehensive understanding of Compound Action YAML structure
- ✅ Clear MVP feature definition
- ✅ Solid technical architecture foundation
- ✅ Complete project structure
- ✅ Core data models implementation

The project is well-positioned to move into Phase 2 (Core Engine Development) with a clear roadmap and solid foundation.
