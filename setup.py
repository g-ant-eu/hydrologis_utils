from setuptools import find_packages, setup

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setup(
    name='hydrologis_utils',
    url='https://bitbucket.org/moovida/hydrologis_utils',
    packages=find_packages(include=['hydrologis_utils']),
    version='0.1.0',
    description='HydroloGIS Utils Library.',
    long_description=open('README.md').read(),
    author='Andrea Antonello',
    author_email='andrea.antonello@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GPL3 License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
)