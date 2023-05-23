import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px
from helper_funcs import data_parser, styles, st_filters
from streamlit_extras.metric_cards import style_metric_cards
import plotly.graph_objects as go
from helper_funcs import ml_models


st.set_page_config(page_icon="🧮", layout="wide",
                   initial_sidebar_state="expanded")

styles.load_css_file("assets/styles/main.css")
styles.set_png_as_page_bg("assets/img/olist_logo.png")

df = data_parser.read_data(add_geo_location=True)
total_num_orders = df['order_id'].nunique()

df = df[df['order_status'] == "delivered"]
customer_date_null_mask = df['order_delivered_customer_date'].isna()
df.loc[customer_date_null_mask, 'order_delivered_customer_date'] = df.loc[customer_date_null_mask,
                                                                          'order_delivered_carrier_date']
df.loc[customer_date_null_mask,
       'order_delivered_customer_date'] = df.loc[customer_date_null_mask, 'order_approved_at']
df = df[df["order_delivered_customer_date"] >= df["order_approved_at"]]

# Sidebar Filters

header = st.sidebar.empty()
selectbox = st.sidebar.empty()


st.sidebar.header("Filters")
filters = st_filters.filter_widgets(df)
df = st_filters.filter_data(df, *filters)


df["delivery_time"] = df["order_delivered_customer_date"] - df["order_approved_at"]
clean_df = df.drop_duplicates(subset=["order_id", "product_id"]).copy()
total_num = clean_df['order_id'].nunique()
avg_delivery_time = df["delivery_time"].mean().days
avg_distance = df["distance_covered"].mean()

st.header("Distribution Insights 🚴")
st.subheader("Overview")

col1, col2, col3 = st.columns(3, gap="small")

col1.metric("**Total Deliveries Completed**",
            value=f"{data_parser.clean_format(total_num)}", delta=f"{data_parser.clean_format(total_num-total_num_orders)} orders")
col2.metric("**Average Delivery Time (Days)**",
            value=f"{avg_delivery_time}")

col3.metric("**Daily Average Distance (miles)**",
            value=f"{data_parser.clean_format(avg_distance)}")

# col1, col2, col3 = st.columns(3, gap="small")

style_metric_cards()


st.subheader("Visualization")
clean_df = df.drop_duplicates(subset=["order_id", "product_id"]).copy()
clean_df['delivery_time'] = clean_df['delivery_time'].dt.days

freq = st.selectbox("Select Frequency for Trend", options=[
    "Daily", "Weekly", "Monthly"], index=1)

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

vars_dict = {
    "Delivery Time (Days)": "delivery_time",
    "Distance Covered (Miles)": "distance_covered"
}


st.subheader("Distribution Breakdown")
# st.dataframe(clean_df)
st.write("Select Variable to Display Distribution")
variable = st.selectbox(
    label='vars', options=vars_dict.keys(), label_visibility="collapsed")

tab1, tab2 = st.tabs(["Overall Distribution", "Daily Distribution"])
clean_df['Days'] = clean_df['order_delivered_customer_date'].dt.day_name()


with tab1:
    plt_df = clean_df
    if st.checkbox("Remove Outliers (Using IQR)", key="check_a"):
        plt_df = data_parser.removeOutliers(clean_df, vars_dict[variable])
    st.write("Select Number of Bins")
    bins = st.slider('bins', min_value=50, max_value=round(
        np.sqrt(clean_df.shape[0])), label_visibility="collapsed")

    fig = px.histogram(plt_df, x=vars_dict[variable],
                       nbins=bins, title=f"Distribution of {variable}")
    fig.update_layout(hoverlabel=dict(
        bgcolor="white", font_size=14, font_family="Rockwell"),)
    fig.update_xaxes(title=variable)
    fig.update_yaxes(title="Counts")
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})

with tab2:

    daily_dist_df = clean_df.groupby(by=[pd.Grouper(key='order_delivered_customer_date', freq='D'),
                                         "Days", "order_id"]).agg({vars_dict[variable]: "sum"}).reset_index()

    daily_dist_df["Days"] = pd.Categorical(
        daily_dist_df["Days"], categories=data_parser.days(), ordered=True
    )
    daily_dist_df = daily_dist_df.sort_values(by='Days', ascending=True)

    plt_df = daily_dist_df.copy()

    if st.checkbox("Remove Outliers (Using IQR)", key="check_b"):
        plt_df = data_parser.removeOutliers(daily_dist_df, vars_dict[variable])

    fig = px.box(plt_df, x='Days', y=vars_dict[variable],
                 color='Days', points="outliers", title=f"Daily Distribution of {variable}")
    fig.update_layout(hoverlabel=dict(
        bgcolor="white", font_size=14, font_family="Rockwell"),)
    fig.update_xaxes(title="Days")
    fig.update_yaxes(title=variable)

    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})

st.subheader("Distribution Maps")
colorscales = px.colors.named_colorscales()
colorscale = st.selectbox(
    "Select Preferred Color Scale", options=colorscales)
col1, col2 = st.columns(2)

with col1:
    geo_df = clean_df.groupby(by=['customer_city', "customer_lat", "customer_lng"])[
        'delivery_time'].mean().reset_index()

    fig = px.density_mapbox(geo_df, lat="customer_lat", lon="customer_lng", z="delivery_time", radius=10, zoom=3.5,
                            labels={"customer_lat": "latitude", "customer_lng": "longitude",
                                    "delivery_time": "Delivery_Time"},
                            mapbox_style="open-street-map", color_continuous_scale=colorscale,
                            range_color=[geo_df['delivery_time'].min(), geo_df['delivery_time'].max()], height=650)
    fig.update_layout(title=f"Heatmap of Delivery Times for Customer Cities", hoverlabel=dict(
                            bgcolor="white", font_size=14, font_family="Rockwell"),)
    fig.update_traces(
        hovertemplate="Mean Delivery Days: %{z:.2f} <br> Latitude: %{lat} <br> Longitude: %{lon}")
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})

header.write("**Hierarchical Clustering**")
n_clusters = selectbox.slider("Select Number of Clusters",
                              min_value=2, value=3, max_value=5, key="rev_cluster")
with col2:
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
