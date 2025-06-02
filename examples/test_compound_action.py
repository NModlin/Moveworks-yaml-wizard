#!/usr/bin/env python3
"""
Example script to test the Moveworks YAML Wizard functionality.

This script creates a sample compound action and generates YAML output
to demonstrate the core functionality.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from moveworks_wizard.models.base import CompoundAction
from moveworks_wizard.models.actions import ActionStep, ScriptStep
from moveworks_wizard.models.common import ProgressUpdates, DelayConfig
from moveworks_wizard.serializers import serialize_compound_action


def create_simple_action_example():
    """Create a simple action-based compound action."""
    print("Creating simple action example...")
    
    # Create an action step
    action_step = ActionStep(
        action_name="fetch_user_details",
        output_key="user_info",
        input_args={
            "user_id": "data.user_id"
        },
        progress_updates=ProgressUpdates(
            on_pending="Fetching user details, please wait...",
            on_complete="User details fetched successfully."
        )
    )
    
    # Create compound action
    compound_action = CompoundAction(
        name="Get User Details",
        description="Fetches user details from the system",
        input_args={
            "user_id": "data.employee_id"
        },
        single_step=action_step
    )
    
    return compound_action


def create_multi_step_example():
    """Create a multi-step compound action."""
    print("Creating multi-step example...")
    
    # Step 1: Fetch user details
    step1 = ActionStep(
        action_name="fetch_user_details",
        output_key="user_info",
        input_args={
            "user_id": "data.user_id"
        }
    )
    
    # Step 2: Process the data with a script
    step2 = ScriptStep(
        code="return user_info.get('email', '').upper()",
        output_key="processed_email",
        input_args={
            "user_info": "data.user_info"
        }
    )
    
    # Step 3: Send notification
    step3 = ActionStep(
        action_name="mw.send_plaintext_chat_notification",
        output_key="notification_result",
        input_args={
            "user_record_id": "data.user_info.record_id",
            "message": "Your email has been processed: data.processed_email"
        }
    )
    
    # Create compound action
    compound_action = CompoundAction(
        name="Process User Email",
        description="Fetches user details, processes email, and sends notification",
        input_args={
            "user_id": "data.employee_id"
        },
        steps=[step1, step2, step3]
    )
    
    return compound_action


def create_script_example():
    """Create a script-based compound action."""
    print("Creating script example...")
    
    # Multi-line script
    script_code = """
# Calculate statistics from a list of numbers
sum_numbers = sum(numbers)
count_numbers = len(numbers)
average = sum_numbers / count_numbers if count_numbers > 0 else 0

stats = {
    'sum': sum_numbers,
    'count': count_numbers, 
    'average': average,
    'max': max(numbers) if numbers else 0,
    'min': min(numbers) if numbers else 0
}

return stats
    """.strip()
    
    script_step = ScriptStep(
        code=script_code,
        output_key="statistics",
        input_args={
            "numbers": "data.number_list"
        }
    )
    
    compound_action = CompoundAction(
        name="Calculate Statistics",
        description="Calculates statistical information from a list of numbers",
        input_args={
            "number_list": "data.input_numbers"
        },
        single_step=script_step
    )
    
    return compound_action


def main():
    """Main function to run examples."""
    print("🧙 Moveworks YAML Wizard - Example Generator")
    print("=" * 50)
    
    examples = [
        ("simple_action", create_simple_action_example),
        ("multi_step", create_multi_step_example),
        ("script_example", create_script_example)
    ]
    
    # Create examples directory
    examples_dir = Path("examples/generated")
    examples_dir.mkdir(exist_ok=True)
    
    for name, create_func in examples:
        try:
            print(f"\n📝 Generating {name}...")
            
            # Create the compound action
            compound_action = create_func()
            
            # Generate YAML
            yaml_content = serialize_compound_action(compound_action)
            
            # Save to file
            output_file = examples_dir / f"{name}.yaml"
            output_file.write_text(yaml_content, encoding='utf-8')
            
            print(f"✅ Saved to: {output_file}")
            print(f"📄 Preview:")
            print("-" * 30)
            print(yaml_content)
            print("-" * 30)
            
        except Exception as e:
            print(f"❌ Error generating {name}: {e}")
    
    print(f"\n🎉 Example generation complete!")
    print(f"📁 Check the {examples_dir} directory for generated YAML files.")


if __name__ == "__main__":
    main()
