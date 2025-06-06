from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="taskmanager-cli",
    version="0.1.0",
    author="Daniel Kim",
    author_email="daniel@example.com",
    description="A powerful CLI task manager with Linear integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/danielkim/task-manager-cli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "task=taskmanager.cli:cli",
            "taskmanager=taskmanager.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "taskmanager": ["templates/*", "data/*"],
    },
)