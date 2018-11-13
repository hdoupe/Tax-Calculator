Tax-Calculator Public API
=========================

The Tax-Calculator's core capabilities are in the Python package
called taxcalc, the source code for which is located in the
tax-calculator/taxcalc directory tree.

Here we provide a high-level view of the **public API** of the taxcalc
conda package with links to the source code.  This high-level view is
organized around the modules in the taxcalc package.  Below is a list
of the taxcalc package modules (in alphabetical order) with
documentation about how to call each public class method and function.
There is also a link to the source code for each documented member.
However, it may be more convenient to access this list interactively
via the **alphabetical** :ref:`genindex` **of taxcalc members**.

**Developers who want to use Tax-Calculator capabilities in their own
projects should restrict themselves to using this public API.  All
other Tax-Calculator members are private and subject to change without
advance notice.**

taxcalc.Behavior
----------------

.. autoclass:: taxcalc.Behavior
   :members:
   :exclude-members: _validate_elasticity_values

taxcalc.Calculator
------------------

.. autoclass:: taxcalc.Calculator
   :members:
   :exclude-members: _calc_one_year, _taxinc_to_amt

taxcalc.cli.tc
--------------

.. automodule:: taxcalc.cli.tc
   :members:
   :exclude-members: _compare_test_output_files, _write_test_input_output_files

taxcalc.Consumption
-------------------

.. autoclass:: taxcalc.Consumption
   :members:

taxcalc.decorators
------------------

.. automodule:: taxcalc.decorators
   :members:

taxcalc.functions
-----------------

.. automodule:: taxcalc.functions
   :members:

taxcalc.Growdiff
----------------

.. autoclass:: taxcalc.Growdiff
   :members:

taxcalc.Growfactors
-------------------

.. autoclass:: taxcalc.Growfactors
   :members:

taxcalc.Parameters
------------------

.. autoclass:: taxcalc.Parameters
   :members:
   :exclude-members: _update, _indexing_rates_for_update

taxcalc.Policy
--------------

.. autoclass:: taxcalc.Policy
   :members:

taxcalc.Records
---------------

.. autoclass:: taxcalc.Records
   :members:
   :exclude-members: _adjust, _blowup, _read_adjust, _read_data, _read_weights

taxcalc.TaxCalcIO
-----------------

.. autoclass:: taxcalc.TaxCalcIO
   :members:

taxcalc.tbi.tbi
-------------------

.. automodule:: taxcalc.tbi.tbi
   :members:

taxcalc.utils
-------------

.. automodule:: taxcalc.utils
   :members:
