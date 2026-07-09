import streamlit as st
from openai import OpenAI
import pandas as pd

# 1. Configurazione OpenAI
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("AI PM Reporter (OpenAI Edition)")

uploaded_file = st.file_uploader("Carica il file CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Dati caricati:")
    st.dataframe(df.head())
    
    if st.button("Analizza con AI"):
        # Convertiamo i dati in testo per l'AI
        dati_testo = df.to_string()
        
        try:
            # 2. Chiamata a OpenAI
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Sei un PM esperto. Analizza i dati del CSV fornito."},
                    {"role": "user", "content": f"Analizza questi dati:\n{dati_testo}"}
                ]
            )
            st.write("### Risultato dell'analisi:")
            st.write(response.choices[0].message.content)
        except Exception as e:
            st.error(f"Errore durante l'analisi: {e}")
