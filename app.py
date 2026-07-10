import streamlit as st
import pandas as pd

st.title("AI PM Reporter")

# 1. Caricamento File
uploaded_file = st.file_uploader("Carica il tuo file CSV", type=["csv"])

# 2. Se il file esiste, lo leggiamo e mostriamo
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Dati caricati correttamente:")
    st.dataframe(df.head())
else:
    st.info("Carica un file CSV per iniziare.")
