"""
Setup file for clotho package
"""
from setuptools import (
    setup,
    find_packages,
)


PACKAGES = find_packages()


setup(
    name='gi-releaser',
    version='0.0.1',
    description='Release script for bumping git tag and create commit',
    url='',
    author='André Engström',
    author_email='anmien89@gmail.com',
    license='GNU GPL',
    packages=PACKAGES,
    install_requires=[
        'GitPython',
    ],
    zip_safe=False,
)
