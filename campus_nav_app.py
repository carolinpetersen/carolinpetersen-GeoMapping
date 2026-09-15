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
import pyproj
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
from campus_orte import ORTE



ort_bedeutungen = {
    "Universitätsallee": ["Universitätsallee", "Universität", "Campus", "Hauptstraße", "Alle"],
    "Radio Zusa": ["Radio", "Zusa", "Rundfunk", "Radio Zusa"],
    "Taxistand UNI": ["Taxistand UNI", "Taxi", "Taxistand", "Taxi-Station", "Taxi-Platz"],
    "KonRad Fahrrad-Selbsthilfe-Werkstatt": ["Fahrrad", "Konrad", "Werkstatt", "Reparatur", "Selbsthilfe"],
    "PENNY": ["Supermarkt", "Einkauf", "Laden", "Geschäft", "Discounter", "PENNY", "Lebensmittel" ],
    "Wichernstraße": ["Wichernstraße", "Straße", "Wichern"],
    "Carl-von-Ossietzky-Straße": ["Carl-von-Ossietzky", "CVO"],
    "Kindertagesstätte Campus": ["Kindertagesstätte", "Kita", "Kindergarten", "Kinder"],
    "Studio 21": ["Studio 21", "Sport", "Fitness", "Workout", "Gym"],
    "HairNews": ["Friseur", "Haare", "Friseur", "Haarschnitt"],
    "Kruse - Der Lecker Bäcker": ["Bäcker", "Kruse", "Brot", "Kuchen", "Backwaren", "Brötchen"],
    "Alexander Fritz GmbH": ["Firma", "Unternehmen", "Fritz", "GmbH"],
    "planB": ["planB", "Büro", "Büro", "Planung"],
    "Scharnhorststraße": ["Scharnhorst"],
    "Universitätsbibliothek": ["Bibliothek", "Bib", "Bücher", "Lernen", "BIB"],
    "Blücherstraße": ["Blücherstraße", "Blücher"],
    "Geschwister-Scholl-Haus": ["Geschwister-Scholl", "Haus", "GSH"],
    "Zufahrt 1 Leuphana Universität Lüneburg": ["Zufahrt 1"],
    "Klippo": ["Klippo", "Kiosk", "Laden", "Kiosk", "Snack", "Kaffee"],
    "Zufahrt 2 Leuphana Universität Lüneburg": ["Zufahrt 2"],
    "Zufahrt 3 Leuphana Universität Lüneburg": ["Zufahrt 3"],
    "TRAFOS": ["TRAFOS", "Transformator", "Strom", "Energie"],
    "Gondel": ["Gondel", "Kaffee"],
    "Universität": ["Universität", "Campus", "Hauptgebäude", "Hauptgebäude"],
    "Zentraler Campus": ["Campus"],
    "Gneisenaustraße": ["Gneisenaustraße", "Gneisenau"],
    "Gebäude 12": ["Gebäude 12", "12"],
    "Gebäude 13": ["Gebäude 13", "13"],
    "Hochschulsport": ["Sport","Turnhalle"],
    "Leuphana Mensawiese": ["Mensawiese", "Wiese"],
    "Gebäude 3": ["Gebäude 3", "3"],
    "Erstsemesterwohnheim": ["Erstsemester", "Erstis", "Wohnheim", "Wohnung", "Studenten"],
    "Scharnhorststraße": ["Scharnhorststraße", "Scharnhorst"],
    "Heinrich-Böll-Straße": ["Heinrich-Böll", "Böll"],
    "Gebäude 8": ["Gebäude 8", "8"],
    "Mensa": ["Mensa", "Essen", "Mittagessen", "Kantine"],
    "Initiativen-Räume": ["Initiativen", "Initiative"],
    "Gebäude 25": ["Gebäude 25", "25"],
    "Gebäude 27": ["Gebäude 27", "27"],
    "Gebäude 1": ["Gebäude 1", "1"],
    "Gebäude 10": ["Gebäude 10", "10"],
    "Gebäude 11": ["Gebäude 11", "11"],
    "Gebäude 14": ["Gebäude 14", "14"],
    "Campus 1": ["Campus 1", "1"],
    "Gebäude 16": ["Gebäude 16", "16"],
    "Gebäude 19": ["Gebäude 19", "19"],
    "Campus 2": ["Campus 2", "2"],
    "Gebäude 22": ["Gebäude 22", "22"],
    "Campus 3": ["Campus 3", "3"],
    "Gebäude 4": ["Gebäude 4", "4"],
    "Gebäude 5": ["Gebäude 5", "5"],
    "Gebäude 6": ["Gebäude 6", "6"],
    "Gebäude 7": ["Gebäude 7", "7"],
    "Gebäude 9": ["Gebäude 9", "9"],
    "Hörsaal 1": ["Hörsaal 1"],
    "Hörsaal 2": ["Hörsaal 2"],
    "Hörsaal 3": ["Hörsaal 3"],
    "Hörsaal 5": ["Hörsaal 5"],
    "Hörsaalgang": ["Hörsaalgang", "Hörsäle"],
    "Laubgang": ["Laubgang"],
    "Gebäude 26": ["Gebäude 26", "26"],
    "Leuphana Universität Lüneburg Zentralgebäude C40": ["Zentralgebäude", "C40", "Zentral", "Hauptgebäude", "ZG"],
    "Hörsaal 4": ["Hörsaal 4"],
    "Biotopgarten": ["Biotopgarten", "Garten", "Pflanzen", "Natur", "Biotop", "Grünfläche", "grün"],
    "Waldgarten Campus Lüneburg": ["Waldgarten", "Natur"],
    "Biotopbeete": ["Biotopbeete", "Beete", "Pflanzen"],
}

bedeutungen = "\n".join([f"- {ort}: {', '.join(worte)}" for ort, worte in ort_bedeutungen.items()])

# 🔐 Lade Umgebungsvariablen (.env)
load_dotenv()

# Hole API-Key aus Umgebungsvariable
ACADEMICCLOUD_API_KEY = os.getenv("ACADEMICCLOUD_API_KEY")
if not ACADEMICCLOUD_API_KEY:
    st.error("❌ API-Key nicht gefunden. Bitte prüfe deine .env-Datei.")
    st.stop()

# Modell
MODEL_NAME = "qwen3.6-35b-a3b"

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
def query_academiccloud(messages, max_tokens=5000, temperature=0.7):
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
# Funktion: Straßennamen entlang der Route extrahieren
# =============================================================================
def route_strassen(G, route):
    """
    Extrahiert die Straßennamen entlang der berechneten Route,
    ohne Duplikate direkt hintereinander.
    """
    strassen = []
    for u, v in zip(route[:-1], route[1:]):
        data = G.get_edge_data(u, v)
        if data:
            # Bei mehreren parallelen Kanten: erste nehmen
            edge = data[0] if 0 in data else list(data.values())[0]
            name = edge.get("name", None)
            if name:
                if isinstance(name, list):
                    name = name[0]
                if not strassen or strassen[-1] != name:
                    strassen.append(name)
    return strassen

# =============================================================================
# Funktion: Orte entlang der Route finden (in der richtigen Reihenfolge!)
# =============================================================================
def orte_entlang_route(G_proj, route, orte, transformer, max_distance=20, ausschluss=None):
    """
    Findet Orte aus 'orte' (campus_orte.py), die nahe an der berechneten Route liegen.
    Gibt sie SORTIERT zurück - in der Reihenfolge, wie man an ihnen vorbeikommt.
    
    max_distance = wie nah (in Metern) ein Ort an der Route sein muss, um "gezählt" zu werden
    ausschluss = Namen, die NICHT in der Liste erscheinen sollen (z.B. Start & Ziel selbst)
    """
    if ausschluss is None:
        ausschluss = []

    # Koordinaten der Route in Metern (projiziert) sammeln
    route_punkte = []
    for node in route:
        x = G_proj.nodes[node]["x"]
        y = G_proj.nodes[node]["y"]
        route_punkte.append((x, y))

    gefundene_orte = []  # Liste von (Position_auf_Route, Name, Distanz)

    for name, (lat, lon) in orte.items():
        if name in ausschluss:
            continue

        # Ort-Koordinaten in dieselbe Projektion umwandeln wie die Route
        ort_x, ort_y = transformer.transform(lon, lat)

        # Kürzeste Distanz zu irgendeinem Punkt der Route berechnen
        min_dist = float("inf")
        min_index = None
        for i, (rx, ry) in enumerate(route_punkte):
            dist = ((rx - ort_x) ** 2 + (ry - ort_y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                min_index = i

        # Nur behalten, wenn nah genug an der Route
        if min_dist <= max_distance:
            gefundene_orte.append((min_index, name, min_dist))

    # Nach Position entlang der Route sortieren (wichtig für richtige Reihenfolge!)
    gefundene_orte.sort(key=lambda tup: tup[0])

    # Namen extrahieren, Duplikate direkt hintereinander vermeiden
    ergebnis = []
    for _, name, _ in gefundene_orte:
        if not ergebnis or ergebnis[-1] != name:
            ergebnis.append(name)

    return ergebnis
# =============================================================================
# 4. Haupt-App (Streamlit)
# =============================================================================
st.set_page_config(
    page_title="🎓 Campus-Navigation",
    page_icon="🗺️",
    layout="wide"
)

st.title("🗺️ Leupht-wohin?")
st.markdown("Das beste (und einzige) Campus-Navigationssystem für die Leuphana Uni!")

# =============================================================================
# 5. Eingabebereich
# =============================================================================
# ✅ NEU: Session State initialisieren
if "route_data" not in st.session_state:
    st.session_state.route_data = None

with st.container():
    st.subheader("📍 Wo bist du und wo willst du hin?")
    col1, col2 = st.columns(2)

    with col1:
        start_input = st.text_input("Startort", placeholder="Beschreibe wo du bist")
    with col2:
        ziel_input = st.text_input("Zielort", placeholder="Beschreibe wo du hin willst")

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
- Zusätzliche Anforderungen (z. B. barrierefrei, schnell)

Wichtig: Verwende nur Orte aus der folgenden Liste:
{bedeutungen}

Nutzereingabe: "{start_input} nach {ziel_input}"

Antworte **nur** in diesem Format:
Start: [Ort]
Ziel: [Ort]

"""
#wenn mehrer Bedeutungen, dann für jede davon einen Weg berechnen und danach den lürzesten auswählen
#wenn es diese Bedeutung nicht gibt, dann Fehlermeldung
        

            

            messages = [
                {"role": "system", "content": "Du bist ein präziser Campus-Navigationssystem. Gib nur die Antwort im vorgegebenen Format aus."},
                {"role": "user", "content": prompt}
            ]

            response = query_academiccloud(messages, max_tokens=5000)

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
                            G = ox.graph_from_xml("map-3.osm")
                            st.success("✅ Kartendaten geladen.")
                        except Exception as e:
                            st.error(f"❌ Fehler beim Laden der Karte: {e}")
                            st.stop()

                        st.info("🔍 Suche Wegpunkte...")
                        try:
                            # Graph projizieren (nutzt pyproj, KEIN scikit-learn)
                            G_proj = ox.project_graph(G)
                            zielcrs = G_proj.graph["crs"]

                            transformer = pyproj.Transformer.from_crs("EPSG:4326", zielcrs, always_xy=True)
                            start_x, start_y = transformer.transform(start_lon, start_lat)
                            ziel_x, ziel_y = transformer.transform(ziel_lon, ziel_lat)

                            # Nutzt scipy cKDTree (kein scikit-learn nötig)
                            orig = ox.nearest_nodes(G_proj, start_x, start_y)
                            dest = ox.nearest_nodes(G_proj, ziel_x, ziel_y)
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

                     # Straßennamen entlang der Route extrahieren
                        strassen_liste = route_strassen(G, route)
                        if strassen_liste:
                            strassen_text = ", ".join(strassen_liste)
                        else:
                            strassen_text = "keine benannten Straßen gefunden"

                      # Orte entlang der Route finden (in echter Reihenfolge!)
                        orte_auf_weg = orte_entlang_route(
                            G_proj, route, ORTE, transformer,
                            max_distance=20,
                            ausschluss=[start_ort, ziel_ort]
                        )
                        if orte_auf_weg:
                            orte_text = ", ".join(orte_auf_weg)
                        else:
                            orte_text = "keine markanten Orte in der Nähe der Route gefunden"

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
Du bist ein Campus-Navigationssystem für den Leuphana-Campus in Lüneburg.

Erstelle eine klare, schrittweise Wegbeschreibung von "{start_ort}" nach "{ziel_ort}".

FAKTEN ZUR ROUTE (nutze NUR diese Informationen):
- Straßen/Wege der Route, in Reihenfolge: {strassen_text}
- Reale Orte/Gebäude, an denen man auf dem Weg vorbeikommt, in Reihenfolge: {orte_text}

WICHTIG:
- Baue die genannten Orte als Orientierungspunkte in die Beschreibung ein (z. B. "gehen Sie an {orte_auf_weg[0] if orte_auf_weg else '...'} vorbei").
- Erfinde KEINE zusätzlichen Details wie Ampeln, Kreuzungen, Geschäfte oder Gebäude, die NICHT oben genannt wurden.
- Gib nur kurze, klare, nummerierte Anweisungen.
- Keine Einleitung, keine Überschrift.

Beispiel für den Stil (nicht den Inhalt!):
1. Starten Sie bei {start_ort}.
2. Gehen Sie an [Ort aus der Liste] vorbei.
3. Biegen Sie ab und folgen Sie dem Weg bis {ziel_ort}.
"""

                            with st.spinner("🗣️ Generiere Wegbeschreibung..."):
                                beschreibung = query_academiccloud(
                                    messages=[
                                        {"role": "system", "content": "Du bist ein freundlicher, präziser Wegweiser für einen Uni-Campus."},
                                        {"role": "user", "content": beschreibung_prompt}
                                    ],
                                    max_tokens=5000
                                )

                            if beschreibung:
                                folium.Marker(
                                    [start_lat, start_lon],
                                    popup=f"Start: {start_ort}<br><small>{beschreibung}</small>",
                                    icon=folium.Icon(color="green", icon="play")
                                ).add_to(m)

                            st.session_state.route_data = {
                                "map": m,
                                "beschreibung": beschreibung,
                                "start_ort": start_ort,
                                "ziel_ort": ziel_ort
                            }

                        except Exception as e:
                            st.error(f"❌ Fehler bei Karten-Erstellung: {e}")
# =============================================================================
# ✅ NEU: Zeige gespeicherte Ergebnisse an (bleibt auch nach Streamlit-Reruns bestehen)
# =============================================================================
if st.session_state.route_data:
    data = st.session_state.route_data
    st.subheader("📝 Sprachliche Wegbeschreibung")
    st.markdown(data["beschreibung"])
    st_folium(
        data["map"],
        width=800,
        height=500,
        key="route_map",
        returned_objects=[]
    )

# =============================================================================
# 7. Footer
# =============================================================================
st.markdown("---")
st.markdown("💡 *Entwickelt mit ❤️ von Leonie und Caro für den Leuphana-Campus. AcademicCloud-API verwendet.*")