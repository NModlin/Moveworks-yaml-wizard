# Moveworks YAML Wizard for Compound Actions

A Python application that provides a user-friendly wizard interface for creating valid Moveworks Compound Action YAML files, specifically designed for use within "Action Activities" in the post-April 2025 Plugin architecture.

## Project Status

**Phase 1: Discovery & Foundational Planning** - COMPLETED ✅
**Phase 2: Core Engine Development (MVP)** - COMPLETED ✅
**Phase 3: MVP Testing & Refinement** - COMPLETED ✅
**Phase 4: Advanced Features & UI/AI Enhancement** - COMPLETED ✅
**Phase 5: Continuous Testing, Documentation & Deployment** - COMPLETED ✅

### Latest Achievements (Phase 5):
- ✅ **Comprehensive testing suite** with 102 tests (101 passing, 1 skipped)
- ✅ **Production packaging** with setup.py and pyproject.toml
- ✅ **Enhanced documentation** with user guides and API documentation
- ✅ **CLI entry points** for easy installation and usage (3 command aliases)
- ✅ **Action Activity integration** guidance and validation
- ✅ **Performance testing** and stress testing capabilities
- ✅ **Real-world workflow examples** and deployment scenarios
- ✅ **Production deployment** ready for PyPI distribution
- ✅ **JSON analysis for HTTP connectors** to suggest variables from test results
- ✅ **Fully functional GUI** with working buttons and JSON analysis integration

### Complete Feature Set:
- ✅ **Enhanced wizard logic** with 5 step types (action, script, switch, return, raise)
- ✅ **Built-in action catalog** with 15+ actions across 8 categories
- ✅ **Template library** with 8 pre-built workflow templates
- ✅ **AI-powered suggestions** with natural language processing
- ✅ **Bender assistance** for data mapping expressions
- ✅ **GUI interface** with tkinter-based visual editor
- ✅ **Advanced validation framework** with comprehensive input validation
- ✅ **Production-ready deployment** with proper packaging and distribution

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

### Option 1: Install from Source (Development)
```bash
# Clone the repository
git clone <repository-url>
cd Moveworks-yaml-wizard

# Install in development mode with all dependencies
pip install -e ".[all]"

# Or install just the core package
pip install -e .
```

### Option 2: Install from Package (Production)
```bash
# Install the package (when published to PyPI)
pip install moveworks-yaml-wizard

# Install with GUI support
pip install "moveworks-yaml-wizard[gui]"

# Install with development tools
pip install "moveworks-yaml-wizard[dev]"
```

### Option 3: Manual Installation
```bash
# Clone and install dependencies manually
git clone <repository-url>
cd Moveworks-yaml-wizard
pip install -r requirements.txt

# Run directly
python main.py
```

## Usage

### Command Line Interface (All Phases)

After installation, you can use any of these commands:

```bash
# Main wizard command
moveworks-wizard

# Short alias
mw-wizard

# Alternative command
compound-action-wizard
```

### Interactive Wizard
```bash
# Run the interactive wizard
moveworks-wizard wizard

# Specify output file
moveworks-wizard wizard --output my_compound_action.yaml

# Get help
moveworks-wizard --help
```

### GUI Interface (Fully Functional!)
```bash
# Launch the graphical interface with all working buttons
moveworks-wizard gui

# Features:
# • JSON analysis integration
# • Working input argument management
# • Functional step creation/editing
# • Real-time YAML preview
# • Template library access
# • AI suggestions integration
```

### Template Management (Phase 4+)
```bash
# List available templates
moveworks-wizard templates list

# Use a specific template
moveworks-wizard templates use user_management

# Search templates
moveworks-wizard templates search "user"
```

### AI-Powered Suggestions (Phase 4+)
```bash
# Get action suggestions
moveworks-wizard suggest "create a user and send notification"

# Validate Bender expressions
moveworks-wizard validate-bender "RENDER('Hello {{name}}', data)"
```

### JSON Analysis for HTTP Connectors (New!)
```bash
# Analyze JSON from HTTP connector test results
moveworks-wizard analyze-json --file response.json --source user_api

# Interactive JSON analysis
moveworks-wizard analyze-json
# Then paste your JSON data

# Use in wizard for variable suggestions
moveworks-wizard wizard
# Choose "yes" when asked about JSON analysis
```

### Legacy Usage (Development)
```bash
# Run directly from source
python main.py

# Specify output file
python main.py --output my_compound_action.yaml
```

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
