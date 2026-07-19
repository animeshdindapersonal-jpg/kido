"""KIDO — A real programming language for kids (production package)."""

from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="kido",
    version="1.1.0",
    description="KIDO - A Real Programming Language for Kids",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="KIDO Team",
    license="MIT",
    packages=find_packages(exclude=["tests", "tests.*", "stress_tests", "examples"]),
    include_package_data=True,
    install_requires=[],
    extras_require={
        "dev": ["pytest>=7.0.0"],
        "build": ["pyinstaller>=5.0.0", "wheel>=0.37.0", "setuptools>=45.0.0"],
    },
    entry_points={
        "console_scripts": [
            "kido=kido_cli.cli:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Topic :: Education",
        "Topic :: Software Development :: Interpreters",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    keywords="kids education programming language interpreter kido",
    project_urls={
        "Documentation": "https://github.com/animeshdindapersonal-jpg/kido",
        "Source": "https://github.com/animeshdindapersonal-jpg/kido",
    },
)
