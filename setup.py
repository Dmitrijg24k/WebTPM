"""
Setup script for WebTPM - Neural Cryptography Research Project

This package implements Tree-like Parity Machines for secure key exchange
in neural cryptography applications.
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="webtpm",
    version="1.0.0",
    author="Dmitrijg24k",
    description="Neural Cryptography: Tree-like Parity Machine Implementation",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Dmitrijg24k/WebTPM",
    project_urls={
        "Bug Reports": "https://github.com/Dmitrijg24k/WebTPM/issues",
        "Source": "https://github.com/Dmitrijg24k/WebTPM",
        "Documentation": "https://github.com/Dmitrijg24k/WebTPM#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-django>=4.7.0",
            "black>=23.9.1",
            "flake8>=6.1.0",
            "mypy>=1.5.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    keywords=[
        "neural cryptography",
        "tree parity machine",
        "tpm",
        "key exchange",
        "neural networks",
        "cryptography",
        "cybersecurity",
        "django",
        "websocket",
        "research",
    ],
    include_package_data=True,
    zip_safe=False,
)
