import streamlit as st
import pandas as pd
from groq import Groq
from PIL import Image
import io
import base64

st.set_page_config(layout="wide", page_title="AI PMO Dashboard")
st.title("🚀 AI PMO Executive Dashboard")

# Inizializzazione Client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Caricamento file
uploaded_file = st.file_uploader("Carica il tuo export CSV", type=["csv"])

if uploaded_file:
    # Lettura e pulizia
    df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
    df['Closed Date'] = pd.to_datetime(df['Closed Date'], errors='coerce')
    df['Story Points'] = pd.to_numeric(df['Story Points'], errors='coerce').fillna(0)
    
    # KPI calcolati correttamente
    # Filtriamo per righe che hanno una data di chiusura (quindi sono Done/Closed)
    done_items = df.dropna(subset=['Closed Date'])
    total_points = done_items['Story Points'].sum()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Punti Completati", f"{total_points:.0f}")
    col2.metric("Task Chiusi", len(done_items))
    col3.metric("Totale Item", len(df))
    col4.metric("Stato", "Analisi Pronta")

    # Layout a schede
    tab1, tab2 = st.tabs(["📊 Analisi Immagini (Vision)", "💬 Chat Dati"])

    with tab1:
        st.subheader("Analisi Snapshot Azure DevOps")
        uploaded_image = st.file_uploader("Carica lo screenshot", type=["png", "jpg", "jpeg"])
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, use_container_width=True)
            if st.button("Analizza Snapshot"):
                with st.spinner("Analisi in corso..."):
                    # Preparazione immagine
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    
                    # Chiamata Vision (usa llama-3.2-90b-vision-preview o llama-3.3-70b-versatile)
                    response = client.chat.completions.create(
                        model="llama-3.2-90b-vision-preview",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Analizza questo grafico PM. Identifica punti di forza, colli di bottiglia e trend."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                        ]}]
                    )
                    st.markdown(response.choices[0].message.content)

    with tab2:
        st.subheader("Chat Esperta sui Dati")
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages: st.chat_message(msg["role"]).markdown(msg["content"])
        
        if prompt := st.chat_input("Chiedi analisi sui dati..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            # Includiamo un sommario dei dati nel contesto della chat
            context = f"Dati attuali: {len(done_items)} task chiusi, {total_points} punti totali."
            response = client.chat.completions.create(
                messages=[{"role": "system", "content": context}] + st.session_state.messages,
                model="llama-3.3-70b-versatile"
            )
            msg = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": msg})
            st.rerun()
