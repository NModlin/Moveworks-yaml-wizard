# Moveworks YAML Wizard - Deployment Guide

## Overview

This guide covers the deployment of the Moveworks YAML Wizard for production use. The wizard is packaged as a standard Python package and can be distributed via PyPI, internal package repositories, or direct installation.

## Package Information

- **Package Name**: `moveworks-yaml-wizard`
- **Version**: 1.0.0
- **Python Requirements**: Python 3.8+
- **License**: MIT
- **Entry Points**: `moveworks-wizard`, `mw-wizard`, `compound-action-wizard`

## Installation Methods

### 1. PyPI Installation (Recommended)

```bash
# Install the latest stable version
pip install moveworks-yaml-wizard

# Install with GUI support
pip install "moveworks-yaml-wizard[gui]"

# Install with development tools
pip install "moveworks-yaml-wizard[dev]"

# Install all optional features
pip install "moveworks-yaml-wizard[all]"
```

### 2. Development Installation

```bash
# Clone the repository
git clone <repository-url>
cd Moveworks-yaml-wizard

# Install in development mode
pip install -e .

# Install with all development dependencies
pip install -e ".[all]"
```

### 3. Direct Installation from Source

```bash
# Download and install from source
git clone <repository-url>
cd Moveworks-yaml-wizard
python setup.py install

# Or using pip
pip install .
```

## Verification

After installation, verify the wizard is working correctly:

```bash
# Check installation
moveworks-wizard --help

# Test basic functionality
moveworks-wizard wizard --help

# Verify all commands
mw-wizard --version
compound-action-wizard --version
```

## Distribution Options

### 1. PyPI Distribution

The package is ready for PyPI distribution with proper metadata:

```bash
# Build distribution packages
python -m build

# Upload to PyPI (requires credentials)
python -m twine upload dist/*

# Upload to test PyPI first
python -m twine upload --repository testpypi dist/*
```

### 2. Internal Package Repository

For enterprise deployment, the package can be hosted on internal repositories:

```bash
# Build wheel for internal distribution
python setup.py bdist_wheel

# Upload to internal PyPI server
twine upload --repository-url https://internal-pypi.company.com dist/*
```

### 3. Docker Deployment

Create a Docker image for containerized deployment:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy package files
COPY . .

# Install the wizard
RUN pip install .

# Set entry point
ENTRYPOINT ["moveworks-wizard"]
```

## Configuration

### Environment Variables

The wizard supports configuration via environment variables:

```bash
# Set default output directory
export MOVEWORKS_WIZARD_OUTPUT_DIR="/path/to/output"

# Enable debug mode
export MOVEWORKS_WIZARD_DEBUG=true

# Set custom template directory
export MOVEWORKS_WIZARD_TEMPLATES="/path/to/templates"
```

### Configuration File

Create a configuration file at `~/.moveworks-wizard/config.yaml`:

```yaml
# Default configuration
output_directory: "~/moveworks-actions"
debug_mode: false
auto_save: true
template_directory: null

# Validation settings
strict_validation: true
allow_experimental_features: false

# UI preferences
default_interface: "cli"
show_welcome_message: true
```

## Production Deployment

### 1. System Requirements

- **Python**: 3.8 or higher
- **Memory**: 256MB minimum, 512MB recommended
- **Disk Space**: 50MB for installation, additional space for generated files
- **Network**: Internet access for package installation (if using PyPI)

### 2. Security Considerations

- **Input Validation**: All user inputs are validated before processing
- **File Permissions**: Generated YAML files use secure default permissions
- **No Network Calls**: The wizard operates entirely offline after installation
- **Safe Dependencies**: All dependencies are from trusted sources

### 3. Performance Optimization

```bash
# Install with performance optimizations
pip install "moveworks-yaml-wizard[all]" --compile

# Use faster YAML parser (optional)
pip install pyyaml[libyaml]
```

### 4. Monitoring and Logging

Enable logging for production monitoring:

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/moveworks-wizard.log'),
        logging.StreamHandler()
    ]
)
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: Generate Compound Actions

on:
  workflow_dispatch:
    inputs:
      template_name:
        description: 'Template to use'
        required: true
        default: 'user_management'

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install Moveworks Wizard
        run: pip install moveworks-yaml-wizard
      
      - name: Generate YAML
        run: |
          moveworks-wizard templates use ${{ github.event.inputs.template_name }} \
            --output generated-action.yaml
      
      - name: Upload artifact
        uses: actions/upload-artifact@v3
        with:
          name: compound-action
          path: generated-action.yaml
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    
    stages {
        stage('Install') {
            steps {
                sh 'pip install moveworks-yaml-wizard'
            }
        }
        
        stage('Generate') {
            steps {
                sh '''
                    moveworks-wizard wizard \
                        --output ${WORKSPACE}/compound-action.yaml \
                        --non-interactive
                '''
            }
        }
        
        stage('Validate') {
            steps {
                sh 'moveworks-wizard validate compound-action.yaml'
            }
        }
    }
    
    post {
        always {
            archiveArtifacts artifacts: '*.yaml', fingerprint: true
        }
    }
}
```

## Troubleshooting

### Common Issues

**1. Import Errors**
```bash
# Solution: Ensure all dependencies are installed
pip install --upgrade moveworks-yaml-wizard

# Check for missing dependencies
pip check
```

**2. Permission Errors**
```bash
# Solution: Install with user permissions
pip install --user moveworks-yaml-wizard

# Or use virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install moveworks-yaml-wizard
```

**3. Command Not Found**
```bash
# Solution: Check PATH includes pip install location
echo $PATH

# Add to PATH if needed (Linux/Mac)
export PATH="$HOME/.local/bin:$PATH"

# On Windows, add to system PATH:
# %APPDATA%\Python\Python310\Scripts
```

### Debug Mode

Enable debug mode for troubleshooting:

```bash
# Enable debug output
moveworks-wizard --debug wizard

# Or set environment variable
export MOVEWORKS_WIZARD_DEBUG=true
moveworks-wizard wizard
```

### Log Analysis

Check logs for issues:

```bash
# View recent logs
tail -f ~/.moveworks-wizard/logs/wizard.log

# Search for errors
grep ERROR ~/.moveworks-wizard/logs/wizard.log
```

## Maintenance

### Updates

```bash
# Check for updates
pip list --outdated | grep moveworks-yaml-wizard

# Update to latest version
pip install --upgrade moveworks-yaml-wizard

# Update with all extras
pip install --upgrade "moveworks-yaml-wizard[all]"
```

### Cleanup

```bash
# Remove old generated files
find ~/moveworks-actions -name "*.yaml" -mtime +30 -delete

# Clear cache
rm -rf ~/.moveworks-wizard/cache/

# Reset configuration
rm ~/.moveworks-wizard/config.yaml
```

## Support

### Documentation
- [User Guide](User_Guide.md) - Complete usage instructions
- [API Documentation](API_Documentation.md) - Developer reference
- [Architecture Guide](Architecture_Guide.md) - System design

### Community
- **Issues**: Report bugs and feature requests on GitHub
- **Discussions**: Community support and questions
- **Documentation**: Contribute to documentation improvements

### Enterprise Support
For enterprise deployments, consider:
- **Training**: User training sessions
- **Custom Templates**: Organization-specific workflow templates
- **Integration Support**: Help with CI/CD integration
- **Priority Support**: Dedicated support channels

---

This deployment guide ensures successful installation and operation of the Moveworks YAML Wizard in production environments.
