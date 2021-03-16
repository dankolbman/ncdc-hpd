import setuptools

setuptools.setup(
    name="Precipitation Calculator",
    version="1.0.0",
    author="Dan",
    description="Precipitation tools",
    packages=setuptools.find_packages(),
    python_requires=">=3.9",
    install_requires=["pandas"],
)
