from setuptools import setup, find_packages
from glob import glob

with open('README.md', "r") as fid:   #encoding='utf-8'
    long_description = fid.read()

setup(
    name='casaconfig',
    version='0.0.65',
    description='CASA Operational Configuration Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='National Radio Astronomy Observatory',
    author_email='casa-feedback@nrao.edu',
    url='https://github.com/casangi/casadata',
    license='Apache-2.0',
    packages=find_packages(),
    package_data={'casaconfig': ['__data__/*']},
    include_package_data=True,
    install_requires=['certifi>=2023.5.7']
)
