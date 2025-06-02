#!/usr/bin/env python3
"""
Simple test for YAML generation issue.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("Testing YAML generation...")

try:
    from moveworks_wizard.models.base import CompoundAction
    from moveworks_wizard.models.actions import ActionStep
    from moveworks_wizard.serializers import serialize_compound_action
    
    # Create a simple action step
    step = ActionStep(
        action_name="GET_License_Count_Individual_User_result",
        output_key="license_result"
    )
    
    # Create compound action
    compound_action = CompoundAction(
        name="Test License Action",
        steps=[step]
    )
    
    # Generate YAML
    yaml_content = serialize_compound_action(compound_action)
    print("Generated YAML:")
    print("=" * 50)
    print(yaml_content)
    print("=" * 50)
    
    # Test with input args
    compound_action_with_args = CompoundAction(
        name="Test with Args",
        input_args={"@data_context": "GET_License_Count_Individual_User_result.@data.context"},
        steps=[step]
    )
    
    yaml_with_args = serialize_compound_action(compound_action_with_args)
    print("\nWith input_args:")
    print("=" * 50)
    print(yaml_with_args)
    print("=" * 50)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
