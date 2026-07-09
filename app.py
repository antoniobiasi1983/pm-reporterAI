import streamlit as st
import google.generativeai as genai
import pandas as pd

# Configurazione (assicurati di avere la chiave AIza nei secrets come GOOGLE_API_KEY)
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash') # Il modello Flash è gratis e veloce

st.title("AI PM Reporter (Gratuito)")

uploaded_file = st.file_uploader("Carica CSV", type=["csv"])

if uploaded_file and st.button("Analizza con AI"):
    df = pd.read_csv(uploaded_file)
    prompt = f"Analizza questi dati di Project Management: {df.to_string()}"
    
    # Questa chiamata è GRATUITA col piano Free di Gemini
    response = model.generate_content(prompt)
    st.write(response.text)
