#!/usr/bin/env python3
"""
Script d'installation pour PomodoroWidget
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="PomodoroWidget",
    version="1.0.0",
    author="Dapeyco",
    author_email="",
    description="Widget Pomodoro pour Windows avec overlay toujours visible",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dapeyco/PomodoroWidget",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Desktop Environment",
        "Topic :: Office/Business :: Scheduling",
    ],
    python_requires=">=3.11",
    install_requires=[
        "pystray>=0.19.0",
        "Pillow>=9.0.0",
    ],
    entry_points={
        "console_scripts": [
            "pomodoro-widget=main:main",
        ],
    },
)
