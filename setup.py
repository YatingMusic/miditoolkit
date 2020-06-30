from setuptools import setup, find_packages

setup(
    name='miditoolkit',
    version='0.1.14',
    description='',
    author='wayne391',
    author_email='s101062219@gmail.com',
    url='https://github.com/YatingMusic/miditoolkit',
    packages=find_packages(),
    package_data={'': ['examples_data/*']},
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
    ],
    keywords='music midi mir',

    license='MIT',
    install_requires=[
        'numpy >= 1.7.0',
        'mido >= 1.1.16',
    ]
)


"""
python setup.py sdist
twine upload dist/*
"""