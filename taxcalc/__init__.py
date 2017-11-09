from taxcalc.calculate import *
from taxcalc.policy import *
from taxcalc.behavior import *
from taxcalc.consumption import *
from taxcalc.filings import *
from taxcalc.growfactors import *
from taxcalc.growdiff import *
from taxcalc.records import *
from taxcalc.taxcalcio import *
from taxcalc.utils import *
from taxcalc.macro_elasticity import *
from taxcalc.tbi import *
from taxcalc.cli import *
import pandas as pd

from taxcalc._version import get_versions
__version__ = get_versions()['version']
del get_versions

# zsum is defined in utils.py
pd.Series.zsum = zsum
pd.Series.old_sum = pd.Series.sum
pd.Series.sum = zsum
