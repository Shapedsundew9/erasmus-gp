"""Package configuration for egppy."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="egppkrapi",
    version="1.0.0",
    author="Your Name",
    author_email="your_email@example.com",
    description="A Python package for example purposes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your_username/egppy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.11",
    install_requires=[
        # Add any dependencies required by your package here
    ],
    extras_require={
        "dev": [
            # Add any development dependencies required here
        ]
    },
)
