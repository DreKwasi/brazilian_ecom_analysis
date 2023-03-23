import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px
from helper_funcs import data_parser, styles, st_filters
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.annotated_text import annotated_text
from helper_funcs.st_plots import get_key_metrics
from helper_funcs import ml_models


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

styles.load_css_file("assets/styles/main.css")
styles.set_png_as_page_bg("assets/img/olist_logo.png")

df = data_parser.read_data(add_geo_location=True)


# Sidebar Filters
st.sidebar.header("Filters")
st.sidebar.write("**View price/Volume**")
view = st.sidebar.selectbox(
    "view", options=["Revenue", "Volume"], key="view", label_visibility="collapsed")
if view == "price":
    if st.sidebar.checkbox("Add Freight Value to Order"):
        df['price'] = df['price'] + df['freight_value']
filters = st_filters.filter_widgets(df)
df = st_filters.filter_data(df, *filters)

total_customers = df['customer_unique_id'].nunique()


# Count the number of unique customers who have not made a purchase in the last 30 days
churned_customers = len(df.loc[df['order_purchase_timestamp'] < df['order_purchase_timestamp'].max(
) - pd.Timedelta(days=365), 'customer_unique_id'].unique())

# Calculate the churn rate as a percentage of the total customer base
churn_rate = churned_customers / total_customers * 100


# Count the number of unique customers who have made a purchase in the last 30 days
retained_customers = len(df.loc[df['order_purchase_timestamp'] >= df['order_purchase_timestamp'].max(
) - pd.Timedelta(days=30), 'customer_unique_id'].unique())

# Calculate the customer retention rate as a percentage of the total customer base
customer_retention_rate = retained_customers / total_customers * 100


# Create a new dataframe containing only the orders that have been delivered
delivered_orders = df.loc[df['order_delivered_customer_date'].notnull()]

# Create a new dataframe containing only the first order for each customer
first_orders = delivered_orders.sort_values(
    'order_purchase_timestamp').groupby('customer_unique_id').first().reset_index()


# Create a new dataframe containing only the second order for each customer (if it exists)
second_orders = pd.merge(delivered_orders, first_orders[[
                         'customer_unique_id', 'order_purchase_timestamp']], on='customer_unique_id', suffixes=['', '_first'])
second_orders = second_orders.loc[(second_orders['order_purchase_timestamp'] <
                                   second_orders['order_purchase_timestamp_first'] + pd.Timedelta(days=365)), :]

# Count the number of unique customers who made a second purchase
renewed_customers = len(second_orders['customer_unique_id'].unique())

# Calculate the renewal rate as a percentage of the total number of customers
renewal_rate = (renewed_customers / total_customers) * 100

# Calculate the total revenue generated by all customers
total_revenue = df['price'].sum()

# Create a new dataframe containing only the orders that have been delivered
delivered_orders = df.loc[df['order_delivered_customer_date'].notnull()]

# Create a new dataframe containing only the first order for each customer
first_orders = delivered_orders.sort_values(
    'order_purchase_timestamp').groupby('customer_id').first().reset_index()

# Create a new dataframe containing only the second order for each customer (if it exists)
second_orders = pd.merge(delivered_orders, first_orders[[
                         'customer_id', 'order_purchase_timestamp']], on='customer_id', suffixes=['', '_first'])
second_orders = second_orders.loc[(second_orders['order_purchase_timestamp'] <
                                   second_orders['order_purchase_timestamp_first'] + pd.Timedelta(days=365)), :]

# Calculate the total revenue generated by customers who made a second purchase
renewal_revenue = second_orders['price'].sum()

# Calculate the revenue renewal rate as a percentage of the total revenue
revenue_renewal_rate = renewal_revenue / total_revenue * 100

st.header("Customer Insights")
st.subheader("Overview")

col1, col2 = st.columns(2, gap="small")
col1.metric("**Total Number of Customers**",
            value=f"{data_parser.clean_format(total_customers)} ")

col2.metric("**Total Number of Active Customers**",
            value=f"{data_parser.clean_format(retained_customers)} ")

col1, col2, col3, col4 = st.columns(4, gap="small")
col1.metric("**Customer Retention Rate**",
            value=f"{data_parser.clean_format(customer_retention_rate)} %")
col2.metric("**Customer Churn Rate**",
            value=f"{data_parser.clean_format(churn_rate)} %")
col3.metric("**Customer Renewal Rate**",
            value=f"{data_parser.clean_format(renewal_rate)} %")
col4.metric("**Revenue Renewal Rate**",
            value=f"{data_parser.clean_format(revenue_renewal_rate)} %")
style_metric_cards()


st.subheader("Visualization")

tab1, tab2 = st.tabs(["Customer Onboarding Trend",
                     "Product Perference Per Customer"])

with tab1:
    freq = st.selectbox("Select Frequency for Trend", options=[
        "Daily", "Weekly", "Monthly"])
    cus_df = df.groupby(by=pd.Grouper(key="order_approved_at", freq=freq[0])).agg(
        Number_of_Customers=("customer_unique_id", "count")).reset_index()

    fig = px.line(cus_df, x="order_approved_at", y="Number_of_Customers")
    fig.update_layout(
        showlegend=False,
        title=f"{freq} Customer Traffic by Order Day",
        hoverlabel=dict(bgcolor="white", font_size=14,
                        font_family="Rockwell"),
    )
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


with tab2:
    prod_df = df.drop_duplicates(subset="customer_unique_id")
    prod_df = (
        prod_df.groupby(by="product_category_name").agg(
            num_customers=("customer_unique_id", "count")).reset_index()
    )

    num1, num2 = st.columns([1, 1])

    with num1:
        order = st.selectbox(f"Select Sort Order (Volume)",
                             options=["Top", "Bottom"])
        order_ = True if order == "Bottom" else False

    with num2:
        num_fal = st.slider(
            f"Number of Categories to Show", min_value=5, max_value=prod_df["product_category_name"].nunique())

    top_df = prod_df.sort_values(by="num_customers", ascending=order_)[
        :num_fal
    ]

    line1 = st.empty()

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    top_value, avg, med, min_value, max_value = get_key_metrics(
        top_df, "product_category_name", "num_customers")

    perc = np.round(top_value / total_customers * 100)
    line1.markdown(
        f"""##### The {order} {num_fal} Categories Were Requested by :green[{perc}% ({data_parser.clean_format(top_value)} Customers)] of the Total Customers :green[({data_parser.clean_format(total_customers)} Customers)]"""
    )

    with col1:
        annotated_text(
            "Average Value: ", (f"{data_parser.clean_format(avg)}",
                                "value", "#83c9ff")
        )

    with col2:
        annotated_text(
            "Median Value: ", (f"{data_parser.clean_format(med)}",
                               "value", "#83c9ff")
        )

    with col3:
        annotated_text(
            "Min Value: ", (f"{data_parser.clean_format(min_value)}",
                            "value", "#83c9ff")
        )

    with col4:
        annotated_text(
            "Max Value: ", (f"{data_parser.clean_format(max_value)}",
                            "value", "#83c9ff")
        )

    fig = px.bar(
        top_df,
        x="product_category_name",
        y="num_customers",
        color="product_category_name",
        template="presentation",
    )
    fig.update_layout(
        showlegend=False,
        title=f"Customer Interest By Product Category ",
        hoverlabel=dict(bgcolor="white", font_size=14,
                        font_family="Rockwell"),
    )
    fig.update_xaxes(title_text="Product Category Name")
    fig.update_yaxes(title_text="Number of Customers")
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})

st.subheader("Customer Segmentation")

colorscales = px.colors.named_colorscales()
colorscale = st.selectbox(
    "Select Preferred Color Scale", options=colorscales)

col1, col2 = st.columns(2)
# Geographic Segmentation


with col1:
    n_clusters = st.slider("Select Number of Clusters", min_value=2, value=3, max_value=5, key="geo_cluster")
    
    geo_df = df.groupby(
        by=["customer_lat", "customer_lng"]).first().reset_index()
    geo_df = ml_models.cluster(n_clusters=n_clusters, df=geo_df, columns=[
                               "customer_lat", "customer_lng"])
                               
    fig = px.scatter_mapbox(geo_df, lat="customer_lat", lon="customer_lng", color="cluster",
                            labels={"customer_lat": "Latitude",
                                    "customer_lng": "Longitude"},
                            color_continuous_scale=colorscale,
                            zoom=3.5, mapbox_style="open-street-map", height=650)
    fig.update_layout(title=f" Geographic Segmentation of Customers",
                      hoverlabel=dict(bgcolor="white", font_size=14, font_family="Rockwell"),)
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


with col2:
    n_clusters = st.slider("Select Number of Clusters", min_value=2, value=2, max_value=5, key="rev_cluster")
    # # calculate the total price for each customer
    # customer_price = df.groupby('customer_unique_id')['price'].sum()

    # # calculate the number of orders for each customer
    # customer_orders = df.groupby('customer_unique_id')['order_id'].nunique()

    # # calculate the AOV and APF for each customer
    # aov = customer_price / customer_orders
    # apf = customer_orders / df['customer_unique_id'].nunique()
    # clv = aov * apf * 12 * 5
    # clv = clv.reset_index()
    # clv.rename(columns={0: "customer_lifetime_value"}, inplace=True)
    # geo_df = df.merge(clv, how="inner", on="customer_unique_id")

    # geo_df = geo_df.groupby(["customer_lat", "customer_lng"]).agg(
    #     {"customer_lifetime_value": "sum"}).reset_index()

    geo_df = df.groupby(["customer_lat", "customer_lng"]).agg(
        {"price": "sum"}).reset_index()
    geo_df = ml_models.cluster(n_clusters=n_clusters, df=geo_df, columns=[
                               "customer_lat", "customer_lng", "price"])

    fig = px.scatter_mapbox(geo_df, lat="customer_lat", lon="customer_lng", color="cluster",
                            labels={"customer_lat": "Latitude",
                                    "customer_lng": "Longitude",
                                    "price": "Revenue"},
                            color_continuous_scale=colorscale, size="price",
                            zoom=3.5, mapbox_style="open-street-map", height=650)
    fig.update_layout(title=f" Customer Revenue Segmentation",
                      hoverlabel=dict(bgcolor="white", font_size=14, font_family="Rockwell"),)
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})
