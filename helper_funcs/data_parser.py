import pandas as pd
import numpy as np
import streamlit as st
import json
from haversine import haversine, Unit


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


@st.cache_data(show_spinner=False)
def read_geolocations(drop_duplicates=False):
    df = pd.read_csv("assets/data/geolocation_dataset.csv",
                     dtype={"geolocation_zip_code_prefix": "string"})
    # df["geolocation_zip_code_prefix_3_digits"] = df["geolocation_zip_code_prefix"].str[0:3]
    # df["geolocation_zip_code_prefix_3_digits"] = df["geolocation_zip_code_prefix_3_digits"].astype(
    #     int)
    if drop_duplicates:
        df = df.drop_duplicates(subset="geolocation_city")

    return df


@st.cache_data(show_spinner=False)
def read_data(add_geo_location=False):
    df = pd.read_parquet("assets/data/orders_data.parquet")

    df['order_purchase_timestamp'] = pd.to_datetime(
        df['order_purchase_timestamp'], yearfirst=True)
    df['order_approved_at'] = pd.to_datetime(
        df['order_approved_at'], yearfirst=True, )
    df['order_delivered_carrier_date'] = pd.to_datetime(
        df['order_delivered_carrier_date'], yearfirst=True, )
    df['order_delivered_customer_date'] = pd.to_datetime(
        df['order_delivered_customer_date'], yearfirst=True, )
    df['order_estimated_delivery_date'] = pd.to_datetime(
        df['order_estimated_delivery_date'], yearfirst=True, )
    df['shipping_limit_date'] = pd.to_datetime(
        df['shipping_limit_date'], yearfirst=True, )

    name_translation = pd.read_csv(
        "assets/data/product_category_name_translation.csv")
    df = df.merge(name_translation, how="inner", on="product_category_name")
    df.drop(columns='product_category_name', inplace=True)
    df.rename(
        columns={"product_category_name_english": "product_category_name"}, inplace=True)

    if add_geo_location:
        df = df.merge(read_geolocations(drop_duplicates=True), how="inner",
                    left_on="customer_city", right_on="geolocation_city")
        df.rename(
            columns={"geolocation_lat": "customer_lat", "geolocation_lng": "customer_lng"}, inplace=True)

        df = df.merge(read_geolocations(drop_duplicates=True), how="inner",
                                left_on="seller_city", right_on="geolocation_city")
        df.rename(
            columns={"geolocation_lat": "seller_lat", "geolocation_lng": "seller_lng"}, inplace=True)

        df['distance_covered'] = df.apply(lambda row: haversine(
            (row['seller_lat'], row['seller_lng']), (row['customer_lat'], row['customer_lng']), unit="mi"), axis=1)

    return df


@st.cache_data(show_spinner=False)
def months():
    with open("assets/data/dates.json") as f:
        dicts = json.load(f)

    return dicts["months"]


@st.cache_data(show_spinner=False)
def days():
    with open("assets/data/dates.json") as f:
        dicts = json.load(f)

    return dicts["days"]


# Removing the outliers
@st.cache_data()
def removeOutliers(data, col):
    Q3 = data[col].quantile(0.75)
    Q1 = data[col].quantile(0.25)
    IQR = Q3 - Q1
 
    lower_range = Q1 - (1.5 * IQR)
    upper_range = Q3 + (1.5 * IQR)
    
    filtered_data = data[(data[col] > lower_range) & (data[col] < upper_range)]
    
    return filtered_data
