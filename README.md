# casaconfig
Runtime data necessary for CASA operation.

- [latest casaconfig API on casadocs](https://casadocs.readthedocs.io/en/latest/api/casaconfig.html)
- [stable casaconfig API on casadocs](https://casadocs.readthedocs.io/en/stable/api/casaconfig.html)
      

## Release Instructions
1. Create a release branch with a version name (ie v1.6.2)
2. Ensure the version number in pyproject.toml on the branch is set correctly
3. Create a tag of the release branch (ie v1.6.2-1)
4. Github Action runs automatically to publish a pip package to pypi

## Installation

```
$: pip install casaconfig
```

## Usage

See the casaconfig API documentation on casadocs (links above).

Also see the External Data section of casadocs for additional details

- [latest External Data section on casadocs](https://casadocs.readthedocs.io/en/latest/notebooks/external-data.html)
- [stable External Data section on casadocs](https://casadocs.readthedocs.io/en/stable/notebooks/external-data.html)

## Developers Instructions
1. every push to the casaconfig repository will push a new wheel to [test pypi](https://test.pypi.org/project/casaconfig/#history)
2. the version in pyproject.toml must be updated before each push so that the wheel has a unique name (e.g. "1.2.3dev2", where "dev?" could be incremented during development; see the [specification](https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers) for more information about valid version signifiers)
3. When testing with a casatools build, "pip install" the development casaconfig wheel before running any tests - it may be installed before casatools is installed or after since the casatools build does not depend on casasconfig (uninstall any already installed casaconfig if necessary).
4. For release, follow the above instructions.

Wheels can be built locally following the same process used by the CI actions. To install the build-system dependencies as defined in pyproject.toml and then generate a source distribution and wheel:
```
python3 -m pip install build setuptools --user
python3 -m build
```
This will create:
```
casaconfig.egg-info
├── PKG-INFO
├── SOURCES.txt
├── dependency_links.txt
├── requires.txt
└── top_level.txt
dist
├── casaconfig-[VERSION]-py3-none-any.whl
└── casaconfig-[VERSION].tar.gz
```

### Setting up CASA branches for casaconfig development

The casaconfig build process publishes test wheels to test.pypi.org

In order to test these with Casa packages, two changes are needed in the casa6 repository branch.

1) Add a line to casa6/build.conf with the appropriate wheel version. For example:

```
casaconfig==1.0.3.dev2
```
2) Add the following line with the apppropriate branch name to casa6/casatools/setup.py

```
META_DATA["install_requires"] = "casaconfig@git+https://github.com/casangi/casaconfig@CAS-14512"
```

This adds the casaconfig branch as a casatools install time dependency. It will not use the wheel, but rather build the branch in place. This is required in order to avoid adding test.pypi.org as a pip extra-index-url, which might cause other development packages to be installed inadvertently. Note that casaconfig dependency is typically defined in setup.cfg, but the syntax above does not work with setup.cfg. 


### Preparing the casa6 branch for merge

1) Merge the casaconfig branch to main and create a wheel
2) Update casa6/build.conf to use that wheel
3) Comment out the extra "install_requires" line from setup.py
