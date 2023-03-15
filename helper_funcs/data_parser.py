import pandas as pd
import numpy as np
import streamlit as st


def clean_format(num):

    num = float(f"{num:.3g}")
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    num = f"{num:f}".rstrip("0").rstrip(".")
    return f"{num}{['', 'K', 'M', 'B', 'T'][magnitude]}"


def get_freq(input):
    freq_dict = {"Daily": "D", "Weekly": "W", "Monthly": "MS", "Yearly": "Y"}
    return freq_dict[input]

st.cache_data(show_spinner=False)
def read_data():
    df = pd.read_parquet("assets/data/orders_data.parquet")   

    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], yearfirst=True )
    df['order_approved_at'] = pd.to_datetime(df['order_approved_at'], yearfirst=True, )
    df['order_delivered_carrier_date'] = pd.to_datetime(df['order_delivered_carrier_date'], yearfirst=True, )
    df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'], yearfirst=True, )
    df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'], yearfirst=True, )
    df['shipping_limit_date'] = pd.to_datetime(df['shipping_limit_date'], yearfirst=True, )
    
    name_translation = pd.read_csv("assets/data/product_category_name_translation.csv")
    df = df.merge(name_translation, how="inner", on="product_category_name")
    df.drop(columns='product_category_name', inplace=True)
    df.rename(columns={"product_category_name_english":"product_category_name"}, inplace=True)
    

    return df


