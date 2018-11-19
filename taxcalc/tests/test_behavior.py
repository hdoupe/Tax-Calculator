# CODING-STYLE CHECKS:
# pycodestyle test_behavior.py

import os
import json
import numpy as np
import pytest
from taxcalc import Policy, Records, Calculator, Behavior


def test_incorrect_behavior_instantiation():
    with pytest.raises(ValueError):
        Behavior(start_year=2000)
    with pytest.raises(ValueError):
        Behavior(num_years=0)
    with pytest.raises(FloatingPointError):
        np.divide(1., 0.)


def test_behavioral_response_calculator(cps_subsample):
    # create Records object
    rec = Records.cps_constructor(data=cps_subsample)
    year = rec.current_year
    # create Policy object
    pol = Policy()
    # create current-law Calculator object
    calc1 = Calculator(policy=pol, records=rec)
    # implement policy reform
    reform = {year: {'_II_rt7': [0.496],
                     '_PT_rt7': [0.496]}}
    pol.implement_reform(reform)
    # create reform Calculator object with no behavioral response
    behv = Behavior()
    calc2 = Calculator(policy=pol, records=rec, behavior=behv)
    # test incorrect use of Behavior._mtr12 method
    with pytest.raises(ValueError):
        Behavior._mtr12(calc1, calc2, mtr_of='e00200p', tax_type='nonsense')
    # vary substitution and income effects in Behavior object
    behavior0 = {year: {'_BE_sub': [0.0],
                        '_BE_cg': [0.0]}}
    behv0 = Behavior()
    behv0.update_behavior(behavior0)
    calc2 = Calculator(policy=pol, records=rec, behavior=behv0)
    assert calc2.behavior_has_response() is False
    calc2_behv0 = Behavior.response(calc1, calc2)
    behavior1 = {year: {'_BE_sub': [0.3], '_BE_inc': [-0.1], '_BE_cg': [0.0]}}
    behv1 = Behavior()
    behv1.update_behavior(behavior1)
    calc2 = Calculator(policy=pol, records=rec, behavior=behv1)
    assert calc2.behavior_has_response() is True
    epsilon = 1e-9
    assert abs(calc2.behavior('BE_sub') - 0.3) < epsilon
    calc2.behavior('BE_sub', 0.3)
    assert abs(calc2.behavior('BE_sub') - 0.3) < epsilon
    assert abs(calc2.behavior('BE_inc') - -0.1) < epsilon
    assert abs(calc2.behavior('BE_cg') - 0.0) < epsilon
    calc2_behv1 = Behavior.response(calc1, calc2)
    behavior2 = {year: {'_BE_sub': [0.5], '_BE_cg': [-0.8]}}
    behv2 = Behavior()
    behv2.update_behavior(behavior2)
    calc2 = Calculator(policy=pol, records=rec, behavior=behv2)
    assert calc2.behavior_has_response() is True
    calc2_behv2 = Behavior.response(calc1, calc2, trace=True)
    behavior3 = {year: {'_BE_inc': [-0.2], '_BE_cg': [-0.8]}}
    behv3 = Behavior()
    behv3.update_behavior(behavior3)
    calc2 = Calculator(policy=pol, records=rec, behavior=behv3)
    assert calc2.behavior_has_response() is True
    calc2_behv3 = Behavior.response(calc1, calc2)
    behavior4 = {year: {'_BE_cg': [-0.8]}}
    behv4 = Behavior()
    behv4.update_behavior(behavior4)
    calc2 = Calculator(policy=pol, records=rec, behavior=behv4)
    assert calc2.behavior_has_response() is True
    calc2_behv4 = Behavior.response(calc1, calc2)
    # check that total income tax liability differs across the
    # five sets of behavioral-response elasticities
    assert (calc2_behv0.weighted_total('iitax') !=
            calc2_behv1.weighted_total('iitax') !=
            calc2_behv2.weighted_total('iitax') !=
            calc2_behv3.weighted_total('iitax') !=
            calc2_behv4.weighted_total('iitax'))


def test_correct_update_behavior():
    beh = Behavior(start_year=2013)
    beh.update_behavior({2014: {'_BE_sub': [0.5]},
                         2015: {'_BE_cg': [-1.2]}})
    should_be = np.full((Behavior.DEFAULT_NUM_YEARS,), 0.5)
    should_be[0] = 0.0
    assert np.allclose(beh._BE_sub, should_be, rtol=0.0)
    assert np.allclose(beh._BE_inc,
                       np.zeros((Behavior.DEFAULT_NUM_YEARS,)),
                       rtol=0.0)
    beh.set_year(2017)
    assert beh.current_year == 2017
    assert beh.BE_sub == 0.5
    assert beh.BE_inc == 0.0
    assert beh.BE_cg == -1.2


def test_incorrect_update_behavior():
    with pytest.raises(ValueError):
        Behavior().update_behavior([])
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_inc': [+0.2]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_sub': [-0.2]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_cg': [+0.8]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_xx': [0.0]}})
    with pytest.raises(ValueError):
        Behavior().update_behavior({2013: {'_BE_xx_cpi': [True]}})
    # year in update must be greater than or equal start year
    with pytest.raises(ValueError):
        Behavior(start_year=2014).update_behavior({2013: {'_BE_inc': [-0.2]}})
    # year in update must be greater than or equal to current year
    with pytest.raises(ValueError):
        behv = Behavior(start_year=2014)
        behv.set_year(2015)
        behv.update_behavior({2014: {'_BE_inc': [-0.2]}})
    # start year greater than start_year + DEFAULT_NUM_YEARS
    with pytest.raises(ValueError):
        Behavior().update_behavior({2040: {'_BE_inc': [-0.2]}})
    # invalid start year
    with pytest.raises(ValueError):
        Behavior().update_behavior({'notayear': {'_BE_inc': [-0.2]}})


def test_validate_param_names_types_errors():
    behv0 = Behavior()
    specs0 = {2020: {'_BE_bad': [-1.0]}}
    with pytest.raises(ValueError):
        behv0.update_behavior(specs0)
    behv1 = Behavior()
    specs1 = {2019: {'_BE_inc': [True]}}
    with pytest.raises(ValueError):
        behv1.update_behavior(specs1)


def test_validate_param_values_errors():
    behv0 = Behavior()
    specs0 = {2020: {'_BE_cg': [0.2]}}
    with pytest.raises(ValueError):
        behv0.update_behavior(specs0)
    behv1 = Behavior()
    specs1 = {2022: {'_BE_sub': [-0.2]}}
    with pytest.raises(ValueError):
        behv1.update_behavior(specs1)
    behv2 = Behavior()
    specs2 = {
        2020: {
            '_BE_cg': [-0.2],
            '_BE_sub': [0.3]
        }
    }
    behv2.update_behavior(specs2)


def test_future_update_behavior():
    behv = Behavior()
    assert behv.current_year == behv.start_year
    assert behv.has_response() is False
    assert behv.has_any_response() is False
    cyr = 2020
    behv.set_year(cyr)
    behv.update_behavior({cyr: {'_BE_cg': [-1.0]}})
    assert behv.current_year == cyr
    assert behv.has_response() is True
    behv.set_year(cyr - 1)
    assert behv.has_response() is False
    assert behv.has_any_response() is True


def test_boolean_value_infomation(tests_path):
    """
    Check consistency of boolean_value in behavior.json file.
    """
    # read behavior.json file into a dictionary
    path = os.path.join(tests_path, '..', 'behavior.json')
    with open(path, 'r') as behfile:
        beh = json.load(behfile)
    for param in beh.keys():
        val = beh[param]['value']
        if isinstance(val, list):
            val = val[0]
            if isinstance(val, list):
                val = val[0]
        valstr = str(val)
        if valstr == 'True' or valstr == 'False':
            val_is_boolean = True
        else:
            val_is_boolean = False
        if beh[param]['boolean_value'] != val_is_boolean:
            print('param,boolean_value,val,val_is_boolean=',
                  str(param),
                  beh[param]['boolean_value'],
                  val,
                  val_is_boolean)
            assert beh[param]['boolean_value'] == val_is_boolean
