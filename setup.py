import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="compyle",
    version="0.1.0",
    author="Max Fischer",
    author_email="maxfischer2781@gmail.com",
    description="Toy Language to Python Interpreter/Transpiler",
    long_description=long_description,
    url="https://github.com/maxfischer2781/compyle",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pyparsing', 'attrs'],
)