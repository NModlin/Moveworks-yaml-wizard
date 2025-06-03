#!/usr/bin/env python3
"""
Test the JSON analyzer with the license usage example.
"""

import sys
import json
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Your example JSON
license_json = {
    "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('mtestacct%40rehrig.com')/licenseDetails",
    "value": [
        {
            "id": "7V6vYLOcM0qoGqQFu4z1Y_e2zO9BVg5OvRC0l24b9o4",
            "skuId": "efccb6f7-5641-4e0e-bd10-b4976e1bf68e",
            "skuPartNumber": "EMS",
            "servicePlans": [
                {
                    "servicePlanId": "113feb6c-3fe4-4440-bddc-54d774bf0318",
                    "servicePlanName": "EXCHANGE_S_FOUNDATION",
                    "provisioningStatus": "Success",
                    "appliesTo": "Company"
                },
                {
                    "servicePlanId": "932ad362-64a8-4783-9106-97849a1a30b9",
                    "servicePlanName": "ADALLOM_S_DISCOVERY",
                    "provisioningStatus": "Success",
                    "appliesTo": "User"
                }
            ]
        },
        {
            "id": "7V6vYLOcM0qoGqQFu4z1Y4RZWEsbZYpEnlM7EPBpz38",
            "skuId": "4b585984-651b-448a-9e53-3b10f069cf7f",
            "skuPartNumber": "DESKLESSPACK",
            "servicePlans": [
                {
                    "servicePlanId": "13b6da2c-0d84-450e-9f69-a33e221387ca",
                    "servicePlanName": "PEOPLE_SKILLS_FOUNDATION",
                    "provisioningStatus": "PendingProvisioning",
                    "appliesTo": "User"
                }
            ]
        }
    ]
}

def main():
    try:
        from moveworks_wizard.utils.json_analyzer import JSONAnalyzer
        
        print("Testing JSON analyzer with license usage data...")
        print("=" * 60)
        
        analyzer = JSONAnalyzer()
        suggestions = analyzer.analyze_json(json.dumps(license_json), "license_api")
        
        print(f"Found {len(suggestions)} suggestions:")
        print()
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i:2d}. Path: {suggestion.path}")
            print(f"    Type: {suggestion.data_type}")
            print(f"    Description: {suggestion.description}")
            print(f"    Bender: {suggestion.bender_expression}")
            print(f"    Example: {suggestion.example_usage}")
            print()

        # Generate comprehensive YAML example
        print("\n" + "="*60)
        print("COMPREHENSIVE YAML EXAMPLE FOR ARRAY DATA EXTRACTION:")
        print("="*60)

        yaml_example = analyzer.generate_comprehensive_yaml_example("license_api")
        print(yaml_example)

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
