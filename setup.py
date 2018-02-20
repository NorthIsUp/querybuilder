#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'enum34',
    'six',
    'cached-property',
]

setup_requirements = [
    'pytest-runner',
]

setup(
    name='jqueryquerybuilder',
    version='0.2.0',
    description="Generator and Parser for the jQuery Query Builder library.",
    long_description=readme + '\n\n' + history,
    author="Adam Hitchcock",
    author_email='adam@northisup.com',
    url='https://github.com/NorthIsUp/querybuilder',
    packages=find_packages(include=['querybuilder']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='querybuilder',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    setup_requires=setup_requirements,
)
