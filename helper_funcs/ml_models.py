from sklearn.cluster import AgglomerativeClustering
from scipy.cluster import hierarchy
import streamlit as st


@st.cache_data(show_spinner=False)
def cluster(n_clusters, df, columns=["customer_lat", "customer_lng", "distance_covered"]):
    with st.spinner():
        clustering_model_no_clusters = AgglomerativeClustering(
            n_clusters=n_clusters, linkage="ward")
        clustering_model_no_clusters.fit(
            df[columns])
        labels_no_clusters = clustering_model_no_clusters.labels_
        df["cluster"] = labels_no_clusters
        return df