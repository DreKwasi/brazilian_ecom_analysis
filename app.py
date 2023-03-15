import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title
from helper_funcs import styles
from page_funcs import home_view


st.set_page_config(layout="wide", initial_sidebar_state="expanded")

styles.load_css_file("assets/styles/main.css")
styles.set_png_as_page_bg("assets/img/olist_logo.png")

show_pages([
    Page("app.py", "Home", ),
    Page("other_pages/crm.py", "CRM Analytics", ), 
    Page("other_pages/forecast.py", "Forecasting", ), 
     
])


home_view.show()
