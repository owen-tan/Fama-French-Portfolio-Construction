#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 14:58:15 2020

@author: owen
"""


import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
plt.style.use('dark_background')

# =============================================================================
# Checking Fama-French hypothesis through visualisation and statistical method
# =============================================================================

# load data
fama_data = pd.read_excel('fama_french.xlsx', index_col=0)

# plot cummulative return
fama_data = fama_data.cumsum()
fama_data[['Small Value', 'Small Neutral', 'Small Growth', 'Big Value', 'Big Neutral', 'Big Growth', 'Market Return']].plot()
plt.title('Cummulative Return 2015 - 2020')
plt.ylabel('Return (%)')
plt.xlabel('Date')

# =============================================================================
# Multivariate regression of portfolios on market return, SMB, and HML factor
# Code below is only for one portfolio (Small Value), simply change the y parameter (dependent var)
# to test different portfolio.
# =============================================================================

y = fama_data['Small Value']
X = fama_data[['Market Return', 'SMB', 'HML']]
X = sm.add_constant(X)
model = sm.OLS(y,X)
res = model.fit()
print(res.summary())
print(res.HC0_se) # White/robust standard error

