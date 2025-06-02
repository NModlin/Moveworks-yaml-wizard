#!/usr/bin/env python3
"""
Main entry point for the Moveworks Compound Action Wizard.

This script provides the command-line interface for creating
Moveworks Compound Action YAML files.
"""

import sys
from pathlib import Path

# Add src to Python path for development
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from moveworks_wizard.wizard.cli import main

if __name__ == "__main__":
    main()
