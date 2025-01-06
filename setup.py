from setuptools import setup

setup(
    name="smrtclk",
    version="0.1.0",
    packages=["smrtclk"],
    install_requires=[
        "python-dotenv",
        "PyQt5",
        "requests",
        "pytest",
        "black",
    ],
)
