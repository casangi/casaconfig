config.py
====================

Each modular CASA 6 package as well as the full monolithic installation reads a single **config.py** configuration file
to setup the CASA runtime options. A default config.py is included within the casaconfig package.
This default config.py provides automatic initial population and daily maintenance of casaconfig data tables,
and defines the allowable configuration settings for the CASA runtime.

This file will be loaded unless the user places their own version in
their home area .casa folder (**\~/.casa**) prior to starting the casa installation or importing the packages into a standard
python environment for the first time.

.. warning:: Users must ensure they have an up-to-date config.py in their ~/.casa directory (or delete it to utilize the default). Use write_default_config() to update.


**default config.py settings:**

.. include:: ../casaconfig/config.py
   :literal:
