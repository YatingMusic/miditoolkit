from setuptools import setup, find_packages


extras = {
    "tests": [
        "setuptools",
        "flake8",
        "pytest-cov",
        "pytest-xdist[psutil]",
        "tqdm",
    ]
}

setup(
    name="miditoolkit",
    version="1.0.0",
    description="A python package for working with MIDI data files.",
    author="wayne391",
    author_email="s101062219@gmail.com",
    url="https://github.com/YatingMusic/miditoolkit",
    packages=find_packages(exclude=("tests",)),
    package_data={"": ["examples_data/*"]},
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
    ],
    keywords="music midi mir",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    extras_require=extras,
    python_requires=">=3.7.0",
    install_requires=[
        "numpy >= 1.19",
        "mido >= 1.1.16",
        "matplotlib",
    ],
)


"""
python setup.py sdist
twine upload dist/*
"""
