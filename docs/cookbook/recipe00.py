import pandas as pd
from taxcalc import *

# use publicly-available CPS input file including benefits
recs = Records.cps_constructor()
# NOTE: if you have access to the restricted-use IRS-SOI PUF-based input file
#       and you have that file (named 'puf.csv') located in the directory
#       where this script is located, then you can substitute the following
#       statement for the prior statement:
# recs = Records()

# specify Calculator object for static analysis of current-law policy
pol = Policy()
calc1 = Calculator(policy=pol, records=recs)

# NOTE: calc1 now contains a PRIVATE COPY of pol and a PRIVATE COPY of recs,
#       so we can continue to use pol and recs in this script without any
#       concern about side effects from Calculator method calls on calc1.

cyr = 2020

# calculate aggregate current-law income tax liabilities for cyr
calc1.advance_to_year(cyr)
calc1.calc_all()
itax_rev1 = calc1.weighted_total('iitax')

# read JSON reform file and use (the default) static analysis assumptions
reform_filename = './ingredients/reformA.json'
params = Calculator.read_json_param_objects(reform=reform_filename,
                                            assump=None)

# specify Calculator object for static analysis of reform policy
pol.implement_reform(params['policy'])
calc2 = Calculator(policy=pol, records=recs)

# calculate reform income tax liabilities for cyr
calc2.advance_to_year(cyr)
calc2.calc_all()
itax_rev2 = calc2.weighted_total('iitax')

# print reform documentation
print('')
print(Calculator.reform_documentation(params))

# print total revenue estimates for cyr
# (estimates in billons of dollars rounded to nearest hundredth of a billion)
print('{}_CLP_itax_rev($B)= {:.3f}'.format(cyr, itax_rev1 * 1e-9))
print('{}_REF_itax_rev($B)= {:.3f}'.format(cyr, itax_rev2 * 1e-9))
print('')

# generate several other standard results tables:

# aggregate diagnostic tables for cyr
clp_diagnostic_table = calc1.diagnostic_table(1)
ref_diagnostic_table = calc2.diagnostic_table(1)

# income-tax distribution for cyr with CLP and REF results side-by-side
dist_table1, dist_table2 = calc1.distribution_tables(calc2, 'weighted_deciles')
assert isinstance(dist_table1, pd.DataFrame)
assert isinstance(dist_table2, pd.DataFrame)
dist_extract = pd.DataFrame()
dist_extract['funits(#m)'] = dist_table1['s006']
dist_extract['itax1($b)'] = dist_table1['iitax']
dist_extract['itax2($b)'] = dist_table2['iitax']
dist_extract['aftertax_inc1($b)'] = dist_table1['aftertax_income']
dist_extract['aftertax_inc2($b)'] = dist_table2['aftertax_income']

# income-tax difference table by expanded-income decile for cyr
diff_table = calc1.difference_table(calc2, 'weighted_deciles', 'iitax')
assert isinstance(diff_table, pd.DataFrame)
diff_extract = pd.DataFrame()
dif_colnames = ['count', 'tot_change', 'mean',
                'pc_aftertaxinc']
ext_colnames = ['funits(#m)', 'agg_diff($b)', 'mean_diff($)',
                'aftertaxinc_diff(%)']
for dname, ename in zip(dif_colnames, ext_colnames):
    diff_extract[ename] = diff_table[dname]

# generate percentage-change-in-aftertax-income graph and save in an HTML file
fig = calc1.pch_graph(calc2)
write_graph_file(fig, 'recipe00.graph.html', 'recipe00.graph')

print('CLP diagnostic table:')
print(clp_diagnostic_table)
print('')
print('REF diagnostic table:')
print(ref_diagnostic_table)
print('')

title = 'Extract of {} distribution table by baseline expanded-income decile:'
print(title.format(cyr))
print(dist_extract.to_string())
print('')

title = 'Extract of {} income-tax difference table by expanded-income decile:'
print(title.format(cyr))
print(diff_extract.to_string())
