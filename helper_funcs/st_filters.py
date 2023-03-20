import streamlit as st


def filter_widgets(df):
    date_cols = [
        "order_purchase_timestamp", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date"]

    st.sidebar.write("**Filter Date By:**")
    date_col = st.sidebar.selectbox(
        "date_col", key="date_col", options=date_cols, label_visibility="collapsed")
    df = df[~(df[date_col].isna())]
    min_date, max_date = df[date_col].dt.date.min(), df[date_col].dt.date.max()

    start_col, end_col = st.sidebar.columns(2)
    with start_col:
        st.write("**Start Date**")
        start_date = st.date_input("start_date", value=min_date, min_value=min_date,
                                   max_value=max_date, label_visibility="collapsed")
    with end_col:
        st.write("**End Date**")
        end_date = st.date_input(
            "end_date", value=max_date,  min_value=min_date, max_value=max_date, label_visibility="collapsed")

    if start_date > end_date:
        st.error("Start Date Can Not be Greater than End Date")
        st.stop()

    order_status = df['order_status'].unique()
    st.sidebar.write("**Order Status**")
    sel_order_status = st.sidebar.multiselect(
        "order_status", key="order_status", options=order_status, label_visibility="collapsed")

    payment_types = df['payment_type'].unique()
    st.sidebar.write("**Payment Type**")
    sel_payment_type = st.sidebar.multiselect(
        label="payment_type", key="payment_type", options=payment_types, label_visibility="collapsed")

    prod_category = df['product_category_name'].unique()
    st.sidebar.write("**Product Categories**")
    sel_prod_category = st.sidebar.multiselect(
        label="product_category_name", key="product_category_name", options=prod_category, label_visibility="collapsed")

    col_seller_city, col_seller_state = st.sidebar.columns(2)

    with col_seller_city:
        seller_city = df['seller_city'].unique()
        st.write("**Seller City**")
        sel_seller_city = st.multiselect(
            "seller_city", key="seller_city", options=seller_city, label_visibility="collapsed")

    with col_seller_state:
        seller_state = df['seller_state'].unique()
        st.write("**Seller State**")
        sel_seller_state = st.multiselect(
            "seller_state", key="seller_state", options=seller_state, label_visibility="collapsed")

    col_cus_city, col_cus_state = st.sidebar.columns(2)

    with col_cus_city:
        customer_city = df['customer_city'].unique()
        st.write("**Customer City**")
        sel_customer_city = st.multiselect(
            "customer_city", key="customer_city", options=customer_city, label_visibility="collapsed")

    with col_cus_state:
        customer_state = df['customer_state'].unique()
        st.write("**Customer State**")
        sel_customer_state = st.multiselect(
            "customer_state", key="customer_state", options=customer_state, label_visibility="collapsed")
    filters = [date_col, start_date, end_date, sel_order_status, sel_payment_type,
               sel_prod_category, sel_seller_city, sel_seller_state, sel_customer_city, sel_customer_state]
    
    return filters


@st.cache_data(show_spinner=False)
def filter_data(df, date_col, start_date, end_date, sel_order_status, sel_payment_type, sel_prod_category, sel_seller_city, sel_seller_state, sel_customer_city, sel_customer_state):
    date_filter = (df[date_col].dt.date >= start_date) & (
        df[date_col].dt.date <= end_date)
    df = df[date_filter]

    if len(sel_order_status) > 0:
        df = df[df['order_status'].isin(sel_order_status)]

    if len(sel_payment_type) > 0:
        df = df[df['payment_type'].isin(sel_payment_type)]

    if len(sel_prod_category) > 0:
        df = df[df['product_category_name'].isin(sel_prod_category)]

    if len(sel_seller_city) > 0:
        df = df[df['seller_city'].isin(sel_seller_city)]

    if len(sel_seller_state) > 0:
        df = df[df['seller_state'].isin(sel_seller_state)]

    if len(sel_customer_city) > 0:
        df = df[df['customer_city'].isin(sel_customer_city)]

    if len(sel_customer_state) > 0:
        df = df[df['customer_state'].isin(sel_customer_state)]

    return df
