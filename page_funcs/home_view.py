import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px
from plotly import graph_objects as go
from helper_funcs import data_parser
from streamlit_extras.metric_cards import style_metric_cards


def show():
    df = data_parser.read_data()

    # Sidebar Filters
    st.sidebar.header("Filters")

    payment_types = df['payment_type'].unique()
    st.sidebar.write("**Payment Type**")
    sel_payment_type = st.sidebar.multiselect(
        label="payment_type", key="payment_type", options=payment_types, label_visibility="collapsed")
    if len(sel_payment_type) > 0:
        df = df[df['payment_type'].isin(sel_payment_type)]

    prod_category = df['product_category_name'].unique()
    st.sidebar.write("**Product Categories**")
    sel_prod_category = st.sidebar.multiselect(
        label="product_category_name", key="product_category_name", options=prod_category, label_visibility="collapsed")
    if len(sel_prod_category) > 0:
        df = df[df['product_category_name'].isin(sel_prod_category)]

    col_seller_city, col_seller_state = st.sidebar.columns(2)

    with col_seller_city:
        seller_city = df['seller_city'].unique()
        st.write("**Seller City**")
        sel_seller_city = st.multiselect(
            "seller_city", key="seller_city", options=seller_city, label_visibility="collapsed")
        if len(sel_seller_city) > 0:
            df = df[df['seller_city'].isin(sel_seller_city)]

    with col_seller_state:
        seller_state = df['seller_state'].unique()
        st.write("**Seller State**")
        sel_seller_state = st.multiselect(
            "seller_state", key="seller_state", options=seller_state, label_visibility="collapsed")
        if len(sel_seller_state) > 0:
            df = df[df['seller_state'].isin(sel_seller_state)]

    col_cus_city, col_cus_state = st.sidebar.columns(2)

    with col_cus_city:
        customer_city = df['customer_city'].unique()
        st.write("**Customer City**")
        sel_customer_city = st.multiselect(
            "customer_city", key="customer_city", options=customer_city, label_visibility="collapsed")
        if len(sel_customer_city) > 0:
            df = df[df['customer_city'].isin(sel_customer_city)]

    with col_cus_state:
        customer_state = df['customer_state'].unique()
        st.write("**Customer State**")
        sel_customer_state = st.multiselect(
            "customer_state", key="customer_state", options=customer_state, label_visibility="collapsed")
        if len(sel_customer_state) > 0:
            df = df[df['customer_city'].isin(sel_customer_state)]

    # payment_types = df['payment_type'].unique()
    # st.sidebar.write("**Payment Type**")
    # payment_type = st.sidebar.multiselect(
    #     "payment_type", key="payment_type", options=payment_types, label_visibility="collapsed")
    # if len(payment_type) > 0:
    #     df = df[df['payment_type'].isin(payment_type)]

    total_request_value = data_parser.clean_format(df['price'].sum())

    st.header("Ecommerce Dashboard")
    st.subheader("Quick Overview")

    col1, col2, col3 = st.columns(3, gap="small")

    col1.metric("**Total Requested Value**", value=f"$ {total_request_value}")

    style_metric_cards()
