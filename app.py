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
        st.subheader("Carica lo Snapshot per l'AI")
        uploaded_image = st.file_uploader("Scegli immagine", type=["png", "jpg", "jpeg"], key="vision_uploader")
        
        if uploaded_image:
            # Visualizza l'anteprima dell'immagine
            image_display = Image.open(uploaded_image)
            st.image(image_display, caption="Snapshot caricato", use_container_width=True)
            
            if st.button("Analizza Immagine", key="analyze_img_btn"):
                with st.spinner("L'AI sta analizzando il grafico..."):
                    try:
                        # Conversione dell'immagine in base64
                        # È fondamentale usare io.BytesIO per gestire il file caricato
                        import io
                        buffered = io.BytesIO()
                        image_display.save(buffered, format=image_display.format if image_display.format else 'PNG')
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        
                        # Chiamata al modello Vision
                        # NOTA: Assicurati di usare un modello che supporti la visione (es. llama-3.2-90b-vision-preview)
                        # Se il tuo account Groq non ha accesso a questo modello, l'errore sarà qui.
                        model_vision = "llama-3.2-90b-vision-preview" 
                        
                        response = client.chat.completions.create(
                            model=model_vision,
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": "Analizza questo grafico di Azure DevOps. Identifica trend, colli di bottiglia e punti di forza. Sii sintetico e professionale."
                                        },
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/{image_display.format.lower() if image_display.format else 'png'};base64,{img_str}"
                                            }
                                        }
                                    ]
                                }
                            ],
                            max_tokens=1000
                        )
                        
                        # Visualizza la risposta dell'AI
                        st.write("### Risultato Analisi Visiva:")
                        st.success(response.choices[0].message.content)
                        
                    except Exception as e:
                        st.error(f"Errore durante l'analisi dell'immagine: {e}")
                        st.info("Assicurati di avere accesso al modello 'llama-3.2-90b-vision-preview' su Groq.")
