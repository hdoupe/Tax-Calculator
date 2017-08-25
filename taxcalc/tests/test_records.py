import os
import json
import numpy as np
from numpy.testing import assert_array_equal
import pandas as pd
import pytest
from io import StringIO
from taxcalc import Growfactors, Policy, Records, Calculator, CPSCSV_YEAR


def test_incorrect_Records_instantiation(cps_subsample):
    with pytest.raises(ValueError):
        recs = Records(data=list())
    with pytest.raises(ValueError):
        recs = Records(data=cps_subsample, gfactors=list())
    with pytest.raises(ValueError):
        recs = Records(data=cps_subsample, gfactors=None, weights=list())
    with pytest.raises(ValueError):
        recs = Records(data=cps_subsample, gfactors=None, weights=None,
                       start_year=list())
    with pytest.raises(ValueError):
        recs = Records(data=cps_subsample, gfactors=None, weights=None,
                       adjust_ratios=list())


def test_correct_Records_instantiation(cps_subsample):
    rec1 = Records.cps_constructor(data=cps_subsample)
    assert rec1
    assert np.all(rec1.MARS != 0)
    assert rec1.current_year == rec1.data_year
    sum_e00200_in_cps_year = rec1.e00200.sum()
    rec1.set_current_year(rec1.data_year + 1)
    sum_e00200_in_cps_year_plus_one = rec1.e00200.sum()
    assert sum_e00200_in_cps_year_plus_one == sum_e00200_in_cps_year
    wghts_path = os.path.join(Records.CUR_PATH, Records.CPS_WEIGHTS_FILENAME)
    wghts_df = pd.read_csv(wghts_path)
    ratio_path = os.path.join(Records.CUR_PATH, Records.PUF_RATIOS_FILENAME)
    ratio_df = pd.read_csv(ratio_path)
    ratio_df = ratio_df.transpose()
    rec2 = Records(data=cps_subsample,
                   exact_calculations=False,
                   gfactors=Growfactors(),
                   weights=wghts_df,
                   adjust_ratios=ratio_df,
                   start_year=CPSCSV_YEAR)
    assert rec2
    assert np.all(rec2.MARS != 0)
    assert rec2.current_year == rec2.data_year


@pytest.mark.parametrize("csv", [
    (
        u'RECID,MARS,e00200,e00200p,e00200s\n'
        u'1,    2,   200000, 200000,   0.03\n'
    ),
    (
        u'RECID,MARS,e00900,e00900p,e00900s\n'
        u'1,    2,   200000, 200000,   0.03\n'
    ),
    (
        u'RECID,MARS,e02100,e02100p,e02100s\n'
        u'1,    2,   200000, 200000,   0.03\n'
    ),
    (
        u'RxCID,MARS\n'
        u'1,    2\n'
    ),
    (
        u'RECID,e00300\n'
        u'1,    456789\n'
    ),
    (
        u'RECID,MARS\n'
        u'1,    6\n'
    ),
    (
        u'RECID,MARS,e00600,e00650\n'
        u'1,    1,        8,     9\n'
    )
])
def test_read_data(csv):
    df = pd.read_csv(StringIO(csv))
    with pytest.raises(ValueError):
        Records(data=df)


def test_for_duplicate_names():
    varnames = set()
    for varname in Records.USABLE_READ_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname not in Records.CALCULATED_VARS
    varnames = set()
    for varname in Records.CALCULATED_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname not in Records.USABLE_READ_VARS
    varnames = set()
    for varname in Records.INTEGER_READ_VARS:
        assert varname not in varnames
        varnames.add(varname)
        assert varname in Records.USABLE_READ_VARS


def test_records_variables_content(tests_path):
    """
    Check completeness and consistency of records_variables.json content.
    """
    # specify test information
    reqkeys = ['type', 'desc', 'form']
    first_year = Policy.JSON_START_YEAR
    last_form_year = 2016
    # read JSON variable file into a dictionary
    path = os.path.join(tests_path, '..', 'records_variables.json')
    vfile = open(path, 'r')
    allvars = json.load(vfile)
    vfile.close()
    assert isinstance(allvars, dict)
    # check elements in each variable dictionary
    for iotype in ['read', 'calc']:
        for vname in allvars[iotype]:
            variable = allvars[iotype][vname]
            assert isinstance(variable, dict)
            # check that variable contains required keys
            for key in reqkeys:
                assert key in variable
            # check that required is true if it is present
            if 'required' in variable:
                assert variable['required'] is True
            # check that forminfo is dictionary with sensible year ranges
            forminfo = variable['form']
            assert isinstance(forminfo, dict)
            yranges = sorted(forminfo.keys())
            prior_eyr = first_year - 1
            for yrange in yranges:
                yrlist = yrange.split('-')
                fyr = int(yrlist[0])
                eyr = int(yrlist[1])
                assert fyr == prior_eyr + 1
                assert eyr <= last_form_year
                prior_eyr = eyr
            if len(yranges) > 0:
                assert prior_eyr == last_form_year


def test_csv_input_vars_md_contents(tests_path):
    """
    Check CSV_INPUT_VARS.md contents against Records.USABLE_READ_VARS
    """
    # read variable names in CSV_INPUT_VARS.md file (checking for duplicates)
    civ_path = os.path.join(tests_path, '..', 'validation',
                            'CSV_INPUT_VARS.md')
    civ_set = set()
    with open(civ_path, 'r') as civfile:
        msg = 'DUPLICATE VARIABLE(S) IN CSV_INPUT_VARS.MD FILE:\n'
        found_duplicates = False
        for line in civfile:
            str_list = line.split('|', 2)
            if len(str_list) != 3:
                continue  # because line is not part of the markdown table
            assert str_list[0] == ''  # because line starts with | character
            var = (str_list[1]).strip()  # remove surrounding whitespace
            if var == 'Var-name' or var[0] == ':':
                continue  # skip two lines that are the table head
            if var in civ_set:
                found_duplicates = True
                msg += 'VARIABLE= {}\n'.format(var)
            else:
                civ_set.add(var)
        if found_duplicates:
            raise ValueError(msg)
    # check that civ_set is a subset of Records.USABLE_READ_VARS set
    if not civ_set.issubset(Records.USABLE_READ_VARS):
        valid_less_civ = Records.USABLE_READ_VARS - civ_set
        msg = 'VARIABLE(S) IN USABLE_READ_VARS BUT NOT CSV_INPUT_VARS.MD:\n'
        for var in valid_less_civ:
            msg += 'VARIABLE= {}\n'.format(var)
        raise ValueError(msg)


def test_benefits():
    """
    Ensure that benefits data is updated as expected
    """
    benefits_path = os.path.join(os.path.join(Records.CUR_PATH,
                                 "cps_benefits.csv.gz"))
    benefits = pd.read_csv(benefits_path, compression="gzip")
    print(benefits.columns.tolist())
    rec = Records.cps_constructor(data=None,
                                  exact_calculations=False,
                                  growfactors=Growfactors(),
                                  benefits=benefits.copy(deep=True))

    assert rec.current_year == 2014
    recip_col_name = "ssi_recipients_{}".format(2014)
    ben_col_name = "ssi_benefits_{}".format(2014)
    assert (np.allclose(rec.ssi_recipients,
                        benefits[recip_col_name].values) and
            np.allclose(rec.ssi_benefits, benefits[ben_col_name].values))

    for i in range(1, 13):
        rec.increment_year()
        recip_col_name = "ssi_recipients_{}".format(2014 + i)
        ben_col_name = "ssi_benefits_{}".format(2014 + i)
        assert (np.allclose(rec.ssi_recipients,
                            benefits[recip_col_name].values) and
                np.allclose(rec.ssi_benefits, benefits[ben_col_name].values))

    assert rec.current_year == 2026
