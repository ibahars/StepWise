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
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    contents = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        contents.append({"role": role, "parts": [{"text": m["content"]}]})

    payload = {"contents": contents}
    for attempt in range(3):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code == 503:
                time.sleep(2)
                continue
            else:
                return f"🚨 API Hatası: {response.status_code}"
        except:
            time.sleep(2)
            continue
    return "🚨 Sunucu yoğun, lütfen tekrar dene."

if "messages" not in st.session_state: st.session_state.messages = []
if "flow_nodes" not in st.session_state: st.session_state.flow_nodes = []
if "flow_edges" not in st.session_state: st.session_state.flow_edges = []
if "mode" not in st.session_state: st.session_state.mode = "chat"

with st.sidebar:
    st.title("🚀 StepWise Paneli")
    st.divider()

    if st.button("📚 Konu Tekrarını Başlat", use_container_width=True):
        st.session_state.mode = "chat"
        st.session_state.messages = [{"role": "user", "content": f"SİSTEM: {SYSTEM_INSTRUCTIONS}\n\nGÖREV: Merhaba! Lütfen öğrenciye algoritmik düşünme konusunu anlatmaya başla."}]
        with st.spinner("Öğretmen hazırlanıyor..."):
            res = call_gemini(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

    if st.button("📐 Akış Şeması İnşa Edici", use_container_width=True):
        st.session_state.mode = "flowchart"
        st.session_state.flow_nodes, st.session_state.flow_edges = [], []
        flow_cmd = "SİSTEM: Öğrenci akış şeması moduna geçti. Lütfen ona orta zorlukta, içinde bir karar (Evet/Hayır) olan günlük hayattan bir senaryo ver ve bunu çizmesini iste."
        st.session_state.messages.append({"role": "user", "content": flow_cmd})
        with st.spinner("Senaryo oluşturuluyor..."):
            res = call_gemini(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

    st.divider()
    if st.button("🗑️ Her Şeyi Sıfırla", use_container_width=True):
        st.session_state.messages, st.session_state.flow_nodes, st.session_state.flow_edges, st.session_state.mode = [], [], [], "chat"
        st.rerun()

st.title("🤖 StepWise: Algoritmik Düşünme Mentoru")

# --- 1. AKIŞ ŞEMASI PANELİ (ARTIK EN ÜSTTE) ---
if st.session_state.mode == "flowchart":
    with st.container(border=True):
        st.subheader("🛠️ Akış Şeması Tasarım Alanı")
        c1, c2, c3 = st.columns([2, 3, 1])
        with c1:
            shape_type = st.selectbox("Şekil:", ["Elips (Başla/Bitir)", "Dikdörtgen (İşlem)", "Eşkenar Dörtgen (Karar)", "Paralelkenar (Bilgi Girişi)"])
        with c2:
            node_text = st.text_input("Metin:", key="node_input")
        with c3:
            st.write("")
            if st.button("➕ Ekle", use_container_width=True):
                if node_text:
                    st.session_state.flow_nodes.append({"id": str(len(st.session_state.flow_nodes)), "text": node_text, "type": shape_type})
                    st.rerun()

        if st.session_state.flow_nodes:
            st.info("🔗 Bağlantı Kur: Şekilleri birbirine bağlamak için seçim yapın.")
            bc1, bc2, bc3, bc4 = st.columns([2, 2, 2, 1])
            with bc1:
                source = st.selectbox("Kaynak:", options=st.session_state.flow_nodes, format_func=lambda x: f"{x['id']}: {x['text']}")
            with bc2:
                target = st.selectbox("Hedef:", options=st.session_state.flow_nodes, format_func=lambda x: f"{x['id']}: {x['text']}")
            with bc3:
                label = ""
                if "Eşkenar" in source["type"]:
                    label = st.selectbox("Yol:", ["Evet", "Hayır"])
            with bc4:
                st.write("")
                if st.button("🔗 Bağla", use_container_width=True):
                    st.session_state.flow_edges.append({"from": source["id"], "to": target["id"], "label": label})
                    st.rerun()

            dot = graphviz.Digraph()
            dot.attr(rankdir='TB')
            for node in st.session_state.flow_nodes:
                shape = "ellipse" if "Elips" in node["type"] else "box" if "Dikdörtgen" in node["type"] else "diamond" if "Eşkenar" in node["type"] else "parallelogram"
                color = "green" if "Elips" in node["type"] else "blue" if "Dikdörtgen" in node["type"] else "orange" if "Eşkenar" in node["type"] else "purple"
                dot.node(node["id"], node["text"], shape=shape, color=color)

            for edge in st.session_state.flow_edges:
                dot.edge(edge["from"], edge["to"], label=edge["label"])

            st.graphviz_chart(dot)

            b1, b2 = st.columns(2)
            if b1.button("🗑️ Şemayı Temizle", use_container_width=True):
                st.session_state.flow_nodes, st.session_state.flow_edges = [], []
                st.rerun()
            if b2.button("✅ Bitti ve Kontrol Et", use_container_width=True):
                node_map = {n['id']: n['text'] for n in st.session_state.flow_nodes}
                schema_desc = " Bağlantılar: " + " | ".join([f"{node_map[e['from']]} --({e['label']})--> {node_map[e['to']]}" for e in st.session_state.flow_edges])
                st.session_state.messages.append({"role": "user", "content": f"Algoritma bitti. Şema yapısı: {schema_desc}. Lütfen analiz et."})
                with st.spinner("Kontrol ediliyor..."):
                    res = call_gemini(st.session_state.messages)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                    st.rerun()

# --- 2. SOHBET AKIŞI (TASARIM ALANININ ALTINDA) ---
st.divider()
for message in st.session_state.messages:
    if not message["content"].startswith("SİSTEM:"):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Sohbet girişi her zaman en altta kalır
if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Düşünüyorum..."):
            res = call_gemini(st.session_state.messages)
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})