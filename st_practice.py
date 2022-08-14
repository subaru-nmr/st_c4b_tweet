from re import S
import streamlit as st
import datetime
#import pandas as pd
#a=pd.read_csv('kions.csv', encoding='cp932',header=6)
#a.rename(columns={'Unnamed: 0':'年','Unnamed: 1':'月','Unnamed: 2':'日'})
st.title("st練習帳")

s = st.sidebar.container()

date = s.date_input(
    "When's your birthday",
    datetime.date(1979,7,6))
st.write('Your birthday is',date)