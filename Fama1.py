#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep  1 12:43:51 2020

@author: owen
"""


import pandas as pd
import numpy as np
import pandas_datareader as web
from dateutil.relativedelta import relativedelta
import datetime as dt
import math

# organize raw data from bloomberg terminal
df = pd.read_excel('Bloomberg_Data.xlsx')
comp_list = pd.read_excel('comp_list.xlsx')
comp = comp_list['Company'].to_list()
date_index = df.iloc[:,76:].columns.to_list() # start from 2015
company_list = []
for i in comp:
    company_list += [i] * len(date_index)
date = []
for _ in range(0,len(comp)):
    date+= date_index


total = []
for i in range(0,4):
    data = []
    for x in range(i,len(df),4):
        each_data = df.iloc[x,76:].to_list() # start from 2015
        data += each_data
    total.append(data)
p_b = total[0]
market_cap = total[1]
beta = total[2]
vol = total[3]

b_m = [1/i for i in p_b] # convert price to book into book to market

all_data = pd.DataFrame({'Company': company_list, 'B/M':b_m, 'Market_Cap':market_cap, 'Beta':beta}, index=date)

# get each stock return
def get_stock_ret (ticker, start, end):
    stock_price = web.get_data_yahoo(ticker, start, end)
    stock_ret = (np.log(stock_price['Adj Close']) - np.log(stock_price['Adj Close']).shift(1)).dropna()
    monthly_ret = stock_ret.resample('BMS').sum()
    return monthly_ret.to_list()

start = all_data.index[0]
end = all_data.index[-1] + relativedelta(months=+1)
ret = []
for i in comp:
    ticker = i + '.JK'
    ret+= get_stock_ret(ticker, start, end)
all_data['Return'] = ret

# portfolio construction
def vw_weighted_ret(portfolio, factor):
    weight = portfolio[factor]/np.sum(portfolio[factor])
    vw_ret = weight * portfolio['Return']
    return np.sum(vw_ret)

start = dt.datetime(2015,1,1)
end = dt.datetime(2020,1,1)
SMB = []
HML = []
Market_Ret = []
small_growth = []
small_neutral = []
small_value = []
big_growth = []
big_neutral = []
big_value = []
for period in pd.date_range(start,end,freq='MS'):
    first = all_data.loc[period]
    sort_size = first.sort_values('Market_Cap') # ascending
    small_port = sort_size.iloc[:int(len(sort_size)/2)]
    big_port = sort_size.iloc[int(len(sort_size)/2):]
    
    # small -growth, -neutral, and -value portfolio
    sort_small_bm = small_port.sort_values('B/M') # ascending
    small_growth_port = sort_small_bm.iloc[:round(len(sort_small_bm)/3)]
    small_neutral_port = sort_small_bm.iloc[round(len(sort_small_bm)/3):round(len(sort_small_bm)/3)*2]
    small_value_port = sort_small_bm.iloc[-math.floor(len(sort_small_bm)/3):] # division with remainder
    
    small_growth_ret = vw_weighted_ret(small_growth_port, 'Market_Cap')
    small_neutral_ret = vw_weighted_ret(small_neutral_port, 'Market_Cap')
    small_value_ret = vw_weighted_ret(small_value_port, 'Market_Cap')
    
    # big -growth, -neutral, and -value portfolio
    sort_big_bm = big_port.sort_values('B/M') # ascending
    big_growth_port = sort_big_bm.iloc[:round(len(sort_big_bm)/3)]
    big_neutral_port = sort_big_bm.iloc[round(len(sort_big_bm)/3):round(len(sort_big_bm)/3)*2]
    big_value_port = sort_big_bm.iloc[-math.floor(len(sort_big_bm)/3):] # division with remainder
    
    big_growth_ret = vw_weighted_ret(big_growth_port, 'Market_Cap')
    big_neutral_ret = vw_weighted_ret(big_neutral_port, 'Market_Cap')
    big_value_ret = vw_weighted_ret(big_value_port, 'Market_Cap')
    
    
    # smb and hml
    smb_ret = ((small_growth_ret+small_neutral_ret+small_value_ret)/3) - ((big_growth_ret+big_neutral_ret+big_value_ret)/3)
    hml_ret = ((small_value_ret+big_value_ret)/2) - ((small_growth_ret+big_growth_ret)/2)
    
    SMB.append(smb_ret)
    HML.append(hml_ret)
    
    # benchmark return
    market_ret = vw_weighted_ret(first, 'Market_Cap')
    Market_Ret.append(market_ret)
    
    # append 6 portfolios
    small_growth.append(small_growth_ret)
    small_neutral.append(small_value_ret)
    small_value.append(small_value_ret)
    big_growth.append(big_growth_ret)
    big_neutral.append(big_neutral_ret)
    big_value.append(big_value_ret)
    
fama = pd.DataFrame({'Market Return':Market_Ret, 'SMB':SMB, 'HML':HML, 'Small Growth':small_growth, 'Small Neutral':small_neutral, 'Small Value': small_value, 'Big Growth': big_growth, 'Big Neutral':big_neutral, 'Big Value':big_value}, index = all_data.index.unique())
print(fama)
fama.to_excel('fama_french.xlsx')
    




    
