#!/usr/bin/env python3
"""
Validate the YAML output to ensure it's syntactically correct.
"""

import sys
import yaml
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def validate_yaml_syntax():
    """Validate that the generated YAML is syntactically correct."""
    print("🔍 Validating YAML Syntax...")
    
    try:
        from moveworks_wizard.models.base import CompoundAction
        from moveworks_wizard.models.actions import ActionStep
        from moveworks_wizard.serializers import serialize_compound_action
        
        # Create the exact same structure as your example
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
        print("Generated YAML:")
        print("=" * 50)
        print(yaml_content)
        print("=" * 50)
        
        # Try to parse it back with standard YAML parser
        try:
            parsed = yaml.safe_load(yaml_content)
            print("✅ YAML syntax is valid!")
            
            # Check structure
            if 'steps' in parsed and 'input_args' in parsed:
                print("✅ YAML structure is correct!")
                
                # Check that @ character is handled properly
                if '@odata_context' in parsed['input_args']:
                    print("✅ Special characters (@) are handled correctly!")
                    
                    # Check that action has input_args field
                    if 'input_args' in parsed['steps'][0]['action']:
                        print("✅ Action steps include input_args field!")
                        return True
                    else:
                        print("❌ Action steps missing input_args field")
                        return False
                else:
                    print("❌ Special character handling failed")
                    return False
            else:
                print("❌ YAML structure is incorrect")
                print(f"Parsed structure: {list(parsed.keys())}")
                return False
                
        except yaml.YAMLError as e:
            print(f"❌ YAML syntax error: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Error generating YAML: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the validation."""
    print("✅ YAML Validation Test")
    print("=" * 50)
    
    success = validate_yaml_syntax()
    
    if success:
        print("\n🎉 All YAML issues are fixed!")
        print("\nYour YAML should now:")
        print("  ✅ Have no syntax errors")
        print("  ✅ Handle @ characters correctly")
        print("  ✅ Include input_args in action steps")
        print("  ✅ Have proper structure")
    else:
        print("\n⚠️  Some YAML issues remain.")

if __name__ == "__main__":
    main()
