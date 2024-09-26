# casaconfig
Runtime data necessary for CASA operation.

- [latest casaconfig API on casadocs](https://casadocs.readthedocs.io/en/latest/api/casaconfig.html)
- [stable casaconfig API on casadocs](https://casadocs.readthedocs.io/en/stable/api/casaconfig.html)
      

## Release Instructions
1. Create a release branch with a version name (ie v1.6.2)
2. Ensure the version number in setup.py on the branch is set correctly
3. Create a tag of the release branch (ie v1.6.2-1)
4. Github Action runs automatically to publish a pip package to pypi

## Installation

```
$: pip install casaconfig
```

## Usage

See the casaconfig API documentation on casadocs (links above).

Also see the External Data section of casadocs for additional details

- [latext External Data section on casadocs](https://casadocs.readthedocs.io/en/latest/notebooks/external-data.html)
- [stable External Data section on casadocs](https://casadocs.readthedocs.io/en/latest/notebooks/external-data.html)

## Developers Instructions
1. every push to the casaconfig repository will push a new wheel to [test pypi](https://test.pypi.org/project/casaconfig/#history)
2. the version in setup.py must be updated before each push so that the wheel has a unique name (e.g. "1.2.3dev2", where "dev?" could be incremented during development)
3. When testing with a casatools build, "pip install" the development casaconfig wheel before running any tests - it may be installed before casatools is installed or after since the casatools build does not depend on casasconfig (uninstall any already installed casaconfig if necessary).
4. For release, follow the above instructions.
