import streamlit as st
import base64


def load_css_file(css_file_path):
    with open(css_file_path) as f:
        return st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = (
        """
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-repeat: no-repeat;
    background-size: 170px;
    background-position: 80rem 0.5rem;

    }
    </style>
    """
        % bin_str
    )

    st.markdown(page_bg_img, unsafe_allow_html=True)
    return
