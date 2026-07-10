import streamlit as st
import pandas as pd
from groq import Groq

st.title("AI PM Reporter - Chat & Analytics")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Inizializza la cronologia della chat
if "messages" not in st.session_state:
    st.session_state.messages = []

uploaded_file = st.file_uploader("Carica il tuo export CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
    st.dataframe(df.head())
    
    # Pulsante per caricare i dati nel contesto AI
    if st.button("Inizia analisi su questi dati"):
        st.session_state.messages = [{"role": "system", "content": f"Analizza questi dati PM: {df.to_string()}"}]
        st.success("Dati caricati! Ora puoi chiedere all'AI qualsiasi cosa.")

    # Visualizzazione chat
    for message in st.session_state.messages[1:]: # Ignora il system prompt
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Input utente
    if prompt := st.chat_input("Fai una domanda sui dati..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                messages=st.session_state.messages,
                model="llama-3.3-70b-versatile",
            )
            full_response = response.choices[0].message.content
            st.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
