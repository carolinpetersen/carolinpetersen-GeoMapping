# =============================================================================
# 🌐 Campus-Navigationssystem – Web-App mit Streamlit (SICHER)
# =============================================================================
# Nutzt AcademicCloud-API (mit .env), OSMnx, Folium, Streamlit
# Sicherheit: API-Key aus .env geladen
# =============================================================================

import streamlit as st
import requests
import json
import networkx as nx
import folium
import osmnx as ox
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
from campus_orte import ORTE

# 🔐 Lade Umgebungsvariablen (.env)
load_dotenv()

# Hole API-Key aus Umgebungsvariable
ACADEMICCLOUD_API_KEY = os.getenv("ACADEMICCLOUD_API_KEY")
if not ACADEMICCLOUD_API_KEY:
    st.error("❌ API-Key nicht gefunden. Bitte prüfe deine .env-Datei.")
    st.stop()

# Modell
MODEL_NAME = "meta-llama-3.1-8b-instruct"

# API-Endpunkt
API_URL = "https://chat-ai.academiccloud.de/v1/chat/completions"

# Header
headers = {
    "Authorization": f"Bearer {ACADEMICCLOUD_API_KEY}",
    "Content-Type": "application/json"
}

# =============================================================================
# 1. Funktion: LLM über AcademicCloud-API aufrufen
# =============================================================================
def query_academiccloud(messages, max_tokens=150, temperature=0.7):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        else:
            st.error(f"API-Fehler: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Fehler beim API-Aufruf: {e}")
        return None

# =============================================================================
# 2. Funktion: LLM-Antwort parsen
# =============================================================================
def parse_llm_response(response_text):
    lines = response_text.strip().split("\n")
    start = None
    ziel = None
    anforderungen = []
    for line in lines:
        if line.lower().startswith("start:"):
            start = line.split(":", 1)[1].strip()
        elif line.lower().startswith("ziel:"):
            ziel = line.split(":", 1)[1].strip()
        elif line.lower().startswith("anforderungen:"):
            parts = line.split(":", 1)[1].strip().split(",")
            anforderungen = [a.strip() for a in parts if a.strip()]
    return start, ziel, anforderungen

# =============================================================================
# 3. Funktion: Suche Ort in ORTE
# =============================================================================
def finde_ort(suchbegriff, orte):
    suchbegriff = suchbegriff.lower()
    for name in orte:
        if name.lower() == suchbegriff:
            return orte[name]
        if suchbegriff in name.lower():
            st.info(f"🔍 Verwende: {name}")
            return orte[name]
    return None

# =============================================================================
# 4. Haupt-App (Streamlit)
# =============================================================================
st.set_page_config(
    page_title="🎓 Campus-Navigation",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Campus-Navigationssystem")
st.markdown("💡 Einfach Start und Ziel eingeben – wir finden die beste Route!")

# =============================================================================
# 5. Eingabebereich
# =============================================================================
with st.container():
    st.subheader("📍 Woher und wohin?")
    col1, col2 = st.columns(2)

    with col1:
        start_input = st.text_input("Startort", placeholder="z. B. Mensa, Hauptgebäude")
    with col2:
        ziel_input = st.text_input("Zielort", placeholder="z. B. Hochschulsport, Rechenzentrum")

    submit = st.button("🔍 Route berechnen", type="primary", use_container_width=True)

# =============================================================================
# 6. Wenn berechnen geklickt
# =============================================================================
if submit:
    if not start_input or not ziel_input:
        st.warning("Bitte gib Start- und Zielort ein.")
    else:
        with st.spinner("🧠 Fragt LLM (OpenAI) ab..."):
            prompt = f"""
Du bist ein Campus-Navigationssystem. Analysiere die folgende Nutzereingabe und extrahiere:
- Startort
- Zielort
- Zusätzliche Anforderungen (z. B. barrierefrei, schnell)

Nutzereingabe: "{start_input} nach {ziel_input}"

Antworte **nur** in diesem Format:
Start: [Ort]
Ziel: [Ort]
Anforderungen: [Liste, z. B. barrierefrei, schnell]
"""

            messages = [
                {"role": "system", "content": "Du bist ein präziser Campus-Navigationssystem. Gib nur die Antwort im vorgegebenen Format aus."},
                {"role": "user", "content": prompt}
            ]

            response = query_academiccloud(messages, max_tokens=150)

            if not response:
                st.error("❌ Keine Antwort vom LLM erhalten.")
            else:
                st.success("✅ LLM hat Antwort erhalten.")
                st.write("🔍 Extrahiertes Ergebnis:")
                st.code(response)

                start_ort, ziel_ort, anforderungen = parse_llm_response(response)

                if not start_ort or not ziel_ort:
                    st.error("❌ Start oder Ziel konnte nicht extrahiert werden.")
                else:
                    st.info(f"✅ Start: **{start_ort}** → Ziel: **{ziel_ort}**")

                    start = finde_ort(start_ort, ORTE)
                    ziel = finde_ort(ziel_ort, ORTE)

                    if start is None:
                        st.error(f"❌ Startort '{start_ort}' nicht gefunden.")
                    elif ziel is None:
                        st.error(f"❌ Zielort '{ziel_ort}' nicht gefunden.")
                    else:
                        start_lat, start_lon = start
                        ziel_lat, ziel_lon = ziel

                        st.info("📥 Lade Kartendaten...")
                        try:
                            G = ox.graph_from_xml("map-3.osm", simplify=True, retain_all=False, crs="EPSG:3857")
                            st.success("✅ Kartendaten geladen.")
                        except Exception as e:
                            st.error(f"❌ Fehler beim Laden der Karte: {e}")
                            st.stop()

                        st.info("🔍 Suche Wegpunkte...")
                        try:
                            orig = ox.nearest_nodes(G, start_lon, start_lat)
                            dest = ox.nearest_nodes(G, ziel_lon, ziel_lat)
                        except Exception as e:
                            st.error(f"❌ Fehler bei Knotensuche: {e}")
                            st.stop()

                        st.info("🚀 Berechne kürzeste Route...")
                        try:
                            route = nx.shortest_path(G, orig, dest, weight="length")
                            st.success("✅ Route berechnet.")
                        except Exception as e:
                            st.error(f"❌ Fehler bei Routing: {e}")
                            st.stop()

                        st.info("🎨 Erstelle Karte...")
                        try:
                            m = folium.Map(location=[start_lat, start_lon], zoom_start=17)

                            route_coords = []
                            for node in route:
                                y = G.nodes[node]["y"]
                                x = G.nodes[node]["x"]
                                route_coords.append((y, x))
                            folium.PolyLine(route_coords, color="blue", weight=6, opacity=0.8).add_to(m)

                            folium.Marker(
                                [start_lat, start_lon],
                                popup=f"Start: {start_ort}",
                                icon=folium.Icon(color="green", icon="play")
                            ).add_to(m)

                            folium.Marker(
                                [ziel_lat, ziel_lon],
                                popup=f"Ziel: {ziel_ort}",
                                icon=folium.Icon(color="red", icon="flag")
                            ).add_to(m)

                            beschreibung_prompt = f"""
Du bist ein Campus-Navigationssystem. Erstelle eine klare, schrittweise Wegbeschreibung von {start_ort} nach {ziel_ort}.
Verwende einfache Sprache. Gib nur die Anweisungen (keine Überschriften).

Beispiel:
1. Gehen Sie aus der Mensa heraus und folgen Sie der Hauptstraße.
2. Biegen Sie links an der Bibliothek ab.
3. Gehen Sie geradeaus bis zum Hochschulsport.
"""

                            with st.spinner("🗣️ Generiere Wegbeschreibung..."):
                                beschreibung = query_openai(
                                    messages=[
                                        {"role": "system", "content": "Du bist ein freundlicher, präziser Wegweiser für einen Uni-Campus."},
                                        {"role": "user", "content": beschreibung_prompt}
                                    ],
                                    max_tokens=200
                                )

                            if beschreibung:
                                st.subheader("📝 Sprachliche Wegbeschreibung")
                                st.markdown(beschreibung)

                                folium.Marker(
                                    [start_lat, start_lon],
                                    popup=f"Start: {start_ort}<br><small>{beschreibung}</small>",
                                    icon=folium.Icon(color="green", icon="play")
                                ).add_to(m)

                            st_folium(m, width=800, height=500)

                        except Exception as e:
                            st.error(f"❌ Fehler bei Karten-Erstellung: {e}")

# =============================================================================
# 7. Footer
# =============================================================================
st.markdown("---")
st.markdown("💡 *Entwickelt mit ❤️ von Leonie und Caro für den Leuphana-Campus. AcademicCloud-API verwendet.*")