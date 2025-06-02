#!/usr/bin/env python3
"""
Test the YAML generation fix for input_args.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_yaml_with_input_args():
    """Test YAML generation with input_args included."""
    print("🧪 Testing YAML Generation with input_args Fix...")
    
    try:
        from moveworks_wizard.models.base import CompoundAction
        from moveworks_wizard.models.actions import ActionStep
        from moveworks_wizard.serializers import serialize_compound_action
        
        # Test 1: Action step with no input_args (should show empty input_args)
        print("\n1. Testing action step with no input_args:")
        step1 = ActionStep(
            action_name="example_action_1_name",
            output_key="example_result"
        )
        
        compound_action1 = CompoundAction(steps=[step1])
        yaml1 = serialize_compound_action(compound_action1)
        print(yaml1)
        
        # Test 2: Action step with input_args
        print("\n2. Testing action step with input_args:")
        step2 = ActionStep(
            action_name="example_action_2_name", 
            output_key="example_result_2",
            input_args={"example_input": "Example Value"}
        )
        
        compound_action2 = CompoundAction(steps=[step2])
        yaml2 = serialize_compound_action(compound_action2)
        print(yaml2)
        
        # Test 3: Multiple steps (like your expected format)
        print("\n3. Testing multiple steps:")
        step3 = ActionStep(
            action_name="example_action_1_name",
            output_key="result_1",
            input_args={"example_input_1": "Example Value 1"}
        )

        step4 = ActionStep(
            action_name="example_action_2_name",
            output_key="result_2",
            input_args={"example_input_2": "Example Value 2"}
        )
        
        compound_action3 = CompoundAction(steps=[step3, step4])
        yaml3 = serialize_compound_action(compound_action3)
        print(yaml3)
        
        # Verify the format
        if "input_args:" in yaml1 and "input_args:" in yaml2 and "input_args:" in yaml3:
            print("✅ SUCCESS: input_args field is now included in all action steps!")
            return True
        else:
            print("❌ FAILED: input_args field is still missing")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🔧 Testing YAML input_args Fix")
    print("=" * 50)
    
    success = test_yaml_with_input_args()
    
    if success:
        print("\n🎉 Fix successful! The GUI should now generate correct YAML.")
        print("\nTo test the GUI:")
        print("  python run_gui_with_autofill.py")
    else:
        print("\n⚠️  Fix needs more work.")

if __name__ == "__main__":
    main()
