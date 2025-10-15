"""
🪐 Project Pluto - Setup Configuration
"""

from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text(encoding="utf-8")

setup(
    name="project-pluto",
    version="0.1.0",
    author="Your Name",
    description="Offline voice assistant test architecture using Vosk + Qwen2.5 + Piper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pluto",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "vosk>=0.3.45",
        "pyaudio>=0.2.13",
        "requests>=2.31.0",
        "psutil>=5.9.6",
        "numpy>=1.24.0",
        "scipy>=1.11.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pluto=src.orchestrator:main",
        ],
    },
)
