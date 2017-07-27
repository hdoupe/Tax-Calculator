from taxcalc.records import Records
from taxcalc.calculate import Calculator
from taxcalc.policy import Policy
from taxcalc.utils import multiyear_diagnostic_table
import pandas as pd
import numpy as np
import json


def format_reform(reform):
    formatted = {"policy": {}}
    for param in reform:
        formatted["policy"][param] = {"2017": reform[param]}

    return formatted

def get_default_reform():
    dd = Policy.default_data(metadata=False, start_year=2017)

    reform = format_reform(dd)

    with open('default_reform_noindent.json', 'w') as js:
        js.write(json.dumps(reform))#, indent=4))

    return reform

def test(dd_path="default_reform.json"):
    puf = pd.read_csv("puf.csv")

    rec_1= Records(data=puf)
    pol_1 = Policy()
    calc_1 = Calculator(records = rec_1, policy = pol_1)

    rec_2= Records(data=puf)
    pol_2 = Policy()
    calc_2 = Calculator(records=rec_2, policy=pol_2)
    formatted = calc_2.read_json_param_files("default_reform.json", None)
    pol_2.implement_reform(formatted["policy"])

    res1 = multiyear_diagnostic_table(calc_1, num_years = 8)
    res2 = multiyear_diagnostic_table(calc_2, num_years = 8)

    diff = res1 - res2
    i, j = len(res1), len(res1.columns)
    assert(np.allclose(diff, np.zeros(i * j).reshape(i, j)))


def test_params(reform, default=False):
    with open("taxcalc/current_law_policy.json", 'r') as js:
        clp = json.loads(js.read())

    puf = pd.read_csv("puf.csv")
    rec_1= Records(data=puf)
    pol_1 = Policy()
    calc_1 = Calculator(records = rec_1, policy = pol_1)
    calc_1.advance_to_year(2017)
    calc_1.calc_all()
    combined1 = (rec_1.combined * rec_1.s006).sum()

    dd = get_default_reform()["policy"]
    success = []
    fail = []
    nochange = []
    inc_taxes = {"policy": {}}
    dec_taxes = {"policy": {}}
    for param in reform:
        v_dd, v_ref = dd[param]["2017"], reform[param]["2017"]
        if not np.allclose(v_dd, v_ref):
            new_reform = {2017: {param: v_ref}}
            rec_ref = Records(data=puf)
            pol_ref = Policy()
            calc_ref = Calculator(records=rec_ref, policy=pol_ref)
            pol_ref.implement_reform(new_reform)

            calc_ref.advance_to_year(2017)
            calc_ref.calc_all()
            combined_ref = (rec_ref.combined * rec_ref.s006).sum()

            rel = (combined_ref-combined1)/combined1
            if combined_ref < combined1:
                print(param, v_dd, v_ref, rel)
                fail.append((param, v_dd, v_ref, rel))
                dec_taxes["policy"][param] = reform[param]
                if default:
                    inc_taxes["policy"][param] = dd[param]
            else:
                success.append((param, v_dd, v_ref, rel))
                inc_taxes["policy"][param] = reform[param]
                if default:
                    dec_taxes["policy"][param] = dd[param]

        else:
            nochange.append((param, clp[param]["section_1"]))
            print(param, clp[param]["section_1"])

    print("FAIL")
    print(fail)
    print('\n\n\n\n')
    print("NOCHANGE")
    print(nochange)

    print('\n\n\n\n')
    print("SUCCESS")
    print(success)

    return (inc_taxes, dec_taxes)


if __name__=="__main__":
    # with open('test_reform.json', 'r') as js:
    #     reform = json.loads(js.read())
    # inc_taxes, dec_taxes = test_params(reform["policy"], default=True)
    #
    # with open("test_reform_inc_taxes_with_default.json", "w") as js:
    #     js.write(json.dumps(inc_taxes, indent=4))
    # with open("test_reform_dec_taxes_with_default.json", "w") as js:
    #     js.write(json.dumps(dec_taxes, indent=4))
    #
    # inc_taxes, dec_taxes = test_params(reform["policy"], default=False)
    #
    # with open("test_reform_inc_taxes.json", "w") as js:
    #     js.write(json.dumps(inc_taxes, indent=4))
    # with open("test_reform_dec_taxes.json", "w") as js:
    #     js.write(json.dumps(dec_taxes, indent=4))


    with open('test_reform_inc_taxes.json', 'r') as js:
        reform = json.loads(js.read())
    inc_taxes, dec_taxes = test_params(reform["policy"], default=True)

    with open('test_reform_dec_taxes.json', 'r') as js:
        reform = json.loads(js.read())
    inc_taxes, dec_taxes = test_params(reform["policy"], default=True)
