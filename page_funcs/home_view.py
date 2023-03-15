import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px
from plotly import graph_objects as go
from helper_funcs import data_parser, st_filters
from streamlit_extras.metric_cards import style_metric_cards
from st_vizzu import *


def show():
    df = data_parser.read_data()
    print(df.info())

    # Sidebar Filters
    st.sidebar.header("Filters")
    st.sidebar.write("**View Revenue/Volume**")
    view = st.sidebar.selectbox(
        "view", options=["Revenue", "Volume"], key="view", label_visibility="collapsed")

    filters = st_filters.filter_widgets(df)
    df = st_filters.filter_data(df, *filters)

    total_request_value = df['price'].sum()
    total_supplied_value = df[df['order_status'].isin(
        ["delivered", "shipped"])]['price'].sum()
    fr = np.round(total_supplied_value/total_request_value * 100, 2)

    st.header("Welcome to Your Ecommerce Insights Dashboard")
    st.subheader("Order Summary")

    col1, col2, col3 = st.columns(3, gap="small")

    col1.metric("**Requested Value**",
                value=f"$ {data_parser.clean_format(total_request_value)}")
    col2.metric("**Supplied Value**",
                value=f"$ {data_parser.clean_format(total_supplied_value)}")
    col3.metric("**Fulfillment Rate**", value=f"{fr} %")

    col1, col2, col3 = st.columns(3, gap="small")

    style_metric_cards()

    # tab1, tab2 = st.tabs(["Value", "Volume"])
    freq = st.selectbox("Select Frequency for Trend", options=["Daily", "Weekly", "Monthly"])

    if view == "Revenue":
        trend_data = df.groupby(by=[pd.Grouper(
            key="order_purchase_timestamp", freq=freq[0]), "order_status"]).agg({"price": "sum"}).reset_index()
        fig = px.line(trend_data, x="order_purchase_timestamp",
                      y="price", color="order_status", labels={"order_status": "Order Status"},
                      color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_layout(title=f" {freq} Revenue Trend",
                          xaxis_title="Order Date", yaxis_title="Revenue")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})

    if view == "Volume":
        trend_data = df.groupby(by=[pd.Grouper(
            key="order_purchase_timestamp", freq=freq[0]), "order_status"]).agg(Number_of_Orders=("order_purchase_timestamp", "count")).reset_index()
        fig = px.line(trend_data, x="order_purchase_timestamp",
                      y="Number_of_Orders", color="order_status", labels={"order_status": "Order Status"},
                      color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_layout(title=f" {freq} Count Trend",
                          xaxis_title="Order Date", yaxis_title="Number of Orders")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})
