#!/usr/bin/env python3
"""
Quick check for auto-fill functionality.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

print("🔍 Checking Auto-fill Implementation...")

# Check if StepDialog has the auto-fill methods
try:
    from moveworks_wizard.gui.main_window import StepDialog
    
    methods = [
        '_auto_fill_output_key',
        '_suggest_action_names', 
        '_insert_code_template',
        '_suggest_return_values'
    ]
    
    print(f"StepDialog class found at: {StepDialog}")
    
    for method in methods:
        if hasattr(StepDialog, method):
            print(f"✅ {method}")
        else:
            print(f"❌ {method} - MISSING")
    
    # Check the source file directly
    import inspect
    source_file = inspect.getfile(StepDialog)
    print(f"\nSource file: {source_file}")
    
    # Read the source to see if methods are there
    with open(source_file, 'r') as f:
        content = f.read()
        
    for method in methods:
        if f"def {method}" in content:
            print(f"✅ {method} found in source")
        else:
            print(f"❌ {method} NOT in source")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🔍 Checking YAML Generation...")

try:
    from moveworks_wizard.models.base import CompoundAction
    from moveworks_wizard.models.actions import ActionStep
    from moveworks_wizard.serializers import serialize_compound_action
    
    # Simple test
    step = ActionStep(action_name="test", output_key="result")
    ca = CompoundAction(steps=[step])
    yaml_out = serialize_compound_action(ca)
    
    print("YAML Output:")
    print("-" * 30)
    print(yaml_out)
    print("-" * 30)
    
    if yaml_out.strip().startswith('steps:'):
        print("✅ YAML order correct")
    else:
        print("❌ YAML order wrong")
        
except Exception as e:
    print(f"YAML Error: {e}")
    import traceback
    traceback.print_exc()
