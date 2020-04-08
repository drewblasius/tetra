#!/usr/bin/env python

"""The setup script."""

import configparser
from setuptools import find_packages, setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()


config = configparser.ConfigParser()
config.read('setup.cfg')

setup(
    author="Ryan Culligan",
    author_email='rrculligan@gmail.com',
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="message queue",
    entry_points={'console_scripts': ['tetra=tetra.cli:main',],},  # NOQA E231
    license="MIT license",
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    install_requires=config['options']['install_requires'],
    setup_requires=config['options']['setup_requires'],
    keywords='tetra',
    name='tetra',
    packages=find_packages(include=['tetra', 'tetra.*']),
    url='https://github.com/TheCulliganMan/tetra',
    version='0.1.0',
    zip_safe=False,
)
