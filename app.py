import streamlit as st
import pandas as pd
from groq import Groq

st.title("AI PM Reporter - Final Version")

# Configurazione Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

uploaded_file = st.file_uploader("Carica il file CSV", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
        st.write("Dati caricati:")
        st.dataframe(df.head())
        
        if st.button("Analizza con AI"):
            dati_testo = df.to_string()
            # Qui ho cambiato le virgolette per evitare l'errore precedente
            with st.spinner("L'IA sta analizzando..."):
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "Sei un PM esperto. Analizza i dati CSV."},
                        {"role": "user", "content": f"Analizza questi dati:\n{dati_testo}"}
                    ],
                    model="llama-3.3-70b-versatile",
                )
                st.write("### Risultato:")
                st.write(chat_completion.choices[0].message.content)
    except Exception as e:
        st.error(f"Errore nella lettura del CSV: {e}")
