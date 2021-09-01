from setuptools import setup, find_packages
from glob import glob

with open('README.md', "r") as fid:   #encoding='utf-8'
    long_description = fid.read()

setup(
    name='casadata',
    version='0.0.1rc18',
    description='CASA Operational Data Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='National Radio Astronomy Observatory',
    author_email='casa-feedback@nrao.edu',
    url='https://github.com/casangi/casadata',
    license='Apache-2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=['xarray>=0.16.2',
                      'numpy>=1.19.5',
                      'python-casacore>=3.4.0',
                      'GitPython>=3.1.18']
)
