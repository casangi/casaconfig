from setuptools import setup, find_packages
from glob import glob

with open('README.md', "r") as fid:   #encoding='utf-8'
    long_description = fid.read()

setup(
    name='casadata',
    version='0.0.1rc3',
    description='CASA Operational Data Package',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='National Radio Astronomy Observatory',
    author_email='casa-feedback@nrao.edu',
    url='https://github.com/casangi/casadata',
    license='Apache-2.0',
    packages=find_packages(),
    include_package_data=True,
    #data_files = [
    #    ('casadata/data', glob('casadata/data/**/*', recursive=True)), # recursive
    #],
    install_requires=['cngi-prototype==0.0.90']
)
