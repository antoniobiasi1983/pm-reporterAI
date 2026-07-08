import streamlit as st
import pandas as pd
import google.generativeai as genai

st.title("📊 AI PM Reporter (Gemini Edition)")

# Recupera la chiave dai Secrets di Streamlit
api_key = st.secrets.get("GOOGLE_API_KEY")

uploaded_file = st.file_uploader("Carica il file CSV", type=["csv"])

if uploaded_file and api_key:
    df = pd.read_csv(uploaded_file)
    st.write("Dati caricati correttamente:")
    st.dataframe(df.head())

    if st.button("Analizza con AI"):
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Creiamo un prompt che istruisce Gemini ad analizzare i dati
            prompt = f"Analizza questi dati Agile in formato CSV e fornisci un report sintetico sullo stato del progetto: {df.to_string()}"
            
            response = model.generate_content(prompt)
            st.write("### Report Analisi:")
            st.write(response.text)
        except Exception as e:
            st.error(f"Si è verificato un errore: {e}")

elif not api_key:
    st.error("Errore: Chiave API di Google non configurata nei 'Secrets'!")
