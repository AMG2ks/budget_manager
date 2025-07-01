"""
Setup configuration for the Smart Budget Manager.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="smart-budget-manager",
    version="1.0.0",
    author="Budget Manager Team",
    author_email="contact@budgetmanager.com",
    description="A smart and flexible budget management application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/budget-manager",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Accounting",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "budget-manager=budget_manager.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 