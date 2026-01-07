# save as app.py and run: streamlit run app.py

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Streamlit Test", layout="wide")

st.title("Minimal Streamlit Test")

st.write("If you see this quickly, Streamlit itself is fine.")

if st.button("Load CSV and show head"):
    df = pd.read_csv("bayut_selling_properties.csv")
    st.write(df.shape)
    st.dataframe(df.head())
