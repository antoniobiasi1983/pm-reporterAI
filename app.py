import streamlit as st
import pandas as pd
import openai

st.title("📊 AI PM Reporter")
api_key = st.secrets.get("OPENAI_API_KEY")
uploaded_file = st.file_uploader("Carica il file CSV", type=["csv"])

if uploaded_file and api_key:
    df = pd.read_csv(uploaded_file)
    st.write("Dati caricati:")
    st.dataframe(df.head())
    if st.button("Analizza con AI"):
        client = openai.OpenAI(api_key=api_key)
        prompt = f"Analizza questi dati Agile: {df.to_string()}"
        response = client.chat.completions.create(
            model="gpt-4o", messages=[{"role": "user", "content": prompt}]
        )
        st.write(response.choices[0].message.content)
elif not api_key:
    st.error("Errore: Chiave API non configurata in 'Secrets'!")
