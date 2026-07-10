import streamlit as st
import pandas as pd
from groq import Groq

st.set_page_config(layout="wide", page_title="AI PMO Dashboard")
st.title("🚀 AI PMO Executive Dashboard")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

uploaded_file = st.file_uploader("Carica il tuo CSV di Azure DevOps", type=["csv"])

if uploaded_file:
    # 1. Caricamento e pulizia (usiamo Closed Date per tutto)
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip()
    
    # Conversione date e numeri
    df['Closed Date'] = pd.to_datetime(df['Closed Date'], errors='coerce')
    df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
    df['Story Points'] = pd.to_numeric(df['Story Points'], errors='coerce').fillna(0)
    
    # 2. KPI: Chi ha una 'Closed Date' è considerato completato
    completati = df.dropna(subset=['Closed Date'])
    total_points = completati['Story Points'].sum()
    lead_time = (completati['Closed Date'] - completati['Created Date']).mean().days
    
    # Visualizzazione KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Punti Completati", f"{total_points:.0f}")
    c2.metric("Task Chiusi", len(completati))
    c3.metric("Lead Time Medio", f"{lead_time:.1f} gg")
    c4.metric("Stato", "Analisi Dati OK")

    # 3. Analisi Automatica (Senza dipendenze da Vision)
    if st.button("Genera Analisi Salute Team"):
        riassunto = f"Punti totali: {total_points}, Task chiusi: {len(completati)}, Lead time medio: {lead_time} giorni. Campione: {df.head(10).to_string()}"
        prompt = f"Sei un PMO esperto. Analizza questi dati: {riassunto}. Identifica 3 colli di bottiglia e 3 punti di forza."
        resp = client.chat.completions.create(messages=[{"role":"user", "content": prompt}], model="llama-3.3-70b-versatile")
        st.markdown(resp.choices[0].message.content)

    # 4. Chat Esperta
    st.subheader("💬 Chat con l'Esperto PMO")
    if "messages" not in st.session_state: st.session_state.messages = []
    for m in st.session_state.messages: st.chat_message(m["role"]).write(m["content"])
    if p := st.chat_input("Fai domande specifiche sui dati..."):
        st.session_state.messages.append({"role": "user", "content": p})
        r = client.chat.completions.create(messages=[{"role": "user", "content": p}], model="llama-3.3-70b-versatile")
        st.session_state.messages.append({"role": "assistant", "content": r.choices[0].message.content})
        st.rerun()
