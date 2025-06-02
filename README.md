# Moveworks YAML Wizard for Compound Actions

A Python application that provides a user-friendly wizard interface for creating valid Moveworks Compound Action YAML files, specifically designed for use within "Action Activities" in the post-April 2025 Plugin architecture.

## Project Status

**Phase 1: Discovery & Foundational Planning** - COMPLETED ✅
**Phase 2: Core Engine Development (MVP)** - COMPLETED ✅

### Phase 2 Achievements:
- ✅ **Enhanced wizard logic** with 5 step types (action, script, switch, return, raise)
- ✅ **Built-in action catalog** with 7 actions across 5 categories
- ✅ **Advanced validation framework** with comprehensive input validation
- ✅ **Improved user experience** with guidance, examples, and error handling
- ✅ **Comprehensive testing** with 33 total test cases (100% pass rate)
- ✅ **Complex workflow support** with conditional logic and multi-step flows
- ✅ **Smart action discovery** with search and categorization
- ✅ **Production-ready code quality** with full documentation

**Ready for Phase 3: Advanced Features & UI/AI Enhancement**

## Overview

This wizard helps developers create syntactically correct and best-practice-compliant Compound Action YAML files that can be used within Moveworks Action Activities. The tool leverages guided logic to ensure proper structure and adherence to Moveworks standards.

## Key Features

### ✅ Implemented Features (Phase 2)
- **Complete step type support**: Action, Script, Switch, Return, Raise steps
- **Built-in action catalog**: 7 actions across 5 categories with smart discovery
- **Advanced validation**: Comprehensive input validation with real-time feedback
- **Enhanced user experience**: Guided wizard with examples and error handling
- **Complex workflow support**: Multi-step actions with conditional logic
- **Progress updates and delays**: Full support for `progress_updates` and `delay_config`
- **Professional YAML generation**: Moveworks-compliant formatting
- **Interactive CLI**: Enhanced command-line interface with step-by-step guidance

### 🚀 Advanced Features (Phase 3+)
- Full control flow constructs (for loops, parallel execution, try/catch)
- Advanced Bender JSON assistance for input_args
- GUI interface with visual workflow builder
- AI-powered suggestions and templates
- Template library for common patterns

## Architecture

The wizard uses a rule-based engine with Python classes representing each YAML construct. Each class knows how to:
- Accept and validate necessary parameters
- Serialize itself to proper YAML structure
- Maintain relationships with other constructs

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd Moveworks-yaml-wizard

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Interactive Wizard (Enhanced Phase 2 Functionality)
```bash
# Run the enhanced interactive wizard
python main.py

# Specify output file
python main.py --output my_compound_action.yaml

# Get help
python main.py --help
```

**New in Phase 2:**
- Built-in action catalog browsing and search
- Enhanced step creation with 5 step types
- Real-time validation with immediate feedback
- Guided parameter input for built-in actions
- Complex workflow creation with conditional logic

### Programmatic Usage
```python
from moveworks_wizard.models.base import CompoundAction
from moveworks_wizard.models.actions import ActionStep
from moveworks_wizard.serializers import serialize_compound_action

# Create a simple action
action = ActionStep(
    action_name="fetch_user_details",
    output_key="user_info",
    input_args={"user_id": "data.user_id"}
)

# Create compound action
compound_action = CompoundAction(
    name="Get User Details",
    single_step=action
)

# Generate YAML
yaml_content = serialize_compound_action(compound_action)
print(yaml_content)
```

### Examples
```bash
# Generate example YAML files
python examples/test_compound_action.py

# Run Phase 2 feature demonstration
python examples/phase2_demo.py

# Check the examples/generated/ directory for output
```

**Phase 2 Examples:**
- `phase2_enhanced_workflow.yaml` - Complex multi-step workflow with conditionals
- Built-in action catalog demonstration
- Enhanced validation examples
- Multiple step type demonstrations

## Documentation

- [Project Plan](Project_plan.txt) - Detailed project roadmap and phases
- [Compound Action Syntax Reference](docs/compound-action-syntax-reference.md)
- [Moveworks Bender Language Reference](docs/moveworks-bender-language-reference.md)
- [Compound Actions Explained](docs/Moveworks%20Compound%20Actions%20Explained.md)

## Development

### Project Structure
```
Moveworks-yaml-wizard/
├── src/
│   ├── moveworks_wizard/
│   │   ├── __init__.py
│   │   ├── models/          # YAML construct data models
│   │   ├── wizard/          # Wizard logic and CLI
│   │   └── serializers/     # YAML serialization
├── tests/
├── docs/
├── examples/
├── requirements.txt
└── README.md
```

### Running Tests
```bash
pytest tests/
```

## Contributing

This project follows Moveworks best practices for Compound Actions as documented in the provided reference materials.

## License

*To be determined*
