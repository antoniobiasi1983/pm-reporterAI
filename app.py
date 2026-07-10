import streamlit as st
import pandas as pd

st.title("Test di isolamento")

# Proviamo a creare un piccolo dataframe fisso senza caricare nulla
dati = {'Colonna1': [1, 2, 3], 'Colonna2': ['A', 'B', 'C']}
df = pd.DataFrame(dati)

st.write("Se vedi questa tabella, Pandas sta funzionando:")
st.dataframe(df)
