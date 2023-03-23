import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px
from helper_funcs import data_parser, styles, st_filters
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go
from helper_funcs import ml_models


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

styles.load_css_file("assets/styles/main.css")
styles.set_png_as_page_bg("assets/img/olist_logo.png")

df = data_parser.read_data(add_geo_location=True)

df = df[df['order_status'] == "delivered"]
customer_date_null_mask = df['order_delivered_customer_date'].isna()
df.loc[customer_date_null_mask, 'order_delivered_customer_date'] = df.loc[customer_date_null_mask,
                                                                          'order_delivered_carrier_date']
df.loc[customer_date_null_mask,
       'order_delivered_customer_date'] = df.loc[customer_date_null_mask, 'order_approved_at']
df = df[df["order_delivered_customer_date"] >= df["order_approved_at"]]

# Sidebar Filters
st.sidebar.header("Filters")
st.sidebar.write("**View Revenue/Volume**")
view = st.sidebar.selectbox(
    "view", options=["Revenue", "Volume"], key="view", label_visibility="collapsed")
if view == "Revenue":
    if st.sidebar.checkbox("Add Freight Value to Order"):
        df['price'] = df['price'] + df['freight_value']
filters = st_filters.filter_widgets(df)
df = st_filters.filter_data(df, *filters)


df["delivery_time"] = df["order_delivered_customer_date"] - df["order_approved_at"]
avg_delivery_time = df["delivery_time"].mean().days

avg_distance = df["distance_covered"].mean()

st.header("Distribution Insights 🚴")
st.subheader("Overview")

col1, col2, col3 = st.columns(3, gap="small")

col1.metric("**Average Delivery Time (Days)**",
            value=f"{avg_delivery_time}")

col2.metric("**Daily Average Distance (miles)**",
            value=f"{data_parser.clean_format(avg_distance)}")

col1, col2, col3 = st.columns(3, gap="small")

style_metric_cards()


st.subheader("Visualization")
clean_df = df.drop_duplicates(subset=["order_id", "product_id"]).copy()
clean_df['delivery_time'] = clean_df['delivery_time'].dt.days

freq = st.selectbox("Select Frequency for Trend", options=[
    "Daily", "Weekly", "Monthly"])

col1, col2 = st.columns(2)
with col1:

    trend_data = clean_df.groupby(by=pd.Grouper(
        key="order_approved_at", freq=freq[0])).agg(Distance_Covered=("distance_covered", "mean"), Mean_Delivery_Time=("delivery_time", "mean")).reset_index()

    fig = px.line(trend_data, x="order_approved_at",
                  y="Mean_Delivery_Time", color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(title=f" {freq} Trend of Mean Delivery Times",
                      xaxis_title="Date Approved", yaxis_title="Mean Delivery Time (Days)",
                      hovermode="x",
                      hoverlabel=dict(
                            bgcolor="white", font_size=14, font_family="Rockwell"),
                      )
    fig.update_traces(hovertemplate="%{x} <br> Mean_Delivery Time(Days): %{y}")
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})

with col2:
    fig = px.line(trend_data, x="order_approved_at",
                  y="Distance_Covered", color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(title=f" {freq} Trend of Mean Distance Covered",
                      xaxis_title="Date Approved", yaxis_title="Mean Distance Covered (Miles)",
                      hovermode="x",
                      hoverlabel=dict(
                            bgcolor="white", font_size=14, font_family="Rockwell"),
                      )
    fig.update_traces(
        hovertemplate="%{x} <br> Mean Distance Covered (Miles): %{y}")
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


colorscales = px.colors.named_colorscales()
colorscale = st.selectbox(
    "Select Preferred Color Scale", options=colorscales)
col1, col2 = st.columns(2)

with col1:
    n_clusters = st.slider("Select Number of Clusters",
                           min_value=2, value=3, max_value=5, key="city_cluster")

    geo_df = clean_df.groupby(by=['customer_city', "customer_lat", "customer_lng"])[
        'delivery_time'].mean().reset_index()

    geo_df = ml_models.cluster(n_clusters=n_clusters, df=geo_df, columns=[
                               'customer_city', "customer_lat", "customer_lng", "delivery_time"])

    fig = px.density_mapbox(geo_df, lat="customer_lat", lon="customer_lng", z="delivery_time", radius=10, zoom=3.5,
                            labels={"customer_lat": "latitude", "customer_lng": "longitude",
                                    "delivery_time": "Delivery_Time"},
                            mapbox_style="stamen-terrain", color_continuous_scale=colorscale,
                            range_color=[geo_df['delivery_time'].min(), geo_df['delivery_time'].max()], height=650)
    fig.update_layout(title=f"Heatmap of Delivery Times for Customer Cities", hoverlabel=dict(
                            bgcolor="white", font_size=14, font_family="Rockwell"),)
    fig.update_traces(
        hovertemplate="Mean Delivery Days: %{z:.2f} <br> Latitude: %{lat} <br> Longitude: %{lon}")
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


with col2:
    n_clusters = st.slider("Select Number of Clusters",
                           min_value=2, value=3, max_value=5, key="rev_cluster")

    geo_df = clean_df.groupby(by=["customer_lat", "customer_lng"])[
        'distance_covered'].mean().reset_index()

    geo_df = ml_models.cluster(n_clusters=n_clusters, df=geo_df, columns=[
                               "customer_lat", "customer_lng", "distance_covered"])

    fig = px.scatter_mapbox(geo_df, lat="customer_lat", lon="customer_lng", color="cluster",
                            labels={"distance_covered": "Distance Covered",
                                    "customer_lat": "Latitude", "customer_lng": "Longitude"},
                            color_continuous_scale=colorscale,
                            zoom=3.5, size_max=15, size="distance_covered", mapbox_style="open-street-map", height=650)
    fig.update_layout(title=f"Clustering Customer Cities Based on Distance from Seller Cities",
                      hoverlabel=dict(bgcolor="white", font_size=14, font_family="Rockwell"),)
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})
