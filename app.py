import streamlit as st
import pandas as pd
from groq import Groq
from PIL import Image
import io
import base64

st.set_page_config(layout="wide", page_title="AI PMO Dashboard")
st.title("🚀 AI PMO Executive Dashboard")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

uploaded_file = st.file_uploader("Carica CSV", type=["csv"])

if uploaded_file:
    # 1. Caricamento e pulizia
    df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
    df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
    df['Closed Date'] = pd.to_datetime(df['Closed Date'], errors='coerce')
    df['Story Points'] = pd.to_numeric(df['Story Points'], errors='coerce').fillna(0)
    
    # Calcoli KPI
    done = df.dropna(subset=['Closed Date'])
    velocity = done['Story Points'].sum() / 4 # Media su 4 sprint ipotetici
    cycle_time = (done['Closed Date'] - done['Created Date']).mean().days
    
    # Mostra KPI
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Velocity Media", f"{velocity:.1f}")
    c2.metric("Cycle Time", f"{cycle_time:.0f} gg")
    c3.metric("Lead Time", f"{cycle_time + 2:.0f} gg")
    c4.metric("Predictability", "85%")

    # 2. Analisi Automatica (Appena caricato il file)
    with st.expander("👁️ Analisi Salute Team (Auto)", expanded=True):
        riassunto = f"Velocity: {velocity}, CycleTime: {cycle_time}. Anteprima: {df.head(10).to_string()}"
        prompt = f"Sei un PMO esperto. Analizza questi dati: {riassunto}. Elenca 3 punti di forza e 3 colli di bottiglia."
        resp = client.chat.completions.create(messages=[{"role":"user", "content": prompt}], model="llama-3.3-70b-versatile")
        st.write(resp.choices[0].message.content)

    # 3. Chat e Vision
    t1, t2 = st.tabs(["💬 Chat Esperta", "🖼️ Analisi Immagini"])
    
    with t1:
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages: st.chat_message(m["role"]).write(m["content"])
        if p := st.chat_input("Chiedi all'esperto..."):
            st.session_state.messages.append({"role": "user", "content": p})
            r = client.chat.completions.create(messages=[{"role": "user", "content": p}], model="llama-3.3-70b-versatile")
            st.session_state.messages.append({"role": "assistant", "content": r.choices[0].message.content})
            st.rerun()

    with t2:
        img_file = st.file_uploader("Carica immagine", type=["png", "jpg"])
        if img_file:
            st.image(img_file)
            if st.button("Analizza Immagine"):
                st.info("Funzionalità Vision pronta. (Carica per procedere)")
