#import libraries

import pandas as pd
import yfinance as yf
import streamlit as st

st.page_page_config(layout='wide')

#functions to use in the later part
##check if the given date is business day or not
def is_business_day(date):
  '''
  This function checks if the given date is a business day or not
  '''
  return pd.to_datetime(date).weekday()<5

def get_selling_date_and_close(buy_index,holding_period):
  '''
  This function returns the selling date for a given buy date and holding period
  '''
  try:
    sell_index=buy_index+holding_period
    sell_date=df.loc[sell_index,'Date']
    sell_price=df.loc[sell_index,'Close']
    return sell_date,sell_price
  except:
    return None,None

def get_df_between_buy_sell(buy_date,sell_date):
  '''
  This function returns the dataframe between the buy date and sell date
  '''
  temp_df=df[(df['Date']>=buy_date)&(df['Date']<=sell_date)]
  return temp_df

#user input ticker, start_date, end_date,volume_threshold%,%change on the end date,holding period
debug=True
#ask the user for the ticker
user_ticker=st.sidebar.text_input("Enter a ticker",value='TSLA',key='ticker')

if debug:st.write(f'ticker: {user_ticker}')

#start and end date
start_date=st.sidebar.date_input('Enter start business date',value=pd.to_datetime("2024/01/02"))
if debug:st.write(f'start_date: {start_date}')

#check if the start date is a business day
if not is_business_day(start_date):
   st.warning('Start date needs to be a valid business day !',icon='⚠️')
   st.stop()



#last_business_day
date_today=pd.to_datetime('today').normalize().date()
if debug:st.write(f'today: {date_today}')
bdate=pd.bdate_range(end=date_today,periods=1)[0]
if debug:st.write(f'last_business_day: {bdate}')
end_date=st.sidebar.date_input('Enter end business date',value=bdate)
if debug:st.write(f'end_date: {end_date}')

if not is_business_day(end_date):
   st.warning('End date needs to be a valid business day !',icon='⚠️')
   st.stop()

#yfinance is exclusive for end date so making it inclusive
temp_end_date=pd.to_datetime(end_date)+pd.Timedelta(days=1)

if debug:st.write(f'temp_end_date: {temp_end_date}')
#assert that end date is later than the start date
if end_date<start_date:
   st.warning('End date needs to be later than Start date !',icon='⚠️')
   st.stop()

#downloading the stock values between start and end date 
try:
    df_temp=yf.download(user_ticker,start=start_date,end=temp_end_date,group_by='ticker')
except:
   st.warning('Error occured try again with valid ticker !',icon='⚠️')
   st.stop()

if df_temp.empty:
   st.warning('Error occured try again with a valid ticker !',icon='⚠️')
   st.stop()
#reset to keep the date as the column
df_temp=df_temp.reset_index(drop=False)
if debug:st.write(df_temp)
if debug:st.write(df_temp.columns)

#might need to change this part for the remote
remote=False
if remote:
   df=df_temp[user_ticker]
else:
   df=df_temp.copy()


#difference between start and end date
days_diff=int((end_date-start_date).days)
if debug:st.write(f'Differences between end and start date: {days_diff}')

holding_time=st.sidebar.number_input('Enter holding business days',value=10,min_value=0,max_value=days_diff,format='%d')

if debug:st.write(f'holding days {holding_time}')
#st.stop()

#ensuring that the holding time is less than the difference between start and end date
if float(holding_time) > days_diff:
   st.warning('Holding days  higher than the difference of  end_date and start_date',icon='⚠️')
   st.stop()


#volume threshold percentage
volume_threshold=st.sidebar.number_input("Enter the volume threshold %",value=20.0,min_value=0.0)
if debug:st.write(f'volume_threshold: {volume_threshold}')
#volume threshold percentage
pct_threshold=st.sidebar.number_input("Enter the percent threshold %",value=2.0,min_value=0.0)
if debug:st.write(f'pct_threshold: {pct_threshold}')


#get daily change % and 20 day average volume
df.loc[:,'daily_change%']=df['Close'].copy().pct_change()*100
df.loc[:,'volume_avearge_20_days']=df['Volume'].copy().rolling(window=20).mean()
df.loc[:,'volume_condition']=df['Volume'].copy()>df['volume_avearge_20_days'].copy()*(100+volume_threshold)/100
df.loc[:,'percent_change_condition']=df['daily_change%'].copy()>pct_threshold
df.loc[:,'buy_condition']=(df['volume_condition'].copy() & df['percent_change_condition'].copy())

#filter the dataframe with df_buy
df_buy=df[df['buy_condition']==True]

#getting selling date and price
df_buy.loc[:,'selling_date']=df_buy.index.copy().map(lambda buy_index:get_selling_date_and_close(buy_index,holding_time)[0])
df_buy.loc[:,'selling_price']=df_buy.index.copy().map(lambda buy_index:get_selling_date_and_close(buy_index,holding_time)[1])
df_buy.loc[:,'return(%)']=(df_buy['selling_price'].copy()/df_buy['Close'].copy()-1)*100
df_buy.insert(1,'ticker',user_ticker)

#getting final df 
selected_columns=['ticker','Date','Close','selling_date','selling_price','return(%)']
df_final=df_buy[selected_columns].reset_index(drop=True)
df_final=df_final.rename(columns={'Close':'buying_price','Date':'buying_date'}).round(2)

#modify the buying and selling date
df_final['buying_date']=df_final['buying_date'].dt.date
df_final['selling_date']=df_final['selling_date'].dt.date
df_final.index=range(1,len(df_final)+1)
df_final.index.name='S.N.'


if debug:st.write(df_final)