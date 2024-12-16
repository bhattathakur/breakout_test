#import libraries

import pandas as pd
import yfinance as yf
import streamlit as st


#functions to use in the later part
##check if the given date is business day or not
def is_business_day(date):
  '''
  This function checks if the given date is a business day or not
  '''
  return pd.to_datetime(date).weekday()<5

#user input ticker, start_date, end_date,volume_threshold%,%change on the end date,holding period
debug=True
#ask the user for the ticker
user_ticker=st.sidebar.text_input("Enter a ticker",value='TSLA',key='ticker')

#start and end date
start_date=st.sidebar.date_input('Enter start business date')
if debug:st.write(f'start_date: {start_date}')

#check if the start date is a business day
if not is_business_day(start_date):st.warning('Error occured!')
end_date=st.sidebar.date_input('Enter end business date')
if debug:st.write(f'end_date: {end_date}')



