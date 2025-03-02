from setuptools import setup, find_packages

setup(
    name="crew_server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask>=2.0.0",
        "crewai>=0.1.0",
    ],
) 