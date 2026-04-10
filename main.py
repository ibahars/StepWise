import streamlit as st
import requests
import json
import os
import graphviz
import time
from dotenv import load_dotenv
from prompts import SYSTEM_INSTRUCTIONS

st.set_page_config(page_title="StepWise: Algorithmic Thinking Mentor", layout="wide")
load_dotenv()

api_key = os.getenv("API_KEY")

def call_gemini(messages):
    # Senin listendeki en kararlı model olan 'lite' versiyonu seçildi
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}

    contents = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    payload = {"contents": contents}

    # 503 Hatası için 3 kez otomatik yeniden deneme (Retry) mantığı
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))

            if response.status_code == 200:
                response_json = response.json()
                return response_json['candidates'][0]['content']['parts'][0]['text']

            elif response.status_code == 503:
                if attempt < 2:
                    time.sleep(2) # 2 saniye bekle ve tekrar dene
                    continue
                else:
                    return "🚨 Sunucu şu an çok yoğun. Lütfen birkaç saniye sonra tekrar deneyin."
            else:
                response_json = response.json()
                error_msg = response_json.get('error', {}).get('message', 'Bilinmeyen Hata')
                return f"🚨 API Hatası ({response.status_code}): {error_msg}"

        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            return f"❌ Bağlantı Hatası: {str(e)}"

# --- SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "flow_steps" not in st.session_state:
    st.session_state.flow_steps = []
if "mode" not in st.session_state:
    st.session_state.mode = "chat"

# --- SIDEBAR ---
with st.sidebar:
    st.title("🚀 StepWise Paneli")
    st.divider()

    if st.button("📚 Konu Tekrarını Başlat", use_container_width=True):
        st.session_state.mode = "chat"
        st.session_state.messages = [{"role": "user", "content": f"SİSTEM: {SYSTEM_INSTRUCTIONS}\n\nGÖREV: Lütfen öğrenciye algoritmik düşünme konusunu anlatmaya başla."}]
        with st.spinner("Öğretmen hazırlanıyor..."):
            response_text = call_gemini(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.rerun()

    if st.button("📐 Akış Şeması İnşa Edici", use_container_width=True):
        st.session_state.mode = "flowchart"
        st.session_state.flow_steps = []
        flow_init_prompt = "SİSTEM: Öğrenci akış şeması moduna girdi. Lütfen ona günlük hayattan basit bir algoritma problemi ver ve paneldeki araçlarla çizmesini iste."
        st.session_state.messages.append({"role": "user", "content": flow_init_prompt})
        with st.spinner("Problem hazırlanıyor..."):
            response_text = call_gemini(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.rerun()

    st.divider()
    if st.button("🗑️ Her Şeyi Sıfırla", use_container_width=True):
        st.session_state.messages = []
        st.session_state.flow_steps = []
        st.session_state.mode = "chat"
        st.rerun()

# --- ANA EKRAN BAŞLIK ---
st.title("🤖 StepWise: Algoritmik Düşünme Mentoru")

# --- AKIŞ ŞEMASI PANELİ ---
if st.session_state.mode == "flowchart":
    with st.container(border=True):
        st.subheader("🛠️ Akış Şeması Tasarım Alanı")

        c1, c2, c3 = st.columns([2, 3, 1])
        with c1:
            shape_type = st.selectbox("Şekil Seç:", ["Elips (Başla/Bitir)", "Dikdörtgen (İşlem)", "Eşkenar Dörtgen (Karar)"])
        with c2:
            step_text = st.text_input("Adım Metni:", placeholder="Adım içeriğini yazın...")
        with c3:
            st.write("") # Görsel hizalama için
            if st.button("➕ Ekle", use_container_width=True):
                if step_text:
                    st.session_state.flow_steps.append({"type": shape_type, "text": step_text})
                    st.rerun()

        if st.session_state.flow_steps:
            dot = graphviz.Digraph()
            dot.attr(rankdir='TB')
            for i, step in enumerate(st.session_state.flow_steps):
                label = step["text"]
                shape = "ellipse" if "Elips" in step["type"] else "box" if "Dikdörtgen" in step["type"] else "diamond"
                color = "green" if "Elips" in step["type"] else "blue" if "Dikdörtgen" in step["type"] else "orange"
                dot.node(str(i), label, shape=shape, color=color)
                if i > 0:
                    dot.edge(str(i-1), str(i))
            st.graphviz_chart(dot)

            b1, b2 = st.columns(2)
            if b1.button("🗑️ Şemayı Temizle", use_container_width=True):
                st.session_state.flow_steps = []
                st.rerun()
            if b2.button("✅ Bitti ve Kontrol Et", use_container_width=True):
                schema_desc = " | ".join([f"{s['type']}: {s['text']}" for s in st.session_state.flow_steps])
                check_prompt = f"Öğrenci şemayı bitirdi: {schema_desc}. Lütfen bu adımları kontrol et, mantıksal sırasını değerlendir ve geri bildirim ver."
                st.session_state.messages.append({"role": "user", "content": check_prompt})
                with st.spinner("Kontrol ediliyor..."):
                    response_text = call_gemini(st.session_state.messages)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    st.rerun()

# --- SOHBET AKIŞI ---
for message in st.session_state.messages:
    if not message["content"].startswith("SİSTEM:"):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            response_text = call_gemini(st.session_state.messages)
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})