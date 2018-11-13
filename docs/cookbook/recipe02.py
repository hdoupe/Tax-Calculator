from taxcalc import *
import behresp

# use publicly-available CPS input file
recs = Records.cps_constructor()

# specify baseline Calculator object representing current-law policy
pol = Policy()
calc1 = Calculator(policy=pol, records=recs)

cyr = 2020

# calculate aggregate current-law income tax liabilities for cyr
calc1.advance_to_year(cyr)
calc1.calc_all()
itax_rev1 = calc1.weighted_total('iitax')

# read JSON reform file
reform_filename = './ingredients/reformA.json'
params = Calculator.read_json_param_objects(reform=reform_filename,
                                            assump=None)

# specify Calculator object for static analysis of reform policy
pol.implement_reform(params['policy'])
calc2sa = Calculator(policy=pol, records=recs)

# calculate reform income tax liabilities for cyr under static assumptions
calc2sa.advance_to_year(cyr)
calc2sa.calc_all()
itax_rev2sa = calc2sa.weighted_total('iitax')

# specify behavioral-response assumptions
behresp_json = '{"BE_sub": {"2018": 0.25}}'
behresp_dict = Calculator.read_json_assumptions(behresp_json)

# specify Calculator object for analysis of reform with behavioral response
calc2br = Calculator(policy=pol, records=recs)
calc2br.advance_to_year(cyr)
_, df2br = behresp.response(calc1, calc2br, behresp_dict)

# calculate reform income tax liabilities for cyr with behavioral response
itax_rev2br = (df2br['iitax'] * df2br['s006']).sum()

# print total income tax revenue estimates for cyr
# (estimates in billons of dollars rounded to nearest hundredth of a billion)
print('{}_CURRENT_LAW_P__itax_rev($B)= {:.2f}'.format(cyr, itax_rev1 * 1e-9))
print('{}_REFORM_STATIC__itax_rev($B)= {:.2f}'.format(cyr, itax_rev2sa * 1e-9))
print('{}_REFORM_DYNAMIC_itax_rev($B)= {:.2f}'.format(cyr, itax_rev2br * 1e-9))
