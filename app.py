import streamlit as st
import google.generativeai as genai
import pandas as pd

# Usa la chiave che hai nei tuoi Secrets chiamata GOOGLE_API_KEY
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

st.title("AI PM Reporter (Gratuito)")

uploaded_file = st.file_uploader("Carica CSV", type=["csv"])

if uploaded_file and st.button("Analizza con AI"):
    df = pd.read_csv(uploaded_file)
    st.dataframe(df.head())
    
    prompt = f"Analizza questi dati di Project Management: {df.to_string()}"
    
    try:
        response = model.generate_content(prompt)
        st.write("### Risultato:")
        st.write(response.text)
    except Exception as e:
        st.error(f"Errore: {e}")
