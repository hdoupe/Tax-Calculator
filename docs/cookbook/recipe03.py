from __future__ import print_function  # necessary only if using Python 2.7
from taxcalc import *

# use publicly-available CPS input file
recs = Records.cps_constructor()

# specify Calculator object for static analysis of current-law policy
pol = Policy()
calc = Calculator(policy=pol, records=recs)

cyr = 2020

# calculate aggregate current-law income tax liabilities for cyr
calc.advance_to_year(cyr)
calc.calc_all()

# tabulate custom table showing number of filing units receiving EITC
# and the average positive EITC amount by IRS-SOI AGI categories
vardf = calc.dataframe(['s006', 'c00100', 'eitc'])
vardf = add_income_table_row_variable(vardf, 'c00100', SOI_AGI_BINS)
gbydf = vardf.groupby('table_row', as_index=False)

# print AGI table with ALL row at bottom
print('Filing Units Receiving EITC and Average Positive EITC by AGI Category')
results = '{:23s}\t{:8.3f}\t{:8.3f}'
colhead = '{:23s}\t{:>8s}\t{:>8s}'
print(colhead.format('AGI Category', 'Num(#M)', 'Avg($K)'))
tot_recips = 0.
tot_amount = 0.
idx = 0
for gname, grp in gbydf:
    recips = grp[grp['eitc'] > 0]['s006'].sum() * 1e-6
    tot_recips += recips
    amount = (grp['eitc'] * grp['s006']).sum() * 1e-9
    tot_amount += amount
    if recips > 0:
        avg = amount / recips
    else:
        avg = np.nan
    print(results.format(gname, recips, avg))
    idx += 1
avg = tot_amount / tot_recips
print(results.format('ALL', tot_recips, avg))
