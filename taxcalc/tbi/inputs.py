import msgpack, json

import numpy as np

from taxcalc import Policy, Behavior

def get_defaults(start_year, **kwargs):
    pol = Policy()
    pol.set_year(start_year)
    pol_mdata = pol.metadata()
    behv_mdata = Behavior()._vals

    return {"policy": pol_mdata, "behavior": behv_mdata}