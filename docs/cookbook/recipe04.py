from taxcalc import *

# use publicly-available CPS input file
recs = Records.cps_constructor()

# specify Calculator object for static analysis of current-law policy
pol = Policy()
calc1 = Calculator(policy=pol, records=recs)

cyr = 2020

# calculate current-law tax liabilities for cyr
calc1.advance_to_year(cyr)
calc1.calc_all()

# calculate marginal tax rate wrt cash charitable giving
(_, _, mtr1) = calc1.mtr('e19800', calc_all_already_called=True,
                         wrt_full_compensation=False)

# read JSON reform file and use (the default) static analysis assumptions
reform_filename = './ingredients/reformB.json'
params = Calculator.read_json_param_objects(reform=reform_filename,
                                            assump=None)

# specify Calculator object for static analysis of reform policy
pol.implement_reform(params['policy'])
calc2 = Calculator(policy=pol, records=recs)

# calculate reform tax liabilities for cyr
calc2.advance_to_year(cyr)
calc2.calc_all()

# calculate marginal tax rate wrt cash charitable giving
(_, _, mtr2) = calc2.mtr('e19800', calc_all_already_called=True,
                         wrt_full_compensation=False)

# extract variables needed for quantity_response utility function
# (note the aftertax price is 1+mtr because mtr wrt charity is non-positive)
vdf = calc1.dataframe(['s006', 'e19800', 'e00200'])
vdf['price1'] = 1.0 + mtr1
vdf['price2'] = 1.0 + mtr2
vdf['atinc1'] = calc1.array('aftertax_income')
vdf['atinc2'] = calc2.array('aftertax_income')

# group filing units into earnings groups with different response elasticities
# (note earnings groups are just an example based on no empirical results)
earnings_bins = [-9e99, 50e3, 9e99]  # two groups: below and above $50,000
vdf = add_income_table_row_variable(vdf, 'e00200', earnings_bins)
gbydf = vdf.groupby('table_row', as_index=False)

# compute percentage response in charitable giving
# (note elasticity values are just an example based on no empirical results)
price_elasticity = [-0.1, -0.4]
income_elasticity = [0.1, 0.1]
print('\nResponse in Charitable Giving by Earnings Group')
results = '{:18s}\t{:8.3f}\t{:8.3f}\t{:8.2f}'
colhead = '{:18s}\t{:>8s}\t{:>8s}\t{:>8s}'
print(colhead.format('Earnings Group', 'Num(#M)', 'Resp($B)', 'Resp(%)'))
tot_funits = 0.
tot_response = 0.
tot_baseline = 0.
idx = 0
for grp_interval, grp in gbydf:
    funits = grp['s006'].sum() * 1e-6
    tot_funits += funits
    response = quantity_response(grp['e19800'],
                                 price_elasticity[idx],
                                 grp['price1'],
                                 grp['price2'],
                                 income_elasticity[idx],
                                 grp['atinc1'],
                                 grp['atinc2'])
    grp_response = (response * grp['s006']).sum() * 1e-9
    tot_response += grp_response
    grp_baseline = (grp['e19800'] * grp['s006']).sum() * 1e-9
    tot_baseline += grp_baseline
    pct_response = 100. * grp_response / grp_baseline
    glabel = '[{:.8g}, {:.8g})'.format(grp_interval.left, grp_interval.right)
    print(results.format(glabel, funits, grp_response, pct_response))
    idx += 1
pct_response = 100. * tot_response / tot_baseline
print(results.format('ALL', tot_funits, tot_response, pct_response))
