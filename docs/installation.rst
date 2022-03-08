Installation
------------

This package is included by default in the `monolithic CASA distribution <https://casadocs.readthedocs.io/en/stable/notebooks/introduction.html#Monolithic-Distribution>`_.
For `modular CASA users <https://casadocs.readthedocs.io/en/stable/notebooks/introduction.html#Modular-Packages>`_, this package is generally installed
automatically as a dependency of casatools.  Manual installation can be accomplished as follows:

::

   $: pip install casaconfig


Usage
-----

The Python package installs with an empty *__data__* subdirectory. The
contents must be populated by calling *pull_data()* to download the tables
from the Github repo *data* folder.

::

   from casaconfig import pull_data
   pull_data()

Within this folder is a stale version of the IERS measures tables needed for accurate measurement.
Generally users will want to update to the latest measures data and keep current each day.

::

   from casaconfig import measures_update
   measures_update()

A default config.py necessary for CASA operation is included in this package. Users may make their
own local copy with any desired modifications.

::

   from casaconfig import write_default_config
   write_default_config('~/.casa/config.py')

