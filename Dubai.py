import streamlit as st

st.set_page_config(page_title="Bare Test", layout="wide")

st.title("Bare Streamlit Test")

x = st.slider("Pick a number", 0, 10, 3)
st.write("You picked:", x)
