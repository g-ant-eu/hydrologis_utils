from setuptools import find_packages, setup

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setup(
    name='hydrologis_utils',
    packages=find_packages(include=['hydrologis_utils']),
    version='0.1.0',
    description='HydroloGIS Utils Library.',
    author='Andrea Antonello',
    license='MIT',
    install_requires=[],#install_requires,
)