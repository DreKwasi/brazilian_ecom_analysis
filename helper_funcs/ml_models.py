from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import OrdinalEncoder
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from scipy.cluster import hierarchy
from sklearn import metrics
from pycaret.classification import *
import streamlit as st
import pandas as pd


coltransform = make_column_transformer(
    (OrdinalEncoder(), ["order_status", "seller_state", "payment_type", "customer_state",
                        "product_category_name"]), remainder="passthrough")


defaultmodels = {
    "Logistic Regression": LogisticRegression,
    "KNearest Neighbours": KNeighborsClassifier,
}


@st.cache_data(show_spinner=False)
def cluster(n_clusters: int, df: pd.DataFrame, columns: list = ["customer_lat", "customer_lng", "distance_covered"]) -> pd.DataFrame:
    with st.spinner():
        clustering_model_no_clusters = AgglomerativeClustering(
            n_clusters=n_clusters, linkage="ward")
        clustering_model_no_clusters.fit(
            df[columns])
        labels_no_clusters = clustering_model_no_clusters.labels_
        df["cluster"] = labels_no_clusters
        return df


@st.cache_resource()
def train(X: pd.DataFrame, y: pd.DataFrame, selected_key):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.30, random_state=50)

    model = defaultmodels[selected_key]()
    pipeline = make_pipeline(coltransform, model)
    pipeline.fit(X_train, y_train)
    pred = pipeline.predict(X_test)
    mae = metrics.mean_absolute_error(pred, y_test)
    acc = round(metrics.accuracy_score(y_test, pred) * 100, 2)
    col1, col2 = st.columns(2)

    col1.write(f"{selected_key} MAE: {round(mae, 2)}")
    col2.write(f"{selected_key} Accuracy: {round(acc, 2)} %")

    return pipeline


@st.cache_data()
def prediction(_model, df):
    return _model.predict_proba(df)[:, 1]


@st.cache_resource()
def pycaret_modelling(df):
    model = load_model("best_model")
    s = setup(data=df, target="Churn", categorical_features=["customer_city", "seller_city", "order_status", "seller_state", "payment_type", "customer_state",
                                                             "product_category_name"], session_id=153)
    with st.expander("Show Model Plots"):
        st.write(model)
        plot_model(model, "auc", scale=1, plot_kwargs={
                   "percent": True}, display_format="streamlit")
        plot_model(model, "confusion_matrix", scale=1, plot_kwargs={
                   "percent": True}, display_format="streamlit")
        plot_model(model, "class_report", scale=1, plot_kwargs={
                   "percent": True}, display_format="streamlit")
    return model


@st.cache_data()
def pycaret_prediction(df):
    model = load_model("best_model")
    return model.predict_proba(df)[:, 1]
