#!/usr/bin/env python3
"""
Phase 2 Demo - Enhanced Moveworks Compound Action Wizard

This script demonstrates the Phase 2 enhancements including:
- Built-in action catalog integration
- Enhanced validation
- Multiple step types
- Improved user experience
"""

import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from moveworks_wizard.models.base import CompoundAction
from moveworks_wizard.models.actions import ActionStep, ScriptStep
from moveworks_wizard.models.control_flow import SwitchStep, SwitchCase
from moveworks_wizard.models.terminal import ReturnStep
from moveworks_wizard.models.common import ProgressUpdates, DelayConfig
from moveworks_wizard.catalog import builtin_catalog
from moveworks_wizard.serializers import serialize_compound_action


def demo_builtin_catalog():
    """Demonstrate the built-in action catalog functionality."""
    print("🔍 Built-in Action Catalog Demo")
    print("=" * 50)
    
    # Show available categories
    categories = builtin_catalog.get_all_categories()
    print(f"Available categories: {', '.join(categories)}")
    
    # Show communication actions
    comm_actions = builtin_catalog.get_actions_by_category("Communication")
    print(f"\nCommunication actions ({len(comm_actions)}):")
    for action in comm_actions:
        print(f"  • {action.name}: {action.description}")
    
    # Demonstrate action lookup
    action = builtin_catalog.get_action("mw.send_plaintext_chat_notification")
    if action:
        print(f"\nAction Details: {action.name}")
        print(f"Description: {action.description}")
        print(f"Category: {action.category}")
        print("Parameters:")
        for param in action.parameters:
            required = "REQUIRED" if param.required else "optional"
            print(f"  • {param.name} ({param.type}, {required}): {param.description}")
            if param.example:
                print(f"    Example: {param.example}")
    
    # Demonstrate search
    search_results = builtin_catalog.search_actions("user")
    print(f"\nSearch results for 'user' ({len(search_results)} found):")
    for action in search_results[:3]:  # Show first 3
        print(f"  • {action.name}: {action.description}")
    
    print()


def demo_enhanced_validation():
    """Demonstrate enhanced validation capabilities."""
    print("✅ Enhanced Validation Demo")
    print("=" * 50)
    
    from moveworks_wizard.wizard.validators import WizardValidators
    
    # Test various validations
    test_cases = [
        ("Action Name", "mw.send_notification", WizardValidators.validate_action_name),
        ("Output Key", "user_info", WizardValidators.validate_output_key),
        ("Bender Expression", "data.employee_id", WizardValidators.validate_bender_expression),
        ("Python Code", "user_info.get('email', '').upper()", WizardValidators.validate_python_code),
    ]
    
    for test_name, test_value, validator in test_cases:
        is_valid, error = validator(test_value)
        status = "✅ VALID" if is_valid else f"❌ INVALID: {error}"
        print(f"{test_name}: '{test_value}' -> {status}")
    
    print()


def demo_complex_compound_action():
    """Create a complex compound action demonstrating Phase 2 features."""
    print("🏗️ Complex Compound Action Demo")
    print("=" * 50)
    
    # Step 1: Get user details using built-in action
    get_user_step = ActionStep(
        action_name="mw.get_user_details",
        output_key="user_info",
        input_args={"user_id": "data.employee_id"},
        progress_updates=ProgressUpdates(
            on_pending="Fetching user details...",
            on_complete="User details retrieved successfully"
        )
    )
    
    # Step 2: Process user data with script
    process_script = ScriptStep(
        code="""
# Process user information
email = user_info.get('email', '').lower()
department = user_info.get('department', 'Unknown')
full_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}"

# Create processed result
result = {
    'processed_email': email,
    'department': department,
    'display_name': full_name.strip(),
    'is_manager': user_info.get('role', '').lower() == 'manager'
}
""",
        output_key="processed_user",
        input_args={"user_info": "data.user_info"}
    )
    
    # Step 3: Conditional notification based on user role
    manager_notification = ActionStep(
        action_name="mw.send_rich_chat_notification",
        output_key="manager_notification",
        input_args={
            "user_record_id": "data.user_info.record_id",
            "card_content": "data.manager_card"
        }
    )
    
    employee_notification = ActionStep(
        action_name="mw.send_plaintext_chat_notification",
        output_key="employee_notification",
        input_args={
            "user_record_id": "data.user_info.record_id",
            "message": "Your request has been processed successfully."
        }
    )
    
    # Switch step for conditional logic
    notification_switch = SwitchStep(
        cases=[
            SwitchCase(
                condition="data.processed_user.is_manager == true",
                steps=[manager_notification]
            )
        ],
        default=[employee_notification]
    )
    
    # Step 4: Return processed results
    return_step = ReturnStep(
        output_mapper={
            "user_email": "data.processed_user.processed_email",
            "user_department": "data.processed_user.department",
            "notification_sent": "true"
        }
    )
    
    # Create the compound action
    compound_action = CompoundAction(
        name="Enhanced User Processing Workflow",
        description="Demonstrates Phase 2 features with user processing and conditional notifications",
        input_args={
            "employee_id": "data.user_id",
            "manager_card": "data.notification_card"
        },
        steps=[
            get_user_step,
            process_script,
            notification_switch,
            return_step
        ]
    )
    
    # Generate YAML
    yaml_output = serialize_compound_action(compound_action)
    
    print("Generated Compound Action YAML:")
    print("-" * 40)
    print(yaml_output)
    
    # Save to file
    output_file = "examples/generated/phase2_enhanced_workflow.yaml"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(yaml_output)
    
    print(f"\n💾 Saved to: {output_file}")
    print()


def demo_step_types():
    """Demonstrate different step types available in Phase 2."""
    print("🔧 Step Types Demo")
    print("=" * 50)
    
    # Action step with built-in action
    action_step = ActionStep(
        action_name="mw.create_ticket",
        output_key="ticket_result",
        input_args={
            "title": "data.issue_summary",
            "description": "data.issue_details",
            "requestor_id": "meta_info.requestor.employee_id",
            "priority": "Medium"
        },
        delay_config=DelayConfig(seconds=2),
        progress_updates=ProgressUpdates(
            on_pending="Creating support ticket...",
            on_complete="Support ticket created successfully"
        )
    )
    
    print("Action Step Example:")
    print(serialize_compound_action(CompoundAction(single_step=action_step)))
    
    # Script step
    script_step = ScriptStep(
        code="ticket_url = f'https://support.company.com/tickets/{ticket_result.get(\"id\")}'",
        output_key="ticket_url",
        input_args={"ticket_result": "data.ticket_result"}
    )
    
    print("\nScript Step Example:")
    print(serialize_compound_action(CompoundAction(single_step=script_step)))
    
    # Return step
    return_step = ReturnStep(
        output_mapper={
            "ticket_id": "data.ticket_result.id",
            "ticket_url": "data.ticket_url",
            "status": "created"
        }
    )
    
    print("\nReturn Step Example:")
    print(serialize_compound_action(CompoundAction(single_step=return_step)))
    print()


def main():
    """Run all Phase 2 demos."""
    print("🚀 Moveworks Compound Action Wizard - Phase 2 Demo")
    print("=" * 60)
    print()
    
    # Run all demos
    demo_builtin_catalog()
    demo_enhanced_validation()
    demo_step_types()
    demo_complex_compound_action()
    
    print("🎉 Phase 2 Demo Complete!")
    print("\nPhase 2 Features Demonstrated:")
    print("✅ Built-in action catalog with search and categorization")
    print("✅ Enhanced validation for all input types")
    print("✅ Multiple step types (action, script, switch, return)")
    print("✅ Complex workflow creation")
    print("✅ Progress updates and delay configuration")
    print("✅ Conditional logic with switch statements")
    print("✅ Improved YAML generation")
    print("\nTry the interactive wizard: python main.py")


if __name__ == "__main__":
    main()
