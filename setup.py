#!/usr/bin/env python3
"""
Setup script for Moveworks YAML Wizard for Compound Actions.

This script configures the package for distribution and installation.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements from requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#') and not line.startswith('-')
        ]
else:
    requirements = [
        "PyYAML>=6.0",
        "click>=8.0.0", 
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0"
    ]

# Filter out development dependencies for production install
production_requirements = [
    req for req in requirements 
    if not any(dev_pkg in req.lower() for dev_pkg in ['pytest', 'black', 'flake8', 'mypy', 'cov'])
]

setup(
    name="moveworks-yaml-wizard",
    version="1.0.0",
    author="Moveworks Development Team",
    author_email="dev@moveworks.com",
    description="A Python wizard for creating Moveworks Compound Action YAML files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/moveworks/yaml-wizard",
    project_urls={
        "Bug Reports": "https://github.com/moveworks/yaml-wizard/issues",
        "Source": "https://github.com/moveworks/yaml-wizard",
        "Documentation": "https://github.com/moveworks/yaml-wizard/blob/main/README.md",
    },
    
    # Package configuration
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    
    # Dependencies
    install_requires=production_requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "gui": [
            "customtkinter>=5.0.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "customtkinter>=5.0.0",
        ]
    },
    
    # Entry points for CLI commands
    entry_points={
        "console_scripts": [
            "moveworks-wizard=moveworks_wizard.wizard.cli:cli",
            "mw-wizard=moveworks_wizard.wizard.cli:cli",
            "compound-action-wizard=moveworks_wizard.wizard.cli:cli",
        ],
    },
    
    # Package metadata
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Environment :: X11 Applications",
    ],
    
    # Python version requirement
    python_requires=">=3.8",
    
    # Keywords for PyPI search
    keywords=[
        "moveworks",
        "yaml",
        "wizard",
        "compound-actions", 
        "automation",
        "workflow",
        "cli",
        "code-generation"
    ],
    
    # Package data
    package_data={
        "moveworks_wizard": [
            "templates/*.yaml",
            "catalog/*.json",
            "docs/*.md",
        ],
    },
    
    # Zip safe
    zip_safe=False,
    
    # Additional metadata
    platforms=["any"],
    license="MIT",
)
