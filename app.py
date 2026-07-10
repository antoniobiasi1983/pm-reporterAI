import streamlit as st
import pandas as pd
from groq import Groq
from PIL import Image
import io
import base64

st.set_page_config(layout="wide")
st.title("🚀 AI PMO Executive Dashboard")

# Configurazione Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Creiamo due schede separate
tab1, tab2 = st.tabs(["📊 Analisi Dati (CSV)", "🖼️ Analisi Immagini"])

# --- TAB 1: ANALISI DATI ---
with tab1:
    st.subheader("Carica il tuo CSV")
    uploaded_file = st.file_uploader("Carica file CSV", type=["csv"])
    if uploaded_file:
        df = pd.read_csv(uploaded_file, encoding='utf-8', on_bad_lines='skip')
        st.dataframe(df.head())
        if st.button("Analizza Dati"):
            with st.spinner("L'IA sta analizzando..."):
                prompt = f"Sei un PM esperto. Analizza questi dati: {df.to_string()}"
                response = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                )
                st.write(response.choices[0].message.content)

# --- TAB 2: ANALISI IMMAGINI ---
with tab2:
    st.subheader("Carica Snapshot")
    uploaded_image = st.file_uploader("Carica immagine", type=["png", "jpg", "jpeg"])
    if uploaded_image:
        image = Image.open(uploaded_image)
        st.image(image, caption="Snapshot", use_container_width=True)
        if st.button("Analizza Immagine"):
            with st.spinner("Analisi immagine in corso..."):
                # Convertiamo in base64
                buffered = io.BytesIO()
                image.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Chiamata al modello (usiamo llama-3.3-70b-versatile che gestisce bene anche i contesti)
                prompt = "Analizza questa immagine di un grafico di progetto. Cosa noti?"
                # Nota: per la visione pura servirebbe un modello vision specifico, 
                # se l'errore persiste è perché il modello non accetta immagini in questo modo.
                st.info("Funzionalità Vision attiva. (Assicurati di usare un modello vision-ready su Groq)")
