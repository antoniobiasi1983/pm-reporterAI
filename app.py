import streamlit as st
import pandas as pd
from groq import Groq
from PIL import Image
import io
import base64

st.set_page_config(layout="wide")
st.title("🚀 AI PMO Executive Dashboard")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Caricamento CSV
uploaded_file = st.file_uploader("Carica il CSV di Azure DevOps", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
    
    # Pulizia dati: forza le date e i numeri
    df['Created Date'] = pd.to_datetime(df['Created Date'], errors='coerce')
    df['Closed Date'] = pd.to_datetime(df['Closed Date'], errors='coerce')
    # Forza Story Points a numero, se non è un numero lo mette a 0
    df['Story Points'] = pd.to_numeric(df['Story Points'], errors='coerce').fillna(0)
    
    # KPI Dinamici
    closed_items = df[df['State'] == 'Done'] # Assicurati che 'Done' corrisponda al tuo stato nel CSV
    total_points = closed_items['Story Points'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Punti Completati", f"{total_points:.0f}")
    col2.metric("Task Chiusi", len(closed_items))
    col3.metric("Lead Time Medio", "In calcolo...") # Implementeremo dopo
    col4.metric("Stato", "Analisi Pronta")

    # Tabs
    tab1, tab2 = st.tabs(["📊 Analisi Immagine", "💬 Chat Dati"])

    with tab1:
        st.subheader("Analisi Snapshot Azure DevOps")
        uploaded_image = st.file_uploader("Carica lo screenshot del grafico", type=["png", "jpg"])
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, use_container_width=True)
            if st.button("Analizza Immagine"):
                with st.spinner("L'AI sta analizzando i colli di bottiglia..."):
                    # Conversione per invio a Groq
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    response = client.chat.completions.create(
                        model="llama-3.2-90b-vision-preview",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Analizza questo grafico PM. Indica punti di forza e colli di bottiglia."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                        ]}]
                    )
                    st.markdown(response.choices[0].message.content)

    with tab2:
        # Logica Chat (come prima)
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages: st.chat_message(msg["role"]).markdown(msg["content"])
        if prompt := st.chat_input("Chiedi all'esperto..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile"
            )
            st.rerun()
