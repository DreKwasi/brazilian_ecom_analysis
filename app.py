import streamlit as st
from st_pages import Page, Section, show_pages, add_page_title



show_pages([
    Page("app.py", "Home", ),
    Page("other_pages/crm.py", "CRM Analytics", ), 
    Page("other_pages/forecast.py", "Forecasting", ), 
     
])