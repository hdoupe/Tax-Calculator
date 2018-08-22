"""
Implements TaxBrain "Macroeconomic Elasticities Simulation" dynamic analysis.
"""
# CODING-STYLE CHECKS:
# pycodestyle macro_elasticity.py
# pylint --disable=locally-disabled macro_elasticity.py

from taxcalc.policy import Policy
from taxcalc.parameters import ParametersBase


class MacroElasticity(ParametersBase):

    JSON_START_YEAR = Policy.JSON_START_YEAR
    DEFAULTS_FILENAME = 'macro_elasticity.json'
    DEFAULT_NUM_YEARS = Policy.DEFAULT_NUM_YEARS

    def __init__(self,
                 start_year=JSON_START_YEAR,
                 num_years=DEFAULT_NUM_YEARS):
        super(MacroElasticity, self).__init__()
        self._vals = self._params_dict_from_json_file()
        if start_year < Policy.JSON_START_YEAR:
            raise ValueError('start_year < Policy.JSON_START_YEAR')
        if num_years < 1:
            raise ValueError('num_years < 1')
        self.initialize(start_year, num_years)
        self.parameter_errors = ''

    def update_elasticity(self, revision):
        # check that all revisions dictionary keys are integers
        if not isinstance(revision, dict):
            raise ValueError('ERROR: revision is not a dictionary')
        if not revision:
            return  # no revision to implement
        revision_years = sorted(list(revision.keys()))
        for year in revision_years:
            if not isinstance(year, int):
                msg = 'ERROR: {} KEY {}'
                details = 'KEY in revision is not an integer calendar year'
                raise ValueError(msg.format(year, details))
        # check range of remaining revision_years
        first_revision_year = min(revision_years)
        if first_revision_year < self.start_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR < start_year={}'
            raise ValueError(msg.format(first_revision_year, self.start_year))
        if first_revision_year < self.current_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR < current_year={}'
            raise ValueError(
                msg.format(first_revision_year, self.current_year)
            )
        last_revision_year = max(revision_years)
        if last_revision_year > self.end_year:
            msg = 'ERROR: {} YEAR revision provision in YEAR > end_year={}'
            raise ValueError(msg.format(last_revision_year, self.end_year))
        # validate revision parameter names and types
        self._validate_assump_parameter_names_types(revision)
        if self.parameter_errors:
            raise ValueError(self.parameter_errors)
        # implement the revision year by year
        precall_current_year = self.current_year
        revision_parameters = set()
        for year in revision_years:
            self.set_year(year)
            revision_parameters.update(revision[year].keys())
            self._update({year: revision[year]})
        self.set_year(precall_current_year)
        # validate revision parameter values
        self._validate_assump_parameter_values(revision_parameters)
        if self.parameter_errors:
            raise ValueError('\n' + self.parameter_errors)

    def calc_all(self, year, calc1, calc2):
        '''
        This function harnesses econometric estimates of the historic relationship
        between tax policy and the macro economy to predict the effect of tax
        reforms on economic growth.

        In particular, this model relies on estimates of how GDP responds to
        changes in the average after tax rate on wage income across all taxpayers
        (one minus the average marginal tax rate, or 1-AMTR). These estimates are
        derived from calculations of income-weighted marginal tax rates under the
        baseline and reform.  The reform-induced change in GDP in year t is
        assumed to be equal to the assumed elasticity times the absolute (not
        proportional) change in one minus the average marginal tax rate in
        year t-1.  In other words, the current-year change in GDP is assumed to
        be related to the prior-year change in the average marginal tax rate.

        Empirical evidence on this elasticity can be found in Robert Barro
        and Charles Redlick, "Macroeconomic Effects from Government Purchases
        and Taxes" (2011 Quarterly Journal of Economics).  A pre-publication
        version of this paper is available at the following URL:
        <siteresources.worldbank.org/INTMACRO/Resources/BarroBRedlickBpaper.pdf>.
        In particular, Barro and Redlick find that a 1 percentage point decrease
        in the AMTR leads to a 0.54 percent increase in GDP.  Evaluated at the
        sample mean, this translates to an elasticity of GDP with respect to the
        average after-tax marginal rate of about 0.36.

        A more recent paper by Karel Mertens and Jose L. Montiel Olea,
        entitled "Marginal Tax Rates and Income: New Time Series Evidence",
        NBER working paper 19171 (June 2013 with September 2017 revisions)
        <www.nber.org/papers/w19171.pdf>, contains additional empirical
        evidence suggesting the elasticity is no less than the 0.36 Barro-
        Redlick estimate and perhaps somewhat higher (see section 4.6).
        Their summary of the Barro and Redlick findings (on page 5) are
        as follows: "Barro and Redlick (2011) however find that a one
        percentage point cut in the AMTR raises per capita GDP by around
        0.5% in the following year. This estimate is statistically
        significant and amounts to a short run GDP elasticity to the
        net-of-tax rate of 0.36".

        Parameters
        ----------
        year : calendar year of the reform-induced proportion change in GDP
        calc1 : Calculator object for the pre-reform baseline for prior year
        calc2 : Calculator object for the policy reform for prior year
        elasticity: Float estimate of elasticity of GDP wrt 1-AMTR

        Returns
        -------
        Float estimate of proportional change in GDP induced by the reform
        Note that proportional means a relative change but it is not expressed
        in percentage terms
        '''
        assert self.elasticity >= 0.0
        assert calc1.current_year == calc2.current_year
        assert calc1.data_year == calc2.data_year
        if year <= max(Policy.JSON_START_YEAR, calc1.data_year):
            return 0.0  # because Calculator cannot simulate taxes in year-1
        if calc1.current_year != (year - 1):
            msg = 'calc.current_year={} must be one less than year={}'
            raise ValueError(msg.format(calc1.current_year, year))
        _, _, mtr_combined1 = calc1.mtr()
        _, _, mtr_combined2 = calc2.mtr()
        avg_mtr1 = ((mtr_combined1 * calc1.array('c00100') *
                     calc1.array('s006')).sum()) / calc1.weighted_total('c00100')
        avg_mtr2 = ((mtr_combined2 * calc2.array('c00100') *
                     calc2.array('s006')).sum()) / calc2.weighted_total('c00100')
        proportional_chg_in_rate = ((1.0 - avg_mtr2) / (1.0 - avg_mtr1)) - 1.0
        return self.elasticity * proportional_chg_in_rate
