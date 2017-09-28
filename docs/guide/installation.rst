Installation
============

These instructions have only been tested on the `lxplus`_ and `cmslpc`_
computing clusters, so feel free to submit an issue if it doesn't work for you.

.. _lxplus: http://information-technology.web.cern.ch/services/lxplus-service
.. _cmslpc: http://www.uscms.org/uscms_at_work/physics/computing/getstarted/uaf.shtml

Prerequisites
-------------

vhbbtools is meant to be integrated with a CMSSW release and, currently, only
those releases that distribute Python 2.7 are officially supported.

To prepare the installation, checkout a CMSSW release, set up its runtime
environment, and then create and activate a Python virtual environment that
points to its Python interpreter:

.. code-block:: bash

   cmsrel CMSSW_X_Y_Z
   cd CMSSW_X_Y_Z/src
   cmsenv
   virtualenv --python "$(which python)" venv
   source venv/bin/activate

The virtual environment is needed to ensure that vhbbtools and its dependencies
are accessible to the correct Python interpeter and do not contaminate the
system Python's site-packages.

The virtual environment is deactivated by the command:

.. code-block:: bash

   deactivate

and reactivated by the commands:

.. code-block:: bash

   cmsenv # If the runtime environment hasn't been set
   source venv/bin/activate

Install from PyPI (Recommended)
-------------------------------

Once the virtual environment is ready, install the package using pip:

.. code-block:: bash

   pip install vhbbtools

Install from Source
-------------------

Once the virtual environment is ready, clone the repository:

.. code-block:: bash

   git clone git@github.com:swang373/vhbbtools.git

and then change to the vhbbtools directory and run the installer:

.. code-block:: bash

   cd vhbbtools
   python setup.py install

Check Installation
------------------

.. highlight:: python

If the installation succeeded, you should be able to import
the package::

>>> import vhbbtools
>>> help(vhbbtools)

Eventually, a script will be provided to run a suite of unit tests.

