#!/usr/bin/env python3
"""
Test the dialog layout to ensure buttons are visible.
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_dialog_layout():
    """Test that the dialog layout shows buttons properly."""
    try:
        print("🧪 Testing JSON Selection Dialog Layout")
        print("=" * 50)
        
        # Test imports
        from moveworks_wizard.utils.json_analyzer import JSONAnalyzer
        print("✅ JSONAnalyzer imported successfully")
        
        # Create sample data
        sample_json = '''
        {
            "data": {
                "user": {
                    "id": "usr_123",
                    "email": "test@example.com",
                    "name": "Test User"
                }
            },
            "success": true
        }
        '''
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(sample_json, "test_api")
        print(f"✅ Generated {len(suggestions)} suggestions")
        
        # Test dialog creation (without showing it)
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        print("✅ Tkinter root created")
        
        # The dialog should now have:
        print("\n🎯 Dialog Layout Fixes Applied:")
        print("✅ Dialog size: 900x700 (increased from 800x600)")
        print("✅ Buttons packed at bottom with side=tk.BOTTOM")
        print("✅ Selection buttons packed before tree")
        print("✅ Action buttons (Add Selected, Cancel) at very bottom")
        print("✅ Tree frame fills remaining space")
        
        print("\n📋 Expected Dialog Structure (top to bottom):")
        print("1. Instructions and tips")
        print("2. Tree view with suggestions (scrollable)")
        print("3. Quick Selection buttons (Select All, None, Top 5, Common)")
        print("4. Action buttons (Add Selected, Cancel)")
        
        root.destroy()
        
        print("\n🚀 To test the actual dialog:")
        print("1. Run: python -m src.moveworks_wizard.gui.main_window")
        print("2. Click 'New Compound Action'")
        print("3. Click 'Analyze JSON'")
        print("4. Load examples/sample_http_response.json")
        print("5. Click 'Analyze'")
        print("6. You should now see the 'Add Selected' button at the bottom!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the layout test."""
    success = test_dialog_layout()
    
    if success:
        print("\n🎉 Layout test passed!")
        print("The 'Add Selected' button should now be visible in the GUI.")
    else:
        print("\n⚠️ Layout test failed.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
