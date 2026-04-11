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
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                return response.json()['candidates'][0]['content']['parts'][0]['text']
            elif response.status_code in [429, 503]:
                time.sleep(5)
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

    if st.button("📚 Konu Tekrarı", use_container_width=True):
        st.session_state.mode = "chat"
        st.session_state.messages = [{"role": "user", "content": f"SİSTEM: {SYSTEM_INSTRUCTIONS}\n\nGÖREV: Merhaba! Öğrenciye konuyu anlatmaya başla."}]
        with st.spinner("Hazırlanıyor..."):
            res = call_gemini(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

    if st.button("📐 Akış Şeması İnşası", use_container_width=True):
        st.session_state.mode = "flowchart"
        st.session_state.flow_nodes, st.session_state.flow_edges = [], []
        flow_cmd = f"SİSTEM: {SYSTEM_INSTRUCTIONS}\n\nGÖREV: Öğrenciye içinde KARAR yapısı olan bir problem ver."
        st.session_state.messages.append({"role": "user", "content": flow_cmd})
        with st.spinner("Senaryo oluşturuluyor..."):
            res = call_gemini(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

    if st.button("🎁 Girdi-Çıktı Kutusu", use_container_width=True):
        st.session_state.mode = "blackbox"
        st.session_state.messages = []
        box_cmd = f"SİSTEM: {SYSTEM_INSTRUCTIONS}\n\nGÖREV: Girdi-Çıktı oyununu başlat. Hemen bir örnek (Girdi: X, Çıktı: Y) ver."
        st.session_state.messages.append({"role": "user", "content": box_cmd})
        with st.spinner("Kutu hazırlanıyor..."):
            res = call_gemini(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

    if st.button("🔧 Algoritma Tamirhanesi", use_container_width=True):
        st.session_state.mode = "repair"
        repair_cmd = (
            f"SİSTEM: {SYSTEM_INSTRUCTIONS}\n\n"
            "GÖREV: Algoritma Tamirhanesi modunu başlat. Karışık adımlı bir senaryo ver. "
            "ÖNEMLİ: Öğrenci yanlış bildiğinde asla doğru sırayı söyleme, sadece mantık hatasını bir soruyla hatırlat."
        )
        st.session_state.messages.append({"role": "user", "content": repair_cmd})
        with st.spinner("Arıza tespit ediliyor..."):
            res = call_gemini(st.session_state.messages)
            st.session_state.messages.append({"role": "assistant", "content": res})
            st.rerun()

    st.divider()
    if st.button("🗑️ Her Şeyi Sıfırla", use_container_width=True):
        st.session_state.messages, st.session_state.flow_nodes, st.session_state.flow_edges, st.session_state.mode = [], [], [], "chat"
        st.rerun()

st.title("🤖 StepWise: Algoritmik Düşünme Mentoru")

if st.session_state.mode == "repair":
    st.info("🔧 **Tamirhane Modu:** Aşağıdaki adımlar birbirine karışmış! Onları mantıklı bir sıraya dizebilir misin? Cevabını harflerle (Örn: B-A-C) sohbet kısmına yazabilirsin.")

elif st.session_state.mode == "flowchart":
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
            bc1, bc2, bc3, bc4 = st.columns([2, 2, 2, 1])
            with bc1:
                source = st.selectbox("Kaynak:", options=st.session_state.flow_nodes, format_func=lambda x: f"{x['id']}: {x['text']}")
            with bc2:
                target = st.selectbox("Hedef:", options=st.session_state.flow_nodes, format_func=lambda x: f"{x['id']}: {x['text']}")
            with bc3:
                label = st.selectbox("Yol:", ["", "Evet", "Hayır"]) if "Eşkenar" in source["type"] else ""
            with bc4:
                st.write("")
                if st.button("🔗 Bağla", use_container_width=True):
                    st.session_state.flow_edges.append({"from": source["id"], "to": target["id"], "label": label})
                    st.rerun()
            dot = graphviz.Digraph()
            for node in st.session_state.flow_nodes:
                shape = "ellipse" if "Elips" in node["type"] else "box" if "Dikdörtgen" in node["type"] else "diamond" if "Eşkenar" in node["type"] else "parallelogram"
                dot.node(node["id"], node["text"], shape=shape, color="blue", style="filled", fillcolor="white")
            for edge in st.session_state.flow_edges:
                dot.edge(edge["from"], edge["to"], label=edge["label"])
            st.graphviz_chart(dot)
            b1, b2 = st.columns(2)
            if b1.button("🗑️ Şemayı Temizle"):
                st.session_state.flow_nodes, st.session_state.flow_edges = [], []
                st.rerun()
            if b2.button("✅ Bitti ve Kontrol Et"):
                node_map = {n['id']: n['text'] for n in st.session_state.flow_nodes}
                schema_desc = " | ".join([f"{node_map[e['from']]} -> {node_map[e['to']]} ({e['label']})" for e in st.session_state.flow_edges])
                st.session_state.messages.append({"role": "user", "content": f"Algoritma bitti: {schema_desc}"})
                with st.spinner("Kontrol ediliyor..."):
                    res = call_gemini(st.session_state.messages)
                    st.session_state.messages.append({"role": "assistant", "content": res})
                    st.rerun()

elif st.session_state.mode == "blackbox":
    with st.container(border=True):
        st.subheader("🎁 Sihirli Kara Kutu")
        box_viz = graphviz.Digraph()
        box_viz.attr(rankdir='LR')
        box_viz.node("IN", "Girdi", shape="parallelogram", style="filled", fillcolor="#E1BEE7")
        box_viz.node("BOX", "???", shape="box", style="filled", fillcolor="#212121", fontcolor="white")
        box_viz.node("OUT", "Çıktı", shape="parallelogram", style="filled", fillcolor="#C8E6C9")
        box_viz.edge("IN", "BOX"); box_viz.edge("BOX", "OUT")
        st.graphviz_chart(box_viz)

st.divider()
for message in st.session_state.messages:
    if not message["content"].startswith("SİSTEM:"):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

if prompt := st.chat_input("Mesajını yaz..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        res = call_gemini(st.session_state.messages)
        st.markdown(res)
        st.session_state.messages.append({"role": "assistant", "content": res})