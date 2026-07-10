import streamlit as st
import pandas as pd
from groq import Groq

# Inizializza il client Groq con la chiave nei secrets
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("AI PM Reporter")

uploaded_file = st.file_uploader("Carica il tuo file CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Dati caricati correttamente:")
    st.dataframe(df.head())
    
    if st.button("Analizza con AI"):
        try:
            dati_testo = df.to_string()
            # Chiamata a Groq con Llama 3
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Sei un PM esperto. Analizza i dati CSV forniti."},
                    {"role": "user", "content": f"Analizza questi dati:\n{dati_testo}"}
                ],
                model="llama-3.3-70b-versatile",
            )
            st.write("### Risultato dell'analisi:")
            st.write(chat_completion.choices[0].message.content)
        except Exception as e:
            st.error(f"Errore durante l'analisi: {e}")
