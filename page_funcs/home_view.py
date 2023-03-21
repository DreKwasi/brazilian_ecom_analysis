import streamlit as st
import pandas as pd
import numpy as np
import plotly_express as px
from plotly import graph_objects as go
from helper_funcs import data_parser, st_filters
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.annotated_text import annotated_text
from helper_funcs import st_plots


def show():
    df = data_parser.read_data()

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

    total_request_value = df['price'].sum()
    total_supplied_value = df[df['order_status'].isin(
        ["delivered", "shipped"])]['price'].sum()
    fr = np.round(total_supplied_value/total_request_value * 100, 2)

    st.header("Ecommerce Dashboard")
    st.subheader("Order Summary")

    col1, col2, col3 = st.columns(3, gap="small")

    col1.metric("**Requested Value**",
                value=f"$ {data_parser.clean_format(total_request_value)}")
    col2.metric("**Supplied Value**",
                value=f"$ {data_parser.clean_format(total_supplied_value)}")
    col3.metric("**Fulfillment Rate**", value=f"{fr} %")

    col1, col2, col3 = st.columns(3, gap="small")

    style_metric_cards()

    if view == "Revenue":
        st_plots.revenue_plots(df)
    if view == "Volume":
        st_plots.volume_plots(df)

    time_match = {"Order Purchase Time": "order_purchase_timestamp",
                  "Order Delivered Carrier Date": "order_delivered_carrier_date",
                  "Order Delivered Customer Date": "order_delivered_customer_date"}
    st.write("**Select Date Column**")
    sel_col = st.selectbox(
        "sel_date_col", options=time_match.keys(), label_visibility="collapsed")
    sel_col = time_match[sel_col]
    ht_df = df.groupby(sel_col).agg(
        num_orders=("order_id", "count")).reset_index()

    # Day vs Hour
    # st.subheader("Testing Frequency")
    tab1, tab2, tab3 = st.tabs(
        ["Daily vs Hourly Comparison", "Daily vs Weekly Comparison",
            "Monthly vs Weekly Comparison"]
    )
    colorscales = px.colors.named_colorscales()
    with tab1:
        ht_df["Days"] = pd.Categorical(
            ht_df[sel_col].dt.day_name(), categories=data_parser.days(), ordered=True
        )
        ht_df["Hours"] = ht_df[sel_col].dt.hour

        dh_df = (
            ht_df.groupby(by=["Days", "Hours"])
            .agg({"num_orders": "sum"})
            .reset_index()
        )

        dh_df = dh_df.pivot(
            index="Hours", columns="Days", values="num_orders"
        )
        scale = st.selectbox(
            "Select A Color Scale", options=colorscales, index=4, key="t1"
        )

        fig = px.imshow(
            dh_df.values.tolist(),
            labels=dict(x="Day of Week", y="Purchase Hour",
                        color="Number of Orders"),
            x=dh_df.columns.tolist(),
            y=dh_df.index.tolist(),
            # labels={"num_orders":"Number of Orders"},
            color_continuous_scale=scale,
            title=f"Activity Heatmap: Daily vs Hourly Analysis",
            template="presentation",
        )

        with fig.batch_update():
            fig.update_xaxes(side="top")
            fig.update_layout(
                margin=dict(l=0, r=0, t=100, b=0),
                hoverlabel=dict(bgcolor="white", font_size=14,
                                font_family="Rockwell"),
                hovermode="x",
            )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with tab2:
        ht_df["Weeks"] = (ht_df[sel_col].dt.day - 1) // 7 + 1

        # Week vs Day
        dw_df = (
            ht_df.groupby(by=["Days", "Weeks"])
            .agg({"num_orders": "sum"})
            .reset_index()
        )

        dw_df = dw_df.pivot(
            index="Weeks", columns="Days", values="num_orders"
        )
        scale = st.selectbox(
            "Select A Color Scale", options=colorscales, index=4, key="t2"
        )
        fig = px.imshow(
            dw_df.values.tolist(),
            labels=dict(x="Day of Week", y="Weeks", color="num_orders"),
            x=dw_df.columns.tolist(),
            y=dw_df.index.tolist(),
            # label={"num_orders":"Number of Orders"},
            color_continuous_scale=scale,
            title=f"Activity Heatmap: Daily vs Weekly Analysis",
            template="presentation",
        )

        with fig.batch_update():
            fig.update_xaxes(side="top")
            fig.update_layout(
                margin=dict(l=0, r=0, t=100, b=0),
                hoverlabel=dict(bgcolor="white", font_size=14,
                                font_family="Rockwell"),
                hovermode="x",
                xaxis_title="Day of Week",
                yaxis_title="Week of Month"
            )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )

    with tab3:
        # Month vs Week
        ht_df["Months"] = pd.Categorical(
            ht_df[sel_col].dt.month_name(), categories=data_parser.months(), ordered=True
        )
        mw_df = (
            ht_df.groupby(by=["Months", "Weeks"])
            .agg({"num_orders": "sum"})
            .reset_index()
        )

        mw_df = mw_df.pivot(
            index="Weeks", columns="Months", values="num_orders"
        )

        scale = st.selectbox(
            "Select A Color Scale", options=colorscales, index=4, key="t3"
        )

        fig = px.imshow(
            mw_df.values.tolist(),
            labels=dict(x="Months", y="Weeks", color="num_orders"),
            x=mw_df.columns.tolist(),
            y=mw_df.index.tolist(),
            color_continuous_scale=scale,
            title=f"Activity Heatmap: Weekly vs Monthly Analysis",
            template="presentation",
        )

        with fig.batch_update():
            fig.update_xaxes(side="top")
            fig.update_layout(
                margin=dict(l=0, r=0, t=100, b=0),
                hoverlabel=dict(bgcolor="white", font_size=14,
                                font_family="Rockwell"),
                hovermode="x",
            )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False},
        )
