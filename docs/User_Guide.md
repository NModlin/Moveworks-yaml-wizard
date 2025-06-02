# Moveworks YAML Wizard - User Guide

## Table of Contents
1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [Basic Usage](#basic-usage)
4. [Advanced Features](#advanced-features)
5. [Action Activity Integration](#action-activity-integration)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

## Getting Started

The Moveworks YAML Wizard is designed to help you create valid Compound Action YAML files for use within Moveworks Action Activities in the post-April 2025 Plugin architecture.

### What are Compound Actions?

Compound Actions are workflow-focused components that orchestrate sequences of actions within Action Activities. They are designed for:
- **Determined tasks** with fixed sequences
- **Asynchronous execution** with progress updates
- **Data flow management** between steps
- **Error handling** and conditional logic

### When to Use Compound Actions

Use Compound Actions when you need to:
- Execute multiple related actions in sequence
- Handle complex conditional logic
- Provide progress updates for long-running tasks
- Manage data flow between different systems
- Implement error handling and recovery

## Installation

### Quick Start (Recommended)
```bash
pip install moveworks-yaml-wizard
```

### Development Installation
```bash
git clone <repository-url>
cd Moveworks-yaml-wizard
pip install -e ".[all]"
```

### Verify Installation
```bash
moveworks-wizard --help
```

## Basic Usage

### 1. Interactive Wizard

The interactive wizard guides you through creating a Compound Action step by step:

```bash
moveworks-wizard wizard
```

**Example Session:**
```
Welcome to the Moveworks Compound Action Wizard!

Enter compound action name: User Onboarding
Enter description: Complete user onboarding workflow

Configure input arguments? (y/n): y
Input argument name: user_email
Input argument value (Bender expression): data.user_email

Add a step:
1. Action Step
2. Script Step  
3. Switch Step
4. Return Step
5. Raise Step

Choose step type (1-5): 1

Action name: mw.user.create
Output key: new_user
```

### 2. Template-Based Creation

Use pre-built templates for common scenarios:

```bash
# List available templates
moveworks-wizard templates list

# Use a template
moveworks-wizard templates use user_management
```

**Available Templates:**
- `user_management` - User creation and management
- `notification_workflow` - Multi-channel notifications
- `approval_process` - Approval workflows with escalation
- `data_sync` - Data synchronization between systems
- `incident_response` - Automated incident handling
- `onboarding` - Employee onboarding process
- `security_check` - Security validation workflow
- `integration_flow` - Third-party system integration

### 3. AI-Powered Suggestions

Get intelligent action suggestions based on natural language:

```bash
moveworks-wizard suggest "create a user and send welcome email"
```

**Example Output:**
```
Suggested Actions:
1. mw.user.create (confidence: 95%)
2. mw.notification.send (confidence: 90%)
3. mw.email.send (confidence: 85%)
```

## Advanced Features

### 1. GUI Interface

Launch the graphical interface for visual workflow building:

```bash
moveworks-wizard gui
```

**GUI Features:**
- Visual workflow designer
- Drag-and-drop step creation
- Real-time YAML preview
- Built-in validation
- Template browser

### 2. Bender Expression Validation

Validate Moveworks Data Mapping Language expressions:

```bash
moveworks-wizard validate-bender "RENDER('Hello {{name}}', data)"
```

**Common Bender Functions:**
- `RENDER()` - Template rendering
- `MAP()` - Data transformation
- `CONCAT()` - String concatenation
- `FILTER()` - Data filtering
- `EXTRACT()` - Data extraction
- `IF()` - Conditional logic

### 3. Built-in Action Catalog

Browse and search the comprehensive action catalog:

```bash
# In interactive mode
moveworks-wizard wizard
> Browse built-in actions
> Search: "user"
```

**Action Categories:**
- User Management (mw.user.*)
- Communication (mw.notification.*, mw.email.*)
- Security (mw.security.*, mw.access.*)
- Integration (mw.api.*, mw.webhook.*)
- Database (mw.database.*, mw.query.*)
- File Operations (mw.file.*, mw.storage.*)
- Workflow (mw.approval.*, mw.escalation.*)
- Analytics (mw.analytics.*, mw.reporting.*)

## Action Activity Integration

### Understanding the Data Flow

```
Plugin Slots → Action Activity Input Mapper → Compound Action input_args → 
Compound Action Steps → Action Activity Output Mapper → Plugin Context
```

### Input Arguments Best Practices

Always use proper data references in your input_args:

```yaml
input_args:
  user_email: "data.user_email"        # From Action Activity data
  department: "data.department"        # From Action Activity data
  context: "meta_info.request_context" # From meta information
```

### Progress Updates for Async Execution

Include progress updates for user feedback:

```yaml
action:
  action_name: "mw.user.create"
  output_key: "new_user"
  progress_updates:
    starting: "Creating new user account..."
    in_progress: "Setting up user {{data.user_email}}..."
    completed: "User account created successfully"
```

### Output Mapping Considerations

Structure your outputs for easy mapping in Action Activities:

```yaml
# Good: Structured output
script:
  output_key: "user_summary"
  code: |
    result = {
        'user_id': new_user.get('id'),
        'status': 'created',
        'next_steps': ['send_welcome_email', 'assign_manager']
    }

# Avoid: Unstructured output
script:
  output_key: "raw_response"
  code: |
    result = new_user  # Raw API response
```

## Troubleshooting

### Common Issues

**1. Invalid Bender Expression**
```
Error: Invalid Bender expression: "data.user_email"
Solution: Use proper syntax: "data.user_email" (with quotes)
```

**2. Missing Required Fields**
```
Error: action_name is required for ActionStep
Solution: Ensure all required fields are provided
```

**3. YAML Parsing Error**
```
Error: YAML parsing failed
Solution: Check for proper indentation and special characters
```

### Validation Errors

The wizard provides real-time validation with helpful error messages:

```
❌ Invalid action name: "invalid-action"
✅ Suggestion: Use format "mw.category.action" (e.g., "mw.user.create")

❌ Invalid output key: "output-key"  
✅ Suggestion: Use snake_case format (e.g., "output_key")
```

### Debug Mode

Enable debug mode for detailed error information:

```bash
moveworks-wizard wizard --debug
```

## Best Practices

### 1. Naming Conventions

**Compound Actions:**
- Use descriptive names: "User Onboarding Workflow"
- Include the business purpose
- Keep under 50 characters

**Output Keys:**
- Use snake_case: `user_details`, `notification_result`
- Be descriptive: `created_user` not `result`
- Avoid generic names: `data`, `response`, `output`

**Action Names:**
- Follow Moveworks convention: `mw.category.action`
- Use existing built-in actions when possible
- Be specific: `mw.user.create` not `mw.user.manage`

### 2. Data Flow Design

**Input Arguments:**
```yaml
# Good: Clear data sources
input_args:
  user_email: "data.user_email"
  manager_id: "data.manager_id"
  department: "data.department"

# Avoid: Unclear references
input_args:
  user_data: "data"
  info: "meta_info"
```

**Step Dependencies:**
```yaml
# Good: Clear dependencies
steps:
  - action:
      action_name: "mw.user.create"
      output_key: "new_user"
  - action:
      action_name: "mw.notification.send"
      input_args:
        user_id: "new_user.id"  # Clear reference
```

### 3. Error Handling

**Use Switch Statements for Conditional Logic:**
```yaml
switch:
  switch_on: "data.user_type"
  cases:
    - case: "employee"
      steps:
        - action:
            action_name: "mw.user.create_employee"
    - case: "contractor"
      steps:
        - action:
            action_name: "mw.user.create_contractor"
  default:
    - raise:
        error_code: "INVALID_USER_TYPE"
        message: "Unsupported user type: {{data.user_type}}"
```

**Include Progress Updates:**
```yaml
action:
  progress_updates:
    starting: "Starting {{action_name}}..."
    in_progress: "Processing {{data.identifier}}..."
    completed: "{{action_name}} completed successfully"
    failed: "{{action_name}} failed: {{error.message}}"
```

### 4. Testing Your Compound Actions

**Validate Generated YAML:**
```bash
# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('your_action.yaml'))"

# Validate with wizard
moveworks-wizard validate your_action.yaml
```

**Test Data Flow:**
- Verify all `data.*` references are available in Action Activity
- Check output structure matches expected format
- Test error scenarios and edge cases

### 5. Documentation

**Include Comments in YAML:**
```yaml
# User Onboarding Compound Action
# Purpose: Complete new user setup process
# Input: user_email, department, manager_id
# Output: user_summary with creation status

input_args:
  user_email: "data.user_email"  # Required: New user's email
  department: "data.department"  # Required: User's department
```

**Maintain Version History:**
- Document changes in commit messages
- Use semantic versioning for major changes
- Keep examples up to date

---

For more information, see the [API Documentation](API_Documentation.md) and [Architecture Guide](Architecture_Guide.md).
