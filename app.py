import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(layout="wide")
st.title("🚀 AI PMO Executive Dashboard")

# Inizializza client Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

uploaded_file = st.file_uploader("Carica il tuo export CSV completo", type=["csv"])

if uploaded_file:
    # Caricamento e pulizia automatica
    df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
    
    # Conversione date e pulizia colonne
    df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
    df['Closed Date'] = pd.to_datetime(df['Closed Date'], errors='coerce')
    
    st.success("Dati caricati e puliti correttamente!")
    
    # --- KPI IN EVIDENZA ---
    closed_items = df[df['State'] == 'Closed']
    total_points = closed_items['Story Points'].sum() if 'Story Points' in df.columns else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Punti Completati", total_points)
    col2.metric("Task Chiusi", len(closed_items))
    col3.metric("Task Totali nel CSV", len(df))
    col4.metric("Stato", "Ready for Analysis")

    # --- TAB ANALISI E CHAT ---
    tab1, tab2 = st.tabs(["📊 Analisi PMO", "💬 Chat"])
    
    with tab1:
        if st.button("Genera Analisi Automatica (Forza/Colli Bottiglia)"):
            with st.spinner("Analisi in corso..."):
                prompt = f"Analizza questi dati PMO. Identifica: 1) 3 Punti di forza 2) 3 Colli di bottiglia 3) Parere esperto PMO. Dati: {df.head(50).to_string()}"
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                )
                st.markdown(response.choices[0].message.content)
    
    with tab2:
        if "messages" not in st.session_state:
            st.session_state.messages = []
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).markdown(msg["content"])
            
        if prompt := st.chat_input("Chiedi all'esperto..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile",
            )
            msg = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.rerun()
