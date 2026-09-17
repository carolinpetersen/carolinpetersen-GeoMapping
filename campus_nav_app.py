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
import math



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

# =============================================================================
# Manuell festgelegte Landmarken: Nur DIESE Orte werden in der Wegbeschreibung
# als "vorbei an..." genannt (große, gut sichtbare Gebäude/Orte)
# =============================================================================
LANDMARKEN = [
    "Mensa",
    "Universitätsbibliothek",
    "Hochschulsport",
    "Leuphana Universität Lüneburg Zentralgebäude C40",
    "PENNY",
    "Erstsemesterwohnheim",
    "Studio 21",
    "Kindertagesstätte Campus",
    "Biotopgarten",
    "Gebäude 1",
    "Gebäude 3",
    "Gebäude 4",
    "Gebäude 5",
    "Gebäude 6",
    "Gebäude 7",
    "Gebäude 8",
    "Gebäude 9",
    "Gebäude 10",
    "Gebäude 11",
    "Gebäude 12",
    "Gebäude 13",
    "Gebäude 14",
    "Gebäude 16",
    "Gebäude 19",
    "Gebäude 22",
    "Gebäude 25",
    "Gebäude 26",
    "Gebäude 27",
    "Gebäude 40",
    # ➕ Hier kannst du jederzeit weitere Orte ergänzen oder welche entfernen
]

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
# Funktion: Kompasswinkel (Bearing) zwischen zwei Punkten berechnen
# =============================================================================
def bearing(x1, y1, x2, y2):
    delta_x = x2 - x1
    delta_y = y2 - y1
    angle = math.degrees(math.atan2(delta_x, delta_y))  # 0° = Norden, 90° = Osten
    return angle % 360


# =============================================================================
# Funktion: Abbiegerichtung zwischen zwei Bearings bestimmen
# =============================================================================
def abbiege_richtung(bearing_vorher, bearing_nachher, schwelle=25):
    diff = (bearing_nachher - bearing_vorher + 180) % 360 - 180
    if diff > schwelle:
        return "rechts"
    elif diff < -schwelle:
        return "links"
    else:
        return None  # keine relevante Richtungsänderung


# =============================================================================
# Funktion: Auf welcher Seite liegt ein Punkt relativ zur Gehrichtung?
# =============================================================================
def seite_von_punkt(x1, y1, x2, y2, px, py):
    cross = (x2 - x1) * (py - y1) - (y2 - y1) * (px - x1)
    if cross > 0:
        return "links"
    elif cross < 0:
        return "rechts"
    else:
        return "direkt auf dem Weg"


# =============================================================================
# Funktion: Abbiegungen entlang der gesamten Route berechnen
# =============================================================================
def berechne_abbiegungen(G_proj, route, schwelle=45, min_abstand=30):
    koordinaten = [(G_proj.nodes[n]["x"], G_proj.nodes[n]["y"]) for n in route]
    abbiegungen = []
    i = 1

    while i < len(koordinaten) - 1:
        x1, y1 = koordinaten[i - 1]
        x2, y2 = koordinaten[i]
        x3, y3 = koordinaten[i + 1]

        dist_vor = math.hypot(x2 - x1, y2 - y1)
        dist_nach = math.hypot(x3 - x2, y3 - y2)
        if dist_vor < min_abstand or dist_nach < min_abstand:
            i += 1
            continue

        b_vor = bearing(x1, y1, x2, y2)
        b_nach = bearing(x2, y2, x3, y3)
        richtung = abbiege_richtung(b_vor, b_nach, schwelle)

        if richtung:
            abbiegungen.append((i, richtung))

        i += 1

    return abbiegungen

# =============================================================================
# Hilfsfunktion: Echter Abstand + Position eines Punktes zu einem Liniensegment
# (genauer als nur die Distanz zu den beiden Endpunkten zu vergleichen)
# =============================================================================
def abstand_zu_segment(px, py, x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1
    laenge_quadrat = dx * dx + dy * dy

    if laenge_quadrat == 0:
        t = 0.0
    else:
        t = ((px - x1) * dx + (py - y1) * dy) / laenge_quadrat
        t = max(0.0, min(1.0, t))  # auf das Segment begrenzen

    naechster_x = x1 + t * dx
    naechster_y = y1 + t * dy
    distanz = math.hypot(px - naechster_x, py - naechster_y)
    return distanz
# =============================================================================
# Funktion: Orte entlang der Route MIT Seitenangabe (links/rechts) finden
# =============================================================================
def orte_entlang_route_mit_seite(G_proj, route, orte, transformer, max_distance=40, ausschluss=None):
    if ausschluss is None:
        ausschluss = []

    koordinaten = [(G_proj.nodes[n]["x"], G_proj.nodes[n]["y"]) for n in route]
    gefunden = []

    for name, (lat, lon) in orte.items():
        if name not in LANDMARKEN or name in ausschluss:
            continue

        ort_x, ort_y = transformer.transform(lon, lat)

        bester_index = None
        beste_distanz = float("inf")

        for i in range(len(koordinaten) - 1):
            x1, y1 = koordinaten[i]
            x2, y2 = koordinaten[i + 1]
            d = abstand_zu_segment(ort_x, ort_y, x1, y1, x2, y2)

            if d < beste_distanz:
                beste_distanz = d
                bester_index = i

        if bester_index is not None and beste_distanz <= max_distance:
            x1, y1 = koordinaten[bester_index]
            x2, y2 = koordinaten[bester_index + 1]
            seite = seite_von_punkt(x1, y1, x2, y2, ort_x, ort_y)
            gefunden.append((bester_index, name, seite))

    gefunden.sort(key=lambda tup: tup[0])

    ergebnis = []
    for index, name, seite in gefunden:
        if not ergebnis or ergebnis[-1][1] != name:
            ergebnis.append((index, name, seite))

    return ergebnis

# =============================================================================
# Funktion: Abbiegungen + Orte in echter Reihenfolge kombinieren
# =============================================================================
def kombiniere_ereignisse(abbiegungen, orte_mit_seite):
    ereignisse = []

    for index, richtung in abbiegungen:
        ereignisse.append((index, f"An dieser Stelle {richtung} abbiegen"))

    for index, name, seite in orte_mit_seite:
        ereignisse.append((index, f"Vorbei an '{name}' (liegt auf der {seite}en Seite)"))

    ereignisse.sort(key=lambda tup: tup[0])

    return [text for _, text in ereignisse]

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
        with st.spinner("🧠 Fragt LLM (AcademicCloud) ab..."):
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
                {"role": "system", "content": "Du bist ein entspannter, lässiger Kumpel, der seinen Freund:innen auf dem Campus den Weg zeigt. Du sprichst locker, modern und mit einem Augenzwinkern – wie ein junger Studi, nicht wie eine Behörde. Nutze gerne Umgangssprache, coole Ausdrücke und einen lockeren Ton, aber bleib klar verständlich."},
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

                        # Abbiegungen berechnen (basiert auf echter Geometrie!)
                        abbiegungen = berechne_abbiegungen(G_proj, route, schwelle=25, min_abstand=15)

                        # Orte MIT Seitenangabe entlang der Route finden
                        orte_mit_seite = orte_entlang_route_mit_seite(
                            G_proj, route, ORTE, transformer,
                            max_distance=40,
                            ausschluss=[start_ort, ziel_ort]
                        )

                        # Alles in echter Reihenfolge kombinieren
                        ereignisse_liste = kombiniere_ereignisse(abbiegungen, orte_mit_seite)
                        if ereignisse_liste:
                            ereignisse_text = "\n".join(f"- {e}" for e in ereignisse_liste)
                        else:
                            ereignisse_text = "- Direkter Weg ohne markante Abbiegungen oder Orientierungspunkte"

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

FAKTEN ZUR ROUTE (in exakter Reihenfolge, wie man sie auf dem Weg erlebt):
{ereignisse_text}

STRIKTE REGELN:
1. JEDE Abbiegung aus der obigen Liste MUSS in der Beschreibung vorkommen - lasse KEINE weg.
2. Nenne bei jeder Abbiegung IMMER die Richtung (links oder rechts), niemals nur "biegen Sie ab".
2b. Übernehme die Wörter "links" und "rechts" EXAKT wie oben angegeben - vertausche sie NIEMALS und ändere sie NICHT.
3. Nenne NUR die oben aufgeführten Orte als Orientierungspunkte - keine weiteren Gebäude oder Objekte erfinden.
4. Wenn kein Ort in der Nähe einer Abbiegung genannt ist, beschreibe nur die Abbiegung selbst (z. B. "Biegen Sie rechts ab").
5. Erfinde KEINE Ampeln, Kreuzungen, Straßennamen oder Details, die nicht oben stehen.
6. Gib NUR nummerierte Schritte aus - keine Einleitung, keine Überschrift, keine Zusammenfassung am Ende.
7. Schreibe locker, cool und modern - wie ein:e Student:in, der/die einem Kumpel den Weg erklärt. Nutze ruhig Wörter wie "chillst", "geradeaus", "checkst", "biegste ab" statt förmlicher Sprache wie "Sie biegen ab, bitte folgen Sie...".

Beispiel für den STIL (nicht den Inhalt!):
1. Starten Sie bei {start_ort} und gehen Sie geradeaus.
2. Biegen Sie rechts ab.
3. Sie kommen an [Ort] vorbei, der auf der linken Seite liegt.
4. Biegen Sie links ab und folgen Sie dem Weg bis {ziel_ort}.
"""

                            with st.spinner("🗣️ Generiere Wegbeschreibung..."):
                                beschreibung = query_academiccloud(
                                    messages=[
                                        {"role": "system", "content": "Du bist ein freundlicher, präziser Wegweiser für einen Uni-Campus."},
                                        {"role": "user", "content": beschreibung_prompt}
                                    ],
                                    max_tokens=5000,
                                    temperature=0.1
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