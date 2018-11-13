WARNING: the Behavior class is deprecated and will be removed soon.
FUTURE: use the Behavioral-Responses behresp package OR
        use the Tax-Calculator quantity_response function.
You loaded data for 2014.
Your data include the following unused variables that will be ignored:
  filer
Tax-Calculator startup automatically extrapolated your data to 2014.
WARNING: the Behavior class is deprecated and will be removed soon.
FUTURE: use the Behavioral-Responses behresp package OR
        use the Tax-Calculator quantity_response function.
You loaded data for 2014.
Your data include the following unused variables that will be ignored:
  filer
Tax-Calculator startup automatically extrapolated your data to 2014.

REFORM DOCUMENTATION
Baseline Growth-Difference Assumption Values by Year:
none: using default baseline growth assumptions
Policy Reform Parameter Values by Year:
2020:
 _II_em : 1000
  name: Personal and dependent exemption amount
  desc: Subtracted from AGI in the calculation of taxable income, per taxpayer
        and dependent.
  baseline_value: 0.0
 _II_rt5 : 0.36
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 5
  desc: The third highest tax rate, applied to the portion of taxable income
        below tax bracket 5 and above tax bracket 4.
  baseline_value: 0.32
 _II_rt6 : 0.39
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 6
  desc: The second higher tax rate, applied to the portion of taxable income
        below tax bracket 6 and above tax bracket 5.
  baseline_value: 0.35
 _II_rt7 : 0.41
  name: Personal income (regular/non-AMT/non-pass-through) tax rate 7
  desc: The tax rate applied to the portion of taxable income below tax
        bracket 7 and above tax bracket 6.
  baseline_value: 0.37
 _PT_rt5 : 0.36
  name: Pass-through income tax rate 5
  desc: The third highest tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 5
        and above tax bracket 4.
  baseline_value: 0.32
 _PT_rt6 : 0.39
  name: Pass-through income tax rate 6
  desc: The second higher tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 6
        and above tax bracket 5.
  baseline_value: 0.35
 _PT_rt7 : 0.41
  name: Pass-through income tax rate 7
  desc: The highest tax rate, applied to the portion of income from sole
        proprietorships, partnerships and S-corporations below tax bracket 7
        and above tax bracket 6.
  baseline_value: 0.37

2020_CLP_itax_rev($B)= 1413.428
2020_REF_itax_rev($B)= 1410.783

CLP diagnostic table:
                                     2020
Returns (#m)                      167.510
AGI ($b)                        11946.468
Itemizers (#m)                     31.030
Itemized Deduction ($b)           872.795
Standard Deduction Filers (#m)    136.480
Standard Deduction ($b)          2438.381
Personal Exemption ($b)             0.000
Taxable Income ($b)              9126.239
Regular Tax ($b)                 1574.257
AMT Income ($b)                 11332.086
AMT Liability ($b)                  1.827
AMT Filers (#m)                     0.420
Tax before Credits ($b)          1576.084
Refundable Credits ($b)            78.598
Nonrefundable Credits ($b)         93.685
Reform Surtaxes ($b)                0.000
Other Taxes ($b)                    9.627
Ind Income Tax ($b)              1413.428
Payroll Taxes ($b)               1316.606
Combined Liability ($b)          2730.034
With Income Tax <= 0 (#m)          60.370
With Combined Tax <= 0 (#m)        39.230

REF diagnostic table:
                                     2020
Returns (#m)                      167.510
AGI ($b)                        11946.468
Itemizers (#m)                     30.950
Itemized Deduction ($b)           870.479
Standard Deduction Filers (#m)    136.560
Standard Deduction ($b)          2439.801
Personal Exemption ($b)           327.446
Taxable Income ($b)              8879.741
Regular Tax ($b)                 1569.188
AMT Income ($b)                 11334.037
AMT Liability ($b)                  1.785
AMT Filers (#m)                     0.420
Tax before Credits ($b)          1570.973
Refundable Credits ($b)            81.346
Nonrefundable Credits ($b)         88.471
Reform Surtaxes ($b)                0.000
Other Taxes ($b)                    9.627
Ind Income Tax ($b)              1410.783
Payroll Taxes ($b)               1316.606
Combined Liability ($b)          2727.388
With Income Tax <= 0 (#m)          62.570
With Combined Tax <= 0 (#m)        39.560

Extract of 2020 distribution table by baseline expanded-income decile:
        funits(#m)  itax1($b)  itax2($b)  aftertax_inc1($b)  aftertax_inc2($b)
0-10n         0.00      0.000      0.000              0.000              0.000
0-10z         0.00      0.000      0.000              0.000              0.000
0-10p        16.75     -4.245     -4.611            162.909            163.274
10-20        16.75     -1.719     -2.795            413.273            414.349
20-30        16.75      3.487      2.255            551.395            552.627
30-40        16.75      9.901      8.217            679.030            680.715
40-50        16.75     18.877     16.549            836.851            839.180
50-60        16.75     32.449     29.390           1028.479           1031.538
60-70        16.75     61.434     57.505           1263.591           1267.519
70-80        16.75    106.685    101.378           1583.962           1589.269
80-90        16.75    213.758    205.507           2108.727           2116.977
90-100       16.75    972.801    997.387           4309.799           4285.212
ALL         167.51   1413.428   1410.783          12938.017          12940.662
90-95         8.38    214.466    210.146           1438.220           1442.539
95-99         6.70    327.052    326.021           1668.488           1669.519
Top 1%        1.68    431.283    461.220           1203.091           1173.155

Extract of 2020 income-tax difference table by expanded-income decile:
        funits(#m)  agg_diff($b)  mean_diff($)  aftertaxinc_diff(%)
0-10n         0.00         0.000           0.0                  NaN
0-10z         0.00         0.000           0.0                  NaN
0-10p        16.75        -0.365         -21.8                  0.2
10-20        16.75        -1.076         -64.2                  0.3
20-30        16.75        -1.232         -73.5                  0.2
30-40        16.75        -1.685        -100.6                  0.2
40-50        16.75        -2.329        -139.0                  0.3
50-60        16.75        -3.059        -182.6                  0.3
60-70        16.75        -3.928        -234.5                  0.3
70-80        16.75        -5.307        -316.8                  0.3
80-90        16.75        -8.250        -492.5                  0.4
90-100       16.75        24.586        1467.7                 -0.6
ALL         167.51        -2.645         -15.8                  0.0
90-95         8.38        -4.319        -515.7                  0.3
95-99         6.70        -1.031        -153.9                  0.1
Top 1%        1.68        29.936       17871.0                 -2.5
