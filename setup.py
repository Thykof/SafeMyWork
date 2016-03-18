# -*- coding: utf-8 -*-

from setuptools import find_packages
try:
    from cx_Freeze import setup, Executable
except ImportError:
    from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    executables = [Executable("SafeMyWork.py")],
    name='SafeMyWork',
    version='0.2',
    description='Little app to save your work.',
    long_description=readme,
    author='Thykof',
    author_email='nathan.seva@outlook.fr',
    url='https://github.com/Thykof/SafeMyWork',
    setup_requires='pytest-runner',
    tests_require='pytest',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'
    ],
)
