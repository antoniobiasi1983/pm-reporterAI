import streamlit as st
import pandas as pd
from groq import Groq

st.title("AI PM Reporter - Dashboard")

# Controlliamo se la chiave API è impostata
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("Chiave API non trovata nei secrets di Streamlit.")
    st.stop()

uploaded_file = st.file_uploader("Carica il file CSV", type=["csv"])

if uploaded_file is not None:
    try:
        # Leggiamo il file
        df = pd.read_csv(uploaded_file)
        st.write("File caricato correttamente!")
        st.dataframe(df.head())
        
        if st.button("Analizza i dati"):
            with st.spinner("Analisi in corso..."):
                dati_testo = df.to_string()
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Sei un PM esperto. Analizza i dati."},
                        {"role": "user", "content": f"Analizza questi dati:\n{dati_testo}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                st.write("### Risultato:")
                st.write(chat_completion.choices[0].message.content)
    except Exception as e:
        st.error(f"Errore durante la lettura del file: {e}")
