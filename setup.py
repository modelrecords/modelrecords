from setuptools import setup, find_packages

setup(
    name="modelrecords",
    version="1.0.0",
    package_data = {"": ["*.yaml", "*.yml"]},
    include_package_data = True,
    packages=find_packages(where="modelrecords"),
    install_requires=[
        "pyyaml",
        "omegaconf",
        "jinja2",
        "semantic_version",
        "requests",
        "pypdf",
    ],
    entry_points={
        "console_scripts": [
            "main-cli=modelrecords.main:main",
            "analyze-cli=analyzer.main:main",
        ],
    },
)
