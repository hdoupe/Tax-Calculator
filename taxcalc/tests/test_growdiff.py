# CODING-STYLE CHECKS:
# pycodestyle test_growdiff.py

import os
import json
import numpy as np
import pytest
from taxcalc import GrowDiff, GrowFactors, Policy


def test_year_consistency():
    assert GrowDiff.JSON_START_YEAR == Policy.JSON_START_YEAR
    assert GrowDiff.DEFAULT_NUM_YEARS == Policy.DEFAULT_NUM_YEARS


def test_update_and_apply_growdiff():
    gdiff = GrowDiff()
    # update GrowDiff instance
    diffs = {2014: {'_AWAGE': [0.01]},
             2016: {'_AWAGE': [0.02]}}
    gdiff.update_growdiff(diffs)
    expected_wage_diffs = [0.00, 0.01, 0.01, 0.02, 0.02] + [0.02]*10
    assert np.allclose(gdiff._AWAGE, expected_wage_diffs, atol=0.0, rtol=0.0)
    # apply growdiff to GrowFactors instance
    gf = GrowFactors()
    syr = GrowDiff.JSON_START_YEAR
    nyrs = GrowDiff.DEFAULT_NUM_YEARS
    lyr = syr + nyrs - 1
    pir_pre = gf.price_inflation_rates(syr, lyr)
    wgr_pre = gf.wage_growth_rates(syr, lyr)
    gfactors = GrowFactors()
    gdiff.apply_to(gfactors)
    pir_pst = gfactors.price_inflation_rates(syr, lyr)
    wgr_pst = gfactors.wage_growth_rates(syr, lyr)
    expected_wgr_pst = [wgr_pre[i] + expected_wage_diffs[i]
                        for i in range(0, nyrs)]
    assert np.allclose(pir_pre, pir_pst, atol=0.0, rtol=0.0)
    assert np.allclose(wgr_pst, expected_wgr_pst, atol=1.0e-9, rtol=0.0)


def test_incorrect_update_growdiff():
    with pytest.raises(ValueError):
        GrowDiff().update_growdiff([])
    with pytest.raises(ValueError):
        GrowDiff().update_growdiff({'xyz': {'_ABOOK': [0.02]}})
    with pytest.raises(ValueError):
        GrowDiff().update_growdiff({2012: {'_ABOOK': [0.02]}})
    with pytest.raises(ValueError):
        GrowDiff().update_growdiff({2052: {'_ABOOK': [0.02]}})
    with pytest.raises(ValueError):
        GrowDiff().update_growdiff({2014: {'_MPC_exxxxx': [0.02]}})
    with pytest.raises(ValueError):
        GrowDiff().update_growdiff({2014: {'_ABOOK': [-1.1]}})


def test_has_any_response():
    start_year = GrowDiff.JSON_START_YEAR
    gdiff = GrowDiff()
    assert gdiff.current_year == start_year
    assert gdiff.has_any_response() is False
    gdiff.update_growdiff({2020: {'_AWAGE': [0.01]}})
    assert gdiff.current_year == start_year
    assert gdiff.has_any_response() is True


def test_description_punctuation(tests_path):
    """
    Check that each description ends in a period.
    """
    # read JSON file into a dictionary
    path = os.path.join(tests_path, '..', 'growdiff.json')
    with open(path, 'r') as jsonfile:
        dct = json.load(jsonfile)
    all_desc_ok = True
    for param in dct.keys():
        if not dct[param]['description'].endswith('.'):
            all_desc_ok = False
            print('param,description=',
                  str(param),
                  dct[param]['description'])
    assert all_desc_ok


def test_boolean_value_infomation(tests_path):
    """
    Check consistency of boolean_value in growdiff.json file.
    """
    # read growdiff.json file into a dictionary
    path = os.path.join(tests_path, '..', 'growdiff.json')
    with open(path, 'r') as gddfile:
        gdd = json.load(gddfile)
    for param in gdd.keys():
        val = gdd[param]['value']
        if isinstance(val, list):
            val = val[0]
            if isinstance(val, list):
                val = val[0]
        valstr = str(val)
        if valstr == 'True' or valstr == 'False':
            val_is_boolean = True
        else:
            val_is_boolean = False
        if gdd[param]['boolean_value'] != val_is_boolean:
            print('param,boolean_value,val,val_is_boolean=',
                  str(param),
                  gdd[param]['boolean_value'],
                  val,
                  val_is_boolean)
            assert gdd[param]['boolean_value'] == val_is_boolean
