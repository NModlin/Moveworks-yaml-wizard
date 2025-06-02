#!/usr/bin/env python3
"""
Test YAML generation with special characters like @.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_yaml_special_characters():
    """Test YAML generation with @ and other special characters."""
    print("🧪 Testing YAML with Special Characters...")
    
    try:
        from moveworks_wizard.models.base import CompoundAction
        from moveworks_wizard.models.actions import ActionStep
        from moveworks_wizard.serializers import serialize_compound_action
        
        # Test with @ character in input_args
        print("\n1. Testing with @ character:")
        step = ActionStep(
            action_name="GET_License_Count_Individual_User",
            output_key="get_license_count_individual_user_result"
        )
        
        compound_action = CompoundAction(
            steps=[step],
            input_args={
                "@odata_context": "GET_License_Count_Individual_User.@odata.context"
            }
        )
        
        yaml_content = serialize_compound_action(compound_action)
        print(yaml_content)
        
        # Test with various special characters
        print("\n2. Testing with various special characters:")
        step2 = ActionStep(
            action_name="test_action",
            output_key="test_result",
            input_args={
                "@special": "value",
                "normal_key": "normal_value",
                "colon:key": "value_with_colon",
                "hash#key": "value_with_hash"
            }
        )
        
        compound_action2 = CompoundAction(steps=[step2])
        yaml_content2 = serialize_compound_action(compound_action2)
        print(yaml_content2)
        
        # Check if @ characters are properly quoted
        if '"@odata_context"' in yaml_content or "'@odata_context'" in yaml_content:
            print("✅ SUCCESS: @ characters are properly quoted!")
            return True
        else:
            print("❌ FAILED: @ characters are not properly quoted")
            print("Looking for quoted @odata_context in:")
            print(repr(yaml_content))
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🔧 Testing YAML Special Character Handling")
    print("=" * 50)
    
    success = test_yaml_special_characters()
    
    if success:
        print("\n🎉 YAML special character handling is working!")
        print("\nThe GUI should now generate valid YAML without syntax errors.")
    else:
        print("\n⚠️  YAML special character handling needs more work.")

if __name__ == "__main__":
    main()
