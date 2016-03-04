# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='SafeMyWork',
    version='0.1',
    description='Little app to save your work.',
    long_description=readme,
    author='Thykof',
    author_email='nathan.seva@outlook.fr',
    url='https://github.com/Thykof/SafeMyWork',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
)
