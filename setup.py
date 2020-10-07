#!/usr/bin/env python
"""The setup script."""
from setuptools import setup, find_packages

with open("testspace/__init__.py", "r") as handle:
    for line in handle:
        if "__version__" in line:
            version = line.split(" = ")[-1].strip('"')
            break

with open("./README.md", "r") as handle:
    readme_text = handle.read()

with open("./requirements.txt", "r") as handle:
    requirements = [lr.strip() for lr in handle.read().splitlines() if lr.strip()]

with open("./requirements_dev.txt", "r") as handle:
    requirements_dev = [lv.strip() for lv in handle.read().splitlines() if lv.strip()]

with open("./requirements_doc.txt", "r") as handle:
    requirements_doc = [ld.strip() for ld in handle.read().splitlines() if ld.strip()]

setup(
    name="testspace-python",
    version="0.1.1",
    description="Library to use Testspace API and client.",
    long_description=readme_text,
    long_description_content_type="text/markdown",
    author="Jeffrey Schultz",
    author_email="jschultz8960@yahoo.com",
    url=("https://github.com/" "s2technologies/testspace-python"),
    license="MIT",
    packages=find_packages(),
    # include anything specified in Manifest.in
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "code_style": ["flake8<3.8.0,>=3.7.0", "black", "pre-commit==1.17.0"],
        "testing": requirements_dev,
        "docs": requirements_doc,
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="",
)
