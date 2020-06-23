from setuptools import setup

setup(
    name='miditoolkit',
    version='0.1.9',
    description='',
    author='Colin Raffel',
    author_email='s101062219@gmail.com',
    url='https://github.com/YatingMusic/miditoolkit',
    packages=['miditoolkit'],
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