#!/usr/bin/env python3
"""
Quick test of the enhanced JSON analyzer.
"""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_json_analyzer():
    try:
        from moveworks_wizard.utils.json_analyzer import JSONAnalyzer
        
        # Simple test data
        test_json = {
            "users": [
                {"id": 1, "name": "John", "email": "john@test.com"},
                {"id": 2, "name": "Jane", "email": "jane@test.com"}
            ]
        }
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(str(test_json).replace("'", '"'), "test_api")
        
        print(f"✅ JSON Analyzer working! Found {len(suggestions)} suggestions")
        
        # Test YAML generation
        yaml_example = analyzer.generate_comprehensive_yaml_example("test_api")
        print("✅ YAML generation working!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing JSON Analyzer...")
    success = test_json_analyzer()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Tests failed!")
