#!/usr/bin/python3

from setuptools import setup, find_packages
import io

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

with io.open('requirements.txt') as f:
    required = f.readlines()

setup(
    name='SafeMyWork',
    version='0.6.0',
    description='Autosave your work',
    long_description=readme,
    author='Thykof',
    author_email='nathan.seva@outlook.fr',
    url='https://github.com/Thykof/SafeMyWork',
    setup_requires='pytest-runner',
    tests_require='pytest',
    install_requires=required,
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Environment :: X11 Applications :: GTK'
    ],
)

# run tests: python3 -m pytest
# or python3 setup.py test
