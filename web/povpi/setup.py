from setuptools import setup, find_packages

setup(
    name='povpi',
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)
