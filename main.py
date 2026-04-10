import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv
from prompts import SYSTEM_INSTRUCTIONS

st.set_page_config(page_title="Algoritmik Rehber", layout="wide")
load_dotenv()

api_key = os.getenv("API_KEY")

def call_gemini(messages):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"

    headers = {'Content-Type': 'application/json'}

    contents = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    payload = {"contents": contents}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response_json = response.json()

        if response.status_code == 200:
            return response_json['candidates'][0]['content']['parts'][0]['text']
        else:
            error_text = response_json.get('error', {}).get('message', 'Bilinmeyen Hata')
            return f"🚨 API Hatası ({response.status_code}): {error_text}"
    except Exception as e:
        return f"❌ Bağlantı Hatası: {str(e)}"

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("🚀 Öğrenme Paneli")
    st.divider()

    if st.button("📚 Konu Tekrarını Başlat"):
        # Sistem talimatını ilk mesaja gömerek zekayı başlatıyoruz
        init_prompt = f"SİSTEM: {SYSTEM_INSTRUCTIONS}\n\nGÖREV: Merhaba! Lütfen öğrenciye algoritmik düşünme konusunu (BTY.5.6.1) anlatmaya başla."
        st.session_state.messages = [{"role": "user", "content": init_prompt}]

        with st.spinner("Öğretmen notlarını hazırlıyor..."):
            response_text = call_gemini(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.rerun()

    if st.button("🗑️ Sohbeti Temizle"):
        st.session_state.messages = []
        st.rerun()

st.title("🤖 Algoritmik Düşünme Mentoru")

for message in st.session_state.messages:
    if not message["content"].startswith("SİSTEM:"):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Mesajını buraya yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            response_text = call_gemini(st.session_state.messages)
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})