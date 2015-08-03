#!/usr/bin/env python
import os
from setuptools import setup


def get_readme():
    return open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    name='ballotbleach',
    version='0.1.0',
    description="Simple data quality tools for online vote data.",
    long_description=get_readme(),
    license="MIT",
    author="Julio Gonzalez Altamirano",
    author_email='devjga@gmail.com',
    url='https://github.com/jga/ballotbleach',
    keywords="elections ballot voting data quality",
    packages=['ballotbleach'],
    install_requires=['click', 'xlrd'],
    entry_points={
        'console_scripts': [
            'ballotbleach=ballotbleach.core:run',
        ],
    },
    platforms=['any'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ]
)