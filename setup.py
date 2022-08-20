"""
This file is internal for creating a proper package.

Build package with `python3 setup.py sdist bdist_wheel`
Upload with `python3 -m twine upload dist/aemeasure-X.X.X-py3-none-any.whl `

"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="aemeasure",
    version="0.2.6",
    author="TU Braunschweig, IBR, Algorithms Group (Dominik Krupke)",
    author_email="krupke@ibr.cs.tu-bs.de",
    description="Simple tools for logging experiments in algorithm engineering",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/d-krupke/AeMeasure",
    packages=[p for p in setuptools.find_packages() if "aemeasure" in p],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
    ],
    python_requires=">=3.6",
    install_requires=["pandas"],
)
