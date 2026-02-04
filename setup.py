#!/usr/bin/env python3
"""
Setup script for AMP CLI - Automated Model Pipeline
"""

from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="amp-cli",
    version="1.0.0",
    author="GenX Trading Platform",
    author_email="support@genx-trading.com",
    description="Automated Model Pipeline CLI for GenX Trading Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mouy-leng/GenX-EA_Script",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=13.0.0",
        "typer>=0.9.0",
        "requests>=2.28.0",
        "pyyaml>=6.0",
        "python-dotenv>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "amp=amp_cli:app",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.yaml", "*.yml"],
    },
)
