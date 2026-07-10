import streamlit as st
import pandas as pd
from groq import Groq
from PIL import Image
import io
import base64

st.set_page_config(layout="wide", page_title="AI PMO Dashboard")
st.title("🚀 AI PMO Executive Dashboard")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

uploaded_file = st.file_uploader("Carica il tuo CSV di Azure DevOps", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
    df['Closed Date'] = pd.to_datetime(df['Closed Date'], errors='coerce')
    df['Story Points'] = pd.to_numeric(df['Story Points'], errors='coerce').fillna(0)
    
    done_items = df.dropna(subset=['Closed Date'])
    total_points = done_items['Story Points'].sum()
    
    # KPI in alto
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Punti Completati", f"{total_points:.0f}")
    col2.metric("Task Chiusi", len(done_items))
    col3.metric("Totale File", len(df))
    col4.metric("Stato", "Dati Caricati")

    # TAB STRUTTURATE
    tab1, tab2, tab3 = st.tabs(["📊 Analisi Dati Automatica", "👁️ Analisi Immagini", "💬 Chat Esperta"])

    with tab1:
        st.subheader("Analisi Forza/Debolezza (Dati)")
        if st.button("Genera Analisi Automatica"):
            with st.spinner("Analisi in corso..."):
                prompt = f"Analizza questi dati PMO. Identifica: 1) 3 Punti di forza 2) 3 Colli di bottiglia 3) Parere esperto PMO. Dati: {df.head(50).to_string()}"
                response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
                st.markdown(response.choices[0].message.content)

    with tab2:
        st.subheader("Analisi Snapshot Azure DevOps")
        uploaded_image = st.file_uploader("Carica lo screenshot", type=["png", "jpg", "jpeg"])
        if uploaded_image:
            image = Image.open(uploaded_image)
            st.image(image, use_container_width=True)
            if st.button("Analizza Snapshot"):
                with st.spinner("Analisi visiva in corso..."):
                    buffered = io.BytesIO()
                    image.save(buffered, format="PNG")
                    img_base64 = base64.b64encode(buffered.getvalue()).decode()
                    response = client.chat.completions.create(
                        model="llama-3.2-90b-vision-preview",
                        messages=[{"role": "user", "content": [
                            {"type": "text", "text": "Analizza questo grafico PM. Identifica punti di forza, colli di bottiglia e trend."},
                            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                        ]}]
                    )
                    st.markdown(response.choices[0].message.content)

    with tab3:
        st.subheader("Chat Libera")
        if "messages" not in st.session_state: st.session_state.messages = []
        for msg in st.session_state.messages: st.chat_message(msg["role"]).markdown(msg["content"])
        if prompt := st.chat_input("Chiedi all'esperto..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama-3.3-70b-versatile")
            st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
            st.rerun()
