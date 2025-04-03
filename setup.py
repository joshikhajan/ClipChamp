#!/usr/bin/env python3
"""
Setup script for the Clipboard History Tool.
This script creates a distributable package for the application.
"""

from setuptools import setup

setup(
    name="clipboard-history-tool",
    version="1.0.0",
    description="A clipboard history manager that tracks and stores clipboard contents",
    author="Manus AI",
    packages=["clipboard_history_tool_package"],
    package_dir={"clipboard_history_tool_package": "."},
    py_modules=["clipboard_history_tool"],
    entry_points={
        "console_scripts": [
            "clipboard-history-tool=clipboard_history_tool:main",
        ],
    },
    install_requires=[
        "pyperclip>=1.8.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
)
