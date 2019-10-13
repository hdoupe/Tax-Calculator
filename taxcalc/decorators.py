"""
Implement numba JIT decorators used to speed-up the execution
of Tax-Calculator functions in the calcfunctions.py module.
"""
# CODING-STYLE CHECKS:
# pycodestyle decorators.py
# pylint --disable=locally-disabled decorators.py

import os
import io
import ast
import inspect
from functools import partial
import numba
import pandas as pd
import dask.dataframe as dd
import dask.array as da
from dask import delayed
import taxcalc
from taxcalc.policy import Policy
from taxcalc.records import Records


DO_JIT = True
# One way to use the Python debugger is to do these two things:
#  (a) change the line immediately above this comment from
#      "DO_JIT = True" to "DO_JIT = False", and
#  (b) import pdb package and call pdb.set_trace() in either the
#      calculator.py or calcfunctions.py file.


def id_wrapper(*dec_args, **dec_kwargs):  # pylint: disable=unused-argument
    """
    Function wrapper when numba package is not being used during debugging.
    """
    def wrap(fnc):
        """
        wrap function nested in id_wrapper function.
        """
        def wrapped_f(*args, **kwargs):
            """
            wrapped_f function nested in wrap function.
            """
            return fnc(*args, **kwargs)
        return wrapped_f
    return wrap


if DO_JIT is False or 'NOTAXCALCJIT' in os.environ:
    JIT = id_wrapper
else:
    JIT = numba.jit


class GetReturnNode(ast.NodeVisitor):
    """
    A NodeVisitor to get the return tuple names from a calc-style function.
    """
    def visit_Return(self, node):  # pylint: disable=invalid-name,no-self-use
        """
        visit_Return is used by NodeVisitor.visit method.
        """
        if isinstance(node.value, ast.Tuple):
            return [e.id for e in node.value.elts]
        return [node.value.id]

def ap_func(pol_args, rec_df, out_args, records_signature, jitted_f):
    partialled = partial(jitted_f, **pol_args)

    def to_apply(row):
        res = partialled(**row.to_dict())
        return pd.Series(res, index=out_args)

    meta = [(recvar, records_signature[recvar]) for recvar in out_args]
    result = rec_df.apply(to_apply, axis=1,  meta=meta)
    return result


@delayed
def hl_func(policy, records, pol_args, rec_args, out_args, jitted_f):
    unique_rec_args = list(set(rec_args))
    arr = da.stack([getattr(records, recvar) for recvar in unique_rec_args], axis=1)
    rec_df = dd.from_dask_array(arr, columns=unique_rec_args)
    pol_args = {arg: getattr(policy, arg) for arg in pol_args}
    output = ap_func(pol_args, rec_df, out_args, records.signature(), jitted_f)
    for c in output.columns:
        setattr(records, c, output[c].values)
    return output


def iterate_jit(parameters=None, **kwargs):
    """
    Public decorator for a calc-style function (see calcfunctions.py) that
    transforms the calc-style function into an apply-style function that
    can be called by Calculator class methods (see calculator.py).
    """
    if not parameters:
        parameters = []

    def make_wrapper(func):
        """
        make_wrapper function nested in iterate_jit decorator
        wraps specified func using apply_jit.
        """
        # pylint: disable=too-many-locals
        # Get the input arguments from the function
        in_args = inspect.getfullargspec(func).args
        # Get the numba.jit arguments
        jit_args_list = inspect.getfullargspec(JIT).args + ['nopython']
        kwargs_for_jit = dict()
        for key, val in kwargs.items():
            if key in jit_args_list:
                kwargs_for_jit[key] = val

        src = inspect.getsourcelines(func)[0]

        # Discover the return arguments by walking
        # the AST of the function
        grn = GetReturnNode()
        all_out_args = None
        for node in ast.walk(ast.parse(''.join(src))):
            all_out_args = grn.visit(node)
            if all_out_args:
                break
        if not all_out_args:
            raise ValueError("Can't find return statement in function!")

        if DO_JIT:
            jitted_f = JIT(**kwargs)(func)
        else:
            jitted_f = func

        def wrapper(*args, **kwargs):
            """
            wrapper function nested in make_wrapper function nested
            in iterate_jit decorator.
            """
            policy = args[0]
            records = args[1]
            pol_args = []
            rec_args = []
            for farg in all_out_args + in_args:
                if hasattr(policy, farg):
                    pol_args.append(farg)
                elif hasattr(records, farg):
                    rec_args.append(farg)
                else:
                    raise RuntimeError(f"unknown: {farg}")

            return hl_func(policy, records, pol_args, rec_args, all_out_args, jitted_f)

        return wrapper

    return make_wrapper
