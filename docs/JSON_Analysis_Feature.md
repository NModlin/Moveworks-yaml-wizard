# JSON Analysis Feature for HTTP Connector Integration

## Overview

The JSON Analysis feature allows users to input test results from HTTP connectors as JSON and automatically receive variable suggestions for use in Compound Actions. This feature significantly improves the developer experience when working with real API responses and helps identify the exact variables needed for Action Activity integration.

## Problem Solved

When working with HTTP connectors in Moveworks Action Activities, developers often need to:
1. Test their HTTP connector to see what data is returned
2. Manually analyze the JSON response structure
3. Figure out which variables they need for their Compound Action
4. Write the correct Bender expressions to access nested data
5. Understand the data types and structure for proper usage

This manual process is time-consuming and error-prone. The JSON Analysis feature automates this entire workflow.

## How It Works

### 1. JSON Input Methods
- **File Upload**: Load JSON from a file (`--file` option)
- **Direct Paste**: Paste JSON directly into the CLI
- **Interactive Integration**: Use within the wizard workflow

### 2. Analysis Process
The analyzer:
- Parses the JSON structure recursively
- Identifies all accessible data paths
- Detects data types (string, integer, email, URL, UUID, date, etc.)
- Generates appropriate Bender expressions
- Creates usage examples for each variable
- Prioritizes suggestions based on common patterns

### 3. Variable Suggestions
Each suggestion includes:
- **Path**: The JSON path (e.g., `data.user.email`)
- **Data Type**: Detected type with special pattern recognition
- **Description**: Human-readable description
- **Bender Expression**: Ready-to-use expression (e.g., `user_api.data.user.email`)
- **Example Usage**: How to use in Compound Actions

## Usage Examples

### Command Line Analysis
```bash
# Analyze a JSON file
moveworks-wizard analyze-json --file response.json --source user_api

# Interactive analysis
moveworks-wizard analyze-json
# Then paste your JSON data
```

### Integrated Wizard Usage
```bash
moveworks-wizard wizard
# When prompted for input arguments:
# "Do you have JSON test results from an HTTP connector to analyze?" → Yes
# Choose input method and provide JSON
# Select variables from suggestions
```

### Sample JSON Response
```json
{
  "data": {
    "user": {
      "id": "usr_12345",
      "email": "john.doe@company.com",
      "department": "Engineering",
      "manager": {
        "id": "usr_67890",
        "email": "manager@company.com"
      }
    }
  },
  "success": true
}
```

### Generated Suggestions
```
1. data.user.id
   Type: string
   Description: Unique identifier (string)
   Bender: user_api.data.user.id
   Example: input_args: {"user_id": "data.user.id"}

2. data.user.email
   Type: email
   Description: Email address (email)
   Bender: user_api.data.user.email
   Example: input_args: {"recipient": "data.user.email"}

3. success
   Type: boolean
   Description: Success indicator (boolean)
   Bender: user_api.success
   Example: condition: "success == true"
```

## Features

### Smart Data Type Detection
- **Email addresses**: Automatically detected and marked as `email` type
- **URLs**: Recognized and marked as `url` type
- **UUIDs**: Pattern-matched and marked as `uuid` type
- **Dates**: ISO date formats detected as `date` type
- **Arrays**: Shows length and provides `[0]` access patterns
- **Nested objects**: Recursively analyzed with depth limits

### Intelligent Prioritization
Variables are prioritized based on:
1. **Common patterns**: `id`, `email`, `name`, `status` fields get higher priority
2. **Path depth**: Shorter paths are prioritized over deeply nested ones
3. **Data type usefulness**: Practical types (string, email, boolean) over complex objects
4. **Naming conventions**: Fields with meaningful names are prioritized

### Flexible Integration
- **Standalone tool**: Use `analyze-json` command independently
- **Wizard integration**: Seamlessly integrated into the interactive wizard
- **File export**: Save suggestions to JSON for later reference
- **Filtering**: Filter suggestions by type or pattern

## Action Activity Integration

### Input Mappers
The generated Bender expressions can be used directly in Action Activity input mappers:

```yaml
# In your Action Activity configuration
input_mapper:
  user_id: "user_api.data.user.id"
  user_email: "user_api.data.user.email"
  manager_id: "user_api.data.user.manager.id"
```

### Compound Action Usage
```yaml
input_args:
  user_id: "data.user_id"        # Maps to user_api.data.user.id
  user_email: "data.user_email"  # Maps to user_api.data.user.email
  manager_id: "data.manager_id"  # Maps to user_api.data.user.manager.id

steps:
  - action:
      action_name: "mw.user.update"
      output_key: "update_result"
      input_args:
        user_id: "data.user_id"
        email: "data.user_email"
```

## Advanced Features

### Array Handling
```json
{
  "users": [
    {"id": 1, "name": "John"},
    {"id": 2, "name": "Jane"}
  ]
}
```

Generates suggestions:
- `users[0].id` - First user's ID
- `users[0].name` - First user's name
- `users.length` - Number of users

### Nested Object Analysis
```json
{
  "user": {
    "profile": {
      "contact": {
        "email": "user@company.com"
      }
    }
  }
}
```

Generates: `user_api.user.profile.contact.email`

### Pattern Recognition
The analyzer recognizes common API patterns:
- **REST API responses**: `data`, `result`, `payload` containers
- **User objects**: `id`, `email`, `name`, `status` fields
- **Metadata**: `request_id`, `timestamp`, `api_version`
- **Pagination**: `page`, `limit`, `total`, `has_more`
- **Error handling**: `success`, `error`, `message`, `code`

## Technical Implementation

### Core Components
- **JSONAnalyzer**: Main analysis engine
- **VariableSuggestion**: Data structure for suggestions
- **CLI Integration**: Command-line interface
- **Wizard Integration**: Interactive workflow integration

### Performance
- **Fast analysis**: Processes large JSON files in milliseconds
- **Memory efficient**: Streaming analysis for large datasets
- **Depth limiting**: Prevents excessive nesting analysis
- **Smart filtering**: Focuses on useful variables

### Error Handling
- **JSON validation**: Clear error messages for invalid JSON
- **Graceful degradation**: Continues analysis even with problematic data
- **User feedback**: Helpful error messages and suggestions

## Benefits

### For Developers
1. **Faster development**: No manual JSON analysis required
2. **Fewer errors**: Correct Bender expressions generated automatically
3. **Better understanding**: Clear data type and usage information
4. **Consistent patterns**: Standardized variable naming and usage

### For Action Activities
1. **Easier integration**: Direct mapping from HTTP connector to Compound Action
2. **Reliable data flow**: Validated paths and expressions
3. **Type safety**: Known data types for proper handling
4. **Documentation**: Self-documenting variable usage

### For Teams
1. **Knowledge sharing**: Standardized approach to API integration
2. **Onboarding**: Easier for new developers to understand data structures
3. **Maintenance**: Clear documentation of data dependencies
4. **Testing**: Known data structures for test case creation

## Future Enhancements

### Planned Features
1. **Schema validation**: Validate JSON against expected schemas
2. **Multiple source analysis**: Compare multiple API responses
3. **Template generation**: Auto-generate Compound Action templates
4. **API documentation**: Generate documentation from JSON analysis
5. **Data transformation**: Suggest data transformation patterns

### Integration Opportunities
1. **IDE plugins**: Direct integration with development environments
2. **API testing tools**: Integration with Postman, Insomnia, etc.
3. **Documentation tools**: Auto-generate API documentation
4. **Monitoring**: Track API response changes over time

## Conclusion

The JSON Analysis feature significantly improves the developer experience when working with HTTP connectors and Action Activities. By automating the tedious process of analyzing JSON responses and generating variable suggestions, developers can focus on building workflows rather than parsing data structures.

This feature represents a major step forward in making Moveworks Action Activities more accessible and developer-friendly, reducing the time and expertise required to integrate with external APIs and systems.
