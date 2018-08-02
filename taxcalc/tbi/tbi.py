"""
The public API of the TaxBrain Interface (tbi) to Tax-Calculator.

The tbi functions are used by TaxBrain to call Tax-Calculator in order
to do distributed processing of TaxBrain runs and in order to maintain
the privacy of the IRS-SOI PUF data being used by TaxBrain.  Maintaining
privacy is done by "fuzzing" reform results for several randomly selected
filing units in each table cell.  The filing units randomly selected
differ for each policy reform and the "fuzzing" involves replacing the
post-reform tax results for the selected units with their pre-reform
tax results.
"""
# CODING-STYLE CHECKS:
# pycodestyle tbi.py
# pylint --disable=locally-disabled tbi.py

from __future__ import print_function
import time
import numpy as np
import pandas as pd
from taxcalc.tbi.tbi_utils import (check_years_return_first_year,
                                   calculate,
                                   random_seed,
                                   fuzzed,
                                   summary_aggregate,
                                   summary_dist_xbin, summary_diff_xbin,
                                   summary_dist_xdec, summary_diff_xdec,
                                   create_dict_table,
                                   AGGR_ROW_NAMES)
from taxcalc import (DIST_TABLE_LABELS, DIFF_TABLE_LABELS,
                     DIST_TABLE_COLUMNS, DIFF_TABLE_COLUMNS,
                     RESULTS_TABLE_LABELS, RESULTS_TABLE_TAGS,
                     proportional_change_in_gdp, GrowDiff, GrowFactors,
                     Policy, Behavior, Consumption)
from taxcalc.utils import mtr_graph_data

AGG_ROW_NAMES = AGGR_ROW_NAMES

GDP_ELAST_ROW_NAMES = ['gdp_proportional_change']


def reform_warnings_errors(user_mods, using_puf):
    """
    The reform_warnings_errors function assumes user_mods is a dictionary
    returned by the Calculator.read_json_param_objects() function.

    This function returns a dictionary containing five STR:STR subdictionaries,
    where the dictionary keys are: 'policy', 'behavior', consumption',
    'growdiff_baseline' and 'growdiff_response'; and the subdictionaries are:
    {'warnings': '<empty-or-message(s)>', 'errors': '<empty-or-message(s)>'}.
    Note that non-policy parameters have no warnings, so the 'warnings'
    string for the non-policy parameters is always empty.
    """
    rtn_dict = {'policy': {'warnings': '', 'errors': ''},
                'behavior': {'warnings': '', 'errors': ''},
                'consumption': {'warnings': '', 'errors': ''},
                'growdiff_baseline': {'warnings': '', 'errors': ''},
                'growdiff_response': {'warnings': '', 'errors': ''}}
    # create GrowDiff objects
    gdiff_baseline = GrowDiff()
    try:
        gdiff_baseline.update_growdiff(user_mods['growdiff_baseline'])
    except ValueError as valerr_msg:
        rtn_dict['growdiff_baseline']['errors'] = valerr_msg.__str__()
    gdiff_response = GrowDiff()
    try:
        gdiff_response.update_growdiff(user_mods['growdiff_response'])
    except ValueError as valerr_msg:
        rtn_dict['growdiff_response']['errors'] = valerr_msg.__str__()
    # create Growfactors object
    growfactors = GrowFactors()
    gdiff_baseline.apply_to(growfactors)
    gdiff_response.apply_to(growfactors)
    # create Policy object
    pol = Policy(gfactors=growfactors)
    try:
        pol.implement_reform(user_mods['policy'],
                             print_warnings=False,
                             raise_errors=False)
        if using_puf:
            rtn_dict['policy']['warnings'] = pol.parameter_warnings
        rtn_dict['policy']['errors'] = pol.parameter_errors
    except ValueError as valerr_msg:
        rtn_dict['policy']['errors'] = valerr_msg.__str__()
    # create Behavior object
    behv = Behavior()
    try:
        behv.update_behavior(user_mods['behavior'])
    except ValueError as valerr_msg:
        rtn_dict['behavior']['errors'] = valerr_msg.__str__()
    # create Consumption object
    consump = Consumption()
    try:
        consump.update_consumption(user_mods['consumption'])
    except ValueError as valerr_msg:
        rtn_dict['consumption']['errors'] = valerr_msg.__str__()
    # return composite dictionary of warnings/errors
    return rtn_dict


def run_nth_year_taxcalc_model(year_n, start_year,
                               use_puf_not_cps,
                               use_full_sample,
                               user_mods,
                               return_html=True):
    """
    The run_nth_year_taxcalc_model function assumes user_mods is a dictionary
      returned by the Calculator.read_json_param_objects() function.
    Setting use_puf_not_cps=True implies use puf.csv input file;
      otherwise, use cps.csv input file.
    Setting use_full_sample=False implies use sub-sample of input file;
      otherwsie, use the complete sample.
    """
    # pylint: disable=too-many-arguments,too-many-locals,too-many-branches

    start_time = time.time()

    # create calc1 and calc2 calculated for year_n
    check_years_return_first_year(year_n, start_year, use_puf_not_cps)
    calc1, calc2 = calculate(year_n, start_year,
                             use_puf_not_cps, use_full_sample,
                             user_mods,
                             behavior_allowed=True)

    # extract unfuzzed raw results from calc1 and calc2
    dv1 = calc1.distribution_table_dataframe()
    dv2 = calc2.distribution_table_dataframe()

    _, _, mtrp1 = calc1.mtr('e00200p')
    _, _, mtrp2 = calc2.mtr('e00200p')
    record_variables = ['s006', 'MARS', 'expanded_income', 'e00200p']
    vdf = calc2.dataframe(record_variables)
    vdf['mtr1'] = mtrp1
    vdf['mtr2'] = mtrp2
    datap = mtr_graph_data(vdf,
                          year=calc2.current_year,
                          mtr_variable='e00200p')['lines']

    _, _, mtrs1 = calc1.mtr('e00200s')
    _, _, mtrs2 = calc2.mtr('e00200s')
    record_variables = ['s006', 'MARS', 'expanded_income', 'e00200p']
    vdf = calc2.dataframe(record_variables)
    vdf['mtr1'] = mtrs1
    vdf['mtr2'] = mtrs2
    datas = mtr_graph_data(vdf,
                          mars=2,
                          year=calc2.current_year,
                          mtr_variable='e00200p')['lines']

    # delete calc1 and calc2 now that raw results have been extracted
    del calc1
    del calc2

    # construct TaxBrain summary results from raw results
    sres = dict()
    fuzzing = use_puf_not_cps
    if fuzzing:
        # seed random number generator with a seed value based on user_mods
        # (reform-specific seed is used to choose whose results are fuzzed)
        seed = random_seed(user_mods)
        print('fuzzing_seed={}'.format(seed))
        np.random.seed(seed)  # pylint: disable=no-member
        # make bool array marking which filing units are affected by the reform
        reform_affected = np.logical_not(  # pylint: disable=no-member
            np.isclose(dv1['combined'], dv2['combined'], atol=0.01, rtol=0.0)
        )
        agg1, agg2 = fuzzed(dv1, dv2, reform_affected, 'aggr')
        sres = summary_aggregate(sres, agg1, agg2)
        del agg1
        del agg2
        dv1b, dv2b = fuzzed(dv1, dv2, reform_affected, 'xbin')
        sres = summary_dist_xbin(sres, dv1b, dv2b)
        sres = summary_diff_xbin(sres, dv1b, dv2b)
        del dv1b
        del dv2b
        dv1d, dv2d = fuzzed(dv1, dv2, reform_affected, 'xdec')
        sres = summary_dist_xdec(sres, dv1d, dv2d)
        sres = summary_diff_xdec(sres, dv1d, dv2d)
        del dv1d
        del dv2d
        del reform_affected
    else:
        sres = summary_aggregate(sres, dv1, dv2)
        sres = summary_dist_xbin(sres, dv1, dv2)
        sres = summary_diff_xbin(sres, dv1, dv2)
        sres = summary_dist_xdec(sres, dv1, dv2)
        sres = summary_diff_xdec(sres, dv1, dv2)
        sres['mtr_primary'] = datap
        sres['mtr_spouse'] = datas

    labels = {x: DIFF_TABLE_LABELS[i]
              for i, x in enumerate(DIFF_TABLE_COLUMNS[:-2])}
    labels.update({x: DIST_TABLE_LABELS[i]
                   for i, x in enumerate(DIST_TABLE_COLUMNS)})

    # nested function used below
    def label_columns(pdf):
        """
        label_columns embedded function revises all column names in pdf
        """
        pdf.columns = [(labels[str(col)] if str(col) in labels else str(col))
                       for col in pdf.columns]
        return pdf

    # optionally return non-JSON-like results
    # it would be nice to allow the user to download the full CSV instead
    # of a CSV for each year
    # what if we allowed an aggregate format call?
    #  - presents project with all data proeduced in a run?

    res = dict()
    for tbl in sres:
        res[tbl] = label_columns(sres[tbl])
    if return_html:
        formatted = {'outputs': []}
        for tbl in res:
            year = str(start_year + year_n)
            formatted['outputs'].append({
                'tags': RESULTS_TABLE_TAGS[tbl],
                'year': year,
                'title': '{} ({})'.format(
                    (RESULTS_TABLE_LABELS[tbl]
                     if tbl in RESULTS_TABLE_LABELS else tbl),
                    year),
                'download_only': res[tbl].to_csv(),
                'renderable': (res[tbl].to_html()
                               .replace(' border="1"', '')
                               .replace(' style="text-align: right;"', ''))
            })
        elapsed_time = time.time() - start_time
        print('elapsed time for this run: {:.1f}'.format(elapsed_time))
        return formatted
    else:
        elapsed_time = time.time() - start_time
        print('elapsed time for this run: {:.1f}'.format(elapsed_time))
        return res

def run_nth_year_gdp_elast_model(year_n, start_year,
                                 use_puf_not_cps,
                                 use_full_sample,
                                 user_mods,
                                 gdp_elasticity,
                                 return_dict=True):
    """
    The run_nth_year_gdp_elast_model function assumes user_mods is a dictionary
      returned by the Calculator.read_json_param_objects() function.
    Setting use_puf_not_cps=True implies use puf.csv input file;
      otherwise, use cps.csv input file.
    Setting use_full_sample=False implies use sub-sample of input file;
      otherwsie, use the complete sample.
    """
    # pylint: disable=too-many-arguments,too-many-locals

    # calculate gdp_effect
    fyear = check_years_return_first_year(year_n, start_year, use_puf_not_cps)
    if year_n > 0 and (start_year + year_n) > fyear:
        # create calc1 and calc2 calculated for year_n - 1
        (calc1, calc2) = calculate((year_n - 1), start_year,
                                   use_puf_not_cps,
                                   use_full_sample,
                                   user_mods,
                                   behavior_allowed=False)
        # compute GDP effect given specified gdp_elasticity
        gdp_effect = proportional_change_in_gdp((start_year + year_n),
                                                calc1, calc2, gdp_elasticity)
    else:
        gdp_effect = 0.0

    # return gdp_effect results
    if return_dict:
        gdp_df = pd.DataFrame(data=[gdp_effect], columns=['col0'])
        gdp_elast_names_n = [x + '_' + str(year_n)
                             for x in GDP_ELAST_ROW_NAMES]
        gdp_elast_total = create_dict_table(gdp_df,
                                            row_names=gdp_elast_names_n,
                                            num_decimals=5)
        gdp_elast_total = dict((k, v[0]) for k, v in gdp_elast_total.items())
        return gdp_elast_total
    return gdp_effect
