import streamlit as st
import plotly_express as px
from streamlit_extras.annotated_text import annotated_text
from . import data_parser
import pandas as pd
import numpy as np


def get_key_metrics(top_df, city_, metric):
    top_value = top_df[metric].sum()
    avg = np.round(top_value / top_df[city_].nunique())
    med = np.percentile(top_df[metric], 50)
    min_value = top_df[metric].min()
    max_value = top_df[metric].max()
    return top_value, avg, med, min_value, max_value


def revenue_plots(df):
    tab1, tab2 = st.tabs(["Monthly Revenue Comparison", "Revenue Trend"])
    with tab1:
        trend_data = df.groupby(by=[pd.Grouper(
            key="order_purchase_timestamp", freq="MS"), "order_status"]).agg({"price": "sum"}).reset_index()

        fig = px.bar(trend_data, x="order_purchase_timestamp",
                     y="price", color="order_status", labels={"order_status": "Order Status"},
                     color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_layout(title=f"M-o-M Sales Revenue ",
                          xaxis_title="Order Date", yaxis_title="Revenue",
                          hovermode="x",
                          hoverlabel=dict(
                                bgcolor="white", font_size=14, font_family="Rockwell"),
                          )
        fig.update_traces(hovertemplate="%{x} <br> Revenue: %{y}")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})
    with tab2:
        freq = st.selectbox("Select Frequency for Trend", options=[
            "Daily", "Weekly", "Monthly"])
        trend_data = df.groupby(by=[pd.Grouper(
            key="order_purchase_timestamp", freq=freq[0]), "order_status"]).agg({"price": "sum"}).reset_index()
        fig = px.line(trend_data, x="order_purchase_timestamp",
                      y="price", color="order_status", labels={"order_status": "Order Status"},
                      color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_layout(title=f" {freq} Revenue Trend",
                          xaxis_title="Order Date", yaxis_title="Revenue",
                          hovermode="x",
                          hoverlabel=dict(
                                bgcolor="white", font_size=14, font_family="Rockwell"),
                          )
        fig.update_traces(hovertemplate="%{x} <br> Revenue: %{y}")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})

    # Regional Analysis
        # Tests/seller_states
    tab1, tab2 = st.tabs(["State Performance", "City Performance"])

    with tab1:
        ss_df = (
            df.groupby(by=["seller_state", "customer_state"])
            .agg({"price": "sum"})
            .reset_index()
        )

        num1, num2, num3 = st.columns([1, 1, 1])
        with num1:
            state = st.selectbox(f"Select State Type (Revenue)",
                                 options=["Customer State", "Seller State"])
            state_ = "customer_state" if state == "Customer State" else "seller_state"

        with num2:
            order = st.selectbox(f"Select State Sort Order (Revenue)",
                                 options=["Top", "Bottom"])
            order_ = True if order == "Bottom" else False

        with num3:
            num_fal = st.slider(
                f"Select No. of States to Show", min_value=5, max_value=ss_df[state_].nunique())

        top_df = ss_df.groupby(by=state_).agg({"price": "sum"}).reset_index().sort_values(by="price", ascending=order_)[
            :num_fal
        ]

        sliced_df = ss_df[ss_df[state_].isin(
            top_df[state_].tolist())]
        sliced_df = sliced_df.sort_values(
            by="price", ascending=order_)
        
        line1 = st.empty()
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        top_value, avg, med, min_value, max_value = get_key_metrics(
            top_df, state_, "price")

        overall = df["price"].sum()
        perc = np.round(top_value / overall * 100)

        line1.markdown(
            f"""##### The {order} {num_fal} {state}s Contributed :green[{perc}% ($ {data_parser.clean_format(top_value)})] of the Total Revenue :green[($ {data_parser.clean_format(overall)})]"""
        )

        with col1:
            annotated_text(
                "Average Value: ", (f"$ {data_parser.clean_format(avg)}",
                                    "value", "#83c9ff")
            )

        with col2:
            annotated_text(
                "Median Value: ", (f"$ {data_parser.clean_format(med)}",
                                   "value", "#83c9ff")
            )

        with col3:
            annotated_text(
                "Min Value: ", (f"$ {data_parser.clean_format(min_value)}",
                                "value", "#83c9ff")
            )

        with col4:
            annotated_text(
                "Max Value: ", (f"$ {data_parser.clean_format(max_value)}",
                                "value", "#83c9ff")
            )

        fig = px.bar(
            sliced_df,
            x=state_,
            y="price",
            color="customer_state" if state_ == "seller_state" else "seller_state",
            template="presentation",
        )
        fig.update_layout(
            showlegend=True,
            legend_title_text="Customer States" if state == "Seller State" else "Seller State",
            title=f"{order} {num_fal} Revenue Contributors Per {state}",
            yaxis_tickprefix="$ ",
            hoverlabel=dict(bgcolor="white", font_size=14,
                            font_family="Rockwell"),
        )
        fig.update_xaxes(title_text=state)
        fig.update_yaxes(title_text="Revenue")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})

    with tab2:

        num1, num2, num3 = st.columns([1, 1, 1])
        with num1:
            city = st.selectbox(f"Select City Type (Revenue)",
                                options=["Customer City", "Seller City"])
            city_ = "customer_city" if state == "Customer City" else "seller_city"

        cc_df = (
            df.groupby(by=city_).agg(
                {"price": "sum"}).reset_index()
        )
        with num2:
            order = st.selectbox(f"Select City Sort Order (Revenue)",
                                 options=["Top", "Bottom"])
            order_ = True if order == "Bottom" else False

        with num3:
            num_fal = st.slider(
                f"Select No. of {city[:-1]}ies to Show", min_value=5, max_value=cc_df[city_].nunique())

        top_df = cc_df.sort_values(by="price", ascending=order_)[
            :num_fal
        ]

        line1 = st.empty()
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

        top_value, avg, med, min_value, max_value = get_key_metrics(
            top_df, city_, "price")
        perc = np.round(top_value / overall * 100)

        line1.markdown(
            f"""##### The {order} {num_fal} {city[:-1]}ies Contributed :green[{perc}% ($ {data_parser.clean_format(top_value)})] of the Total Revenue :green[($ {data_parser.clean_format(overall)})]"""
        )

        with col1:
            annotated_text(
                "Average Value: ", (f"$ {data_parser.clean_format(avg)}",
                                    "value", "#83c9ff")
            )

        with col2:
            annotated_text(
                "Median Value: ", (f"$ {data_parser.clean_format(med)}",
                                   "value", "#83c9ff")
            )

        with col3:
            annotated_text(
                "Min Value: ", (f"$ {data_parser.clean_format(min_value)}",
                                "value", "#83c9ff")
            )

        with col4:
            annotated_text(
                "Max Value: ", (f"$ {data_parser.clean_format(max_value)}",
                                "value", "#83c9ff")
            )
        # text_values = [
        #     data_parser.clean_format(x) for x in sliced_df["price"].values.tolist()
        # ]
        fig = px.bar(
            top_df,
            x=city_,
            y="price",
            color=city_,
            template="presentation",
        )
        fig.update_layout(
            showlegend=True,
            legend_title_text="Customer Cities" if state == "Customer City" else "Seller Cities",
            title=f"{order} {num_fal} Revenue Contributors Per {state}",
            yaxis_tickprefix="$ ",
            hoverlabel=dict(bgcolor="white", font_size=14,
                            font_family="Rockwell"),
        )
        # fig.update_traces(hovertemplate="%{x} <br> Total Revenue: %{y}")
        fig.update_xaxes(title_text=city)
        fig.update_yaxes(title_text="Revenue")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})

    # Products 
    prod_df = (
        df.groupby(by="product_category_name").agg(
            {"price": "sum"}).reset_index()
    )

    num1, num2 = st.columns([1, 1])

    with num1:
        order = st.selectbox(f"Product Category Sort Order",
                             options=["Top", "Bottom"])
        order_ = True if order == "Bottom" else False

    with num2:
        num_fal = st.slider(
            f"Number of Categories to Show", min_value=5, max_value=prod_df["product_category_name"].nunique())

    top_df = prod_df.sort_values(by="price", ascending=order_)[
        :num_fal
    ]

    line1 = st.empty()
    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    top_value, avg, med, min_value, max_value = get_key_metrics(
            top_df, "product_category_name", "price")
    
    perc = np.round(top_value / overall * 100)
    line1.markdown(
        f"""##### The {order} {num_fal} {city[:-1]}ies Contributed :green[{perc}% ($ {data_parser.clean_format(top_value)})] of the Total Revenue :green[($ {data_parser.clean_format(overall)})]"""
    )

    with col1:
        annotated_text(
            "Average Value: ", (f"$ {data_parser.clean_format(avg)}",
                                "value", "#83c9ff")
        )

    with col2:
        annotated_text(
            "Median Value: ", (f"$ {data_parser.clean_format(med)}",
                               "value", "#83c9ff")
        )

    with col3:
        annotated_text(
            "Min Value: ", (f"$ {data_parser.clean_format(min_value)}",
                            "value", "#83c9ff")
        )

    with col4:
        annotated_text(
            "Max Value: ", (f"$ {data_parser.clean_format(max_value)}",
                            "value", "#83c9ff")
        )
    # text_values = [
    #     data_parser.clean_format(x) for x in sliced_df["price"].values.tolist()
    # ]
    fig = px.bar(
        top_df,
        x="product_category_name",
        y="price",
        color="product_category_name",
        template="presentation",
    )
    fig.update_layout(
        showlegend=False,
        title=f"{order} {num_fal} Revenue Contributors Per {state}",
        yaxis_tickprefix="$ ",
        hoverlabel=dict(bgcolor="white", font_size=14,
                        font_family="Rockwell"),
    )
    # fig.update_traces(hovertemplate="%{x} <br> Total Revenue: %{y}")
    fig.update_xaxes(title_text="Product Category Name")
    fig.update_yaxes(title_text="Revenue")
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})


def volume_plots(df):
    tab1, tab2 = st.tabs(["Monthly Volume Comparison", "Volume Trend"])
    with tab1:
        trend_data = df.groupby(by=[pd.Grouper(
            key="order_purchase_timestamp", freq="MS"), "order_status"]).agg(num_products=("product_id", "count")).reset_index()

        fig = px.bar(trend_data, x="order_purchase_timestamp",
                     y="num_products", color="order_status", labels={"order_status": "Order Status"},
                     color_discrete_sequence=px.colors.qualitative.Bold)

        fig.update_layout(title=f"M-o-M Sales Volume ",
                          xaxis_title="Order Date", yaxis_title="No. of Products",
                          hovermode="x",
                          hoverlabel=dict(
                                bgcolor="white", font_size=14, font_family="Rockwell"),
                          )
        fig.update_traces(
            hovertemplate="%{x} <br> Number of Products: %{y}")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})
    with tab2:
        freq = st.selectbox("Select Frequency for Trend", options=[
            "Daily", "Weekly", "Monthly"])
        trend_data = df.groupby(by=[pd.Grouper(
            key="order_purchase_timestamp", freq=freq[0]), "order_status"]).agg(num_products=("product_id", "count")).reset_index()
        fig = px.line(trend_data, x="order_purchase_timestamp",
                      y="num_products", color="order_status", labels={"order_status": "Order Status"},
                      color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_layout(title=f" {freq} Revenue Trend",
                          xaxis_title="Order Date", yaxis_title="Number of Products",
                          hovermode="x",
                          hoverlabel=dict(
                                bgcolor="white", font_size=14, font_family="Rockwell"),
                          )
        fig.update_traces(hovertemplate="%{x} <br> No. of Products: %{y}")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})

    # Regional Analysis
    # Tests/seller_states
    tab1, tab2 = st.tabs(["State Performance", "City Performance"])

    with tab1:
        ss_df = (
            df.groupby(by=["seller_state", "customer_state"])
            .agg(num_products=("product_id", "count"))
            .reset_index()
        )

        num1, num2, num3 = st.columns([1, 1, 1])
        with num1:
            state = st.selectbox(f"Select State Type (Volume)",
                                 options=["Customer State", "Seller State"])
            state_ = "customer_state" if state == "Customer State" else "seller_state"

        with num2:
            order = st.selectbox(f"Select State Sort Order (Volume)",
                                 options=["Top", "Bottom"])
            order_ = True if order == "Bottom" else False

        with num3:
            num_fal = st.slider(
                f"Select No. of States to Show (Volume)", min_value=5, max_value=ss_df[state_].nunique())

        top_df = ss_df.groupby(by=state_).agg({"num_products": "sum"}).reset_index().sort_values(
            by="num_products", ascending=order_)[
            :num_fal
        ]

        sliced_df = ss_df[ss_df[state_].isin(
            top_df[state_].tolist())]
        sliced_df = sliced_df.sort_values(
            by="num_products", ascending=order_)
        
        line1 = st.empty()
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        top_value, avg, med, min_value, max_value = get_key_metrics(
            top_df, state_, "num_products")

        overall = df["product_id"].count()
        perc = np.round(top_value / overall * 100)
        line1.markdown(
            f"""##### The {order} {num_fal} {state}s Contributed :green[{perc}% ({data_parser.clean_format(top_value)} units)] of the Total Units :green[({data_parser.clean_format(overall)} units)]"""
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
        # text_values = [
        #     data_parser.clean_format(x) for x in sliced_df["price"].values.tolist()
        # ]
        fig = px.bar(
            sliced_df,
            x=state_,
            y="num_products",
            color="customer_state" if state_ == "seller_state" else "seller_state",
            template="presentation",
        )
        fig.update_layout(
            showlegend=True,
            legend_title_text="Customer States" if state == "Seller State" else "Seller State",
            title=f"{order} {num_fal} Volume Contributors Per {state}",
            hoverlabel=dict(bgcolor="white", font_size=14,
                            font_family="Rockwell"),
        )
        fig.update_xaxes(title_text=state)
        fig.update_yaxes(title_text="Number of Products")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})

    with tab2:

        num1, num2, num3 = st.columns([1, 1, 1])
        with num1:
            city = st.selectbox(f"Select City Type (Volume)",
                                options=["Customer City", "Seller City"])
            city_ = "customer_city" if state == "Customer City" else "seller_city"

        cc_df = (
            df.groupby(by=city_).agg(num_products=(
                "product_id", "count")).reset_index()
        )
        with num2:
            order = st.selectbox(f"Select City Sort Order (Volume)",
                                 options=["Top", "Bottom"])
            order_ = True if order == "Bottom" else False

        with num3:
            num_fal = st.slider(
                f"No. of Cities to Show (Volume)", min_value=5, max_value=cc_df[city_].nunique())

        top_df = cc_df.sort_values(by="num_products", ascending=order_)[
            :num_fal
        ]

        line1 = st.empty()
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])     
        
        top_value, avg, med, min_value, max_value = get_key_metrics(
            top_df, city_, "num_products")
        perc = np.round(top_value / overall * 100)
        line1.markdown(
            f"""##### The {order} {num_fal} {city[:-1]}ies Contributed :green[{perc}% ({data_parser.clean_format(top_value)}) units] of the Total Units :green[({data_parser.clean_format(overall)} units)]"""
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
        # text_values = [
        #     data_parser.clean_format(x) for x in sliced_df["price"].values.tolist()
        # ]
        fig = px.bar(
            top_df,
            x=city_,
            y="num_products",
            color=city_,
            template="presentation",
        )
        fig.update_layout(
            showlegend=True,
            legend_title_text="Customer Cities" if state == "Customer City" else "Seller Cities",
            title=f"{order} {num_fal} Volume Contributors Per {state}",
            hoverlabel=dict(bgcolor="white", font_size=14,
                            font_family="Rockwell"),
        )
        # fig.update_traces(hovertemplate="%{x} <br> Total Revenue: %{y}")
        fig.update_xaxes(title_text=city)
        fig.update_yaxes(title_text="Volume")
        st.plotly_chart(fig, use_container_width=True,
                        config={"displayModeBar": False})

    prod_df = (
        df.groupby(by="product_category_name").agg(
            num_products=("product_id", "count")).reset_index()
    )

    num1, num2 = st.columns([1, 1])

    with num1:
        order = st.selectbox(f"Select Sort Order (Volume)",
                             options=["Top", "Bottom"])
        order_ = True if order == "Bottom" else False

    with num2:
        num_fal = st.slider(
            f"Number of Categories to Show", min_value=5, max_value=prod_df["product_category_name"].nunique())

    top_df = prod_df.sort_values(by="num_products", ascending=order_)[
        :num_fal
    ]

    line1 = st.empty()

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    top_value, avg, med, min_value, max_value = get_key_metrics(
            top_df, "product_category_name", "num_products")

    perc = np.round(top_value / overall * 100)
    line1.markdown(
        f"""##### The {order} {num_fal} {city[:-1]}ies Contributed :green[{perc}% ({data_parser.clean_format(top_value)} units)] of the Total Units :green[($ {data_parser.clean_format(overall)} units)]"""
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
        y="num_products",
        color="product_category_name",
        template="presentation",
    )
    fig.update_layout(
        showlegend=False,
        title=f"{order} {num_fal} Volume Contributors Per {state}",
        hoverlabel=dict(bgcolor="white", font_size=14,
                        font_family="Rockwell"),
    )
    # fig.update_traces(hovertemplate="%{x} <br> Total Revenue: %{y}")
    fig.update_xaxes(title_text="Product Category Name")
    fig.update_yaxes(title_text="Number of Products")
    st.plotly_chart(fig, use_container_width=True,
                    config={"displayModeBar": False})
