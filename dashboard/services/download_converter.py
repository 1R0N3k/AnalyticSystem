import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def convert_to_dataframe(data: list[dict]) -> pd.DataFrame:
    return pd.DataFrame(data)

@st.cache_data
def convert_for_download_csv(data: list[dict]):
    return convert_to_dataframe(data).to_csv().encode("utf-8")