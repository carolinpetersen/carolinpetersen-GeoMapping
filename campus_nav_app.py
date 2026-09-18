# =============================================================================
# 🌐 Campus-Navigationssystem – Web-App mit Streamlit 
# =============================================================================

import streamlit as st
import requests
import networkx as nx
import folium
import osmnx as ox
import pyproj
from streamlit_folium import st_folium
from dotenv import load_dotenv
import os
from campus_orte import ORTE
import math
import random
import re



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
    "Mensa": ["Mensa", "Essen", "Mittagessen", "Kantine"],
    "Hochschulsport": ["Sport","Turnhalle"],
    "Leuphana Mensawiese": ["Mensawiese", "Wiese"],
    "Gebäude 3": ["Gebäude 3", "3"],
    "Erstsemesterwohnheim": ["Erstsemester", "Erstis", "Wohnheim", "Wohnung", "Studenten"],
    "Scharnhorststraße": ["Scharnhorststraße", "Scharnhorst"],
    "Heinrich-Böll-Straße": ["Heinrich-Böll", "Böll"],
    "Gebäude 8": ["Gebäude 8", "8"],
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
def query_academiccloud(messages, max_tokens=1500, temperature=0.7, reasoning=False):
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "chat_template_kwargs": {"enable_thinking": reasoning}
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
# Funktion: ALLE passenden Orte finden (nicht nur den ersten Treffer)
# Wichtig für Fälle wie "Kaffee" -> Klippo UND Gondel
# =============================================================================
def finde_alle_orte(suchbegriff, ort_bedeutungen, orte_koordinaten):
    suchbegriff = suchbegriff.lower()

    exakte_treffer = []
    teil_treffer = []

    for ort_name, bedeutungen_liste in ort_bedeutungen.items():
        if ort_name not in orte_koordinaten:
            continue

        # ✅ NEU: Den offiziellen Ortsnamen selbst ebenfalls als "Bedeutung" mit einbeziehen
        alle_begriffe = [ort_name] + bedeutungen_liste

        gefunden = False
        for begriff in alle_begriffe:
            begriff_lower = begriff.lower()
            if suchbegriff == begriff_lower:
                exakte_treffer.append((ort_name, orte_koordinaten[ort_name]))
                gefunden = True
                break
            # ✅ FIX: Beide Richtungen prüfen (kurzes Wort in langem Suchbegriff, oder umgekehrt)
            elif begriff_lower in suchbegriff or suchbegriff in begriff_lower:
                teil_treffer.append((ort_name, orte_koordinaten[ort_name]))
                gefunden = True
                break

    # Exakte Treffer haben Vorrang - nur wenn keine da sind, Teiltreffer nutzen
    if exakte_treffer:
        return exakte_treffer
    return teil_treffer
# =============================================================================
# Funktion: Beste Kombination aus mehreren Start-/Zielkandidaten finden
# Berechnet für JEDE Kombination die Weglänge und gibt die kürzeste zurück
# =============================================================================
def beste_kombination_finden(G_proj, transformer, start_kandidaten, ziel_kandidaten):
    beste_kombination = None
    kuerzeste_distanz = float("inf")

    for start_name, (start_lat, start_lon) in start_kandidaten:
        start_x, start_y = transformer.transform(start_lon, start_lat)
        orig = ox.nearest_nodes(G_proj, start_x, start_y)

        for ziel_name, (ziel_lat, ziel_lon) in ziel_kandidaten:
            ziel_x, ziel_y = transformer.transform(ziel_lon, ziel_lat)
            dest = ox.nearest_nodes(G_proj, ziel_x, ziel_y)

            if orig == dest:
                continue  # macht keinen Sinn, Start = Ziel

            try:
                distanz = nx.shortest_path_length(G_proj, orig, dest, weight="length")
            except nx.NetworkXNoPath:
                continue  # kein Weg zwischen diesen Punkten vorhanden

            if distanz < kuerzeste_distanz:
                kuerzeste_distanz = distanz
                beste_kombination = {
                    "start_name": start_name,
                    "start_coords": (start_lat, start_lon),
                    "ziel_name": ziel_name,
                    "ziel_coords": (ziel_lat, ziel_lon),
                    "orig": orig,
                    "dest": dest,
                }

    return beste_kombination

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
# Funktion: Wegbeschreibung DETERMINISTISCH aus den Fakten bauen
# Garantiert 100% korrekte Richtungen - keine KI involviert
# =============================================================================

START_PHRASEN = [
    "Alles klar, du startest bei {start} und läufst erstmal geradeaus.",
    "Los geht's bei {start} – erstmal schön geradeaus weiter.",
    "Du bist bei {start}? Perfekt, dann einfach geradeaus starten.",
]

RICHTUNG_PHRASEN = [
    "Jetzt biegste {richtung} ab.",
    "An dieser Stelle geht's {richtung} weiter.",
    "Hier musst du {richtung} abbiegen.",
    "Ab hier nimmst du die {richtung}e Abzweigung.",
]

LANDMARK_PHRASEN = [
    "Du kommst an {name} vorbei – liegt auf der {seite}en Seite.",
    "Gleich taucht {name} auf, auf deiner {seite}en Seite.",
    "Check {name} ab, den siehst du auf der {seite}en Seite.",
    "{name} liegt dann auf der {seite}en Seite von dir.",
]

END_PHRASEN = [
    "Und schon bist du bei {ziel} angekommen!",
    "Kurz danach stehst du auch schon bei {ziel}.",
    "Dann hast du's geschafft – willkommen bei {ziel}!",
]


def erstelle_wegbeschreibung(start_ort, ziel_ort, abbiegungen, orte_mit_seite):
    ereignisse = []
    for index, richtung in abbiegungen:
        ereignisse.append((index, "abbiegung", richtung, None))
    for index, name, seite in orte_mit_seite:
        ereignisse.append((index, "landmarke", name, seite))

    ereignisse.sort(key=lambda tup: tup[0])

    saetze = [random.choice(START_PHRASEN).format(start=start_ort)]

    for _, typ, wert1, wert2 in ereignisse:
        if typ == "abbiegung":
            satz = random.choice(RICHTUNG_PHRASEN).format(richtung=wert1)
        else:
            satz = random.choice(LANDMARK_PHRASEN).format(name=wert1, seite=wert2)
        saetze.append(satz)

    saetze.append(random.choice(END_PHRASEN).format(ziel=ziel_ort))

    text = "\n".join(f"{i+1}. {satz}" for i, satz in enumerate(saetze))
    return text

# =============================================================================
# Hilfsfunktion: Zählt nummerierte Schritte in einem Text (z.B. "1.", "2.", ...)
# =============================================================================
def zaehle_schritte(text):
    return len(re.findall(r"^\d+\.", text, re.MULTILINE))
# =============================================================================
# Funktion: KI poliert den fertigen Text nur sprachlich - Fakten bleiben geschützt
# =============================================================================
def poliere_mit_ki(roher_text):
    anzahl_schritte_original = zaehle_schritte(roher_text)

    polier_prompt = f"""
Hier ist eine technisch korrekte, aber etwas roboterhafte Wegbeschreibung mit GENAU {anzahl_schritte_original} Schritten:

{roher_text}

Formuliere sie natürlicher und lockerer, wie ein Studi das einem Kumpel erklären würde.

WICHTIG:
- Die Ausgabe MUSS GENAU {anzahl_schritte_original} nummerierte Schritte enthalten - nicht mehr, nicht weniger.
- Fasse KEINE zwei Schritte zusammen. Lasse KEINEN Schritt weg.
- Ändere NIEMALS die Wörter "links" oder "rechts".
- Ändere NIEMALS Gebäude-/Ortsnamen.
- Ändere NICHT die Reihenfolge der Schritte.
- Du darfst NUR den sprachlichen Ausdruck jedes einzelnen Schrittes verbessern, NICHT den Inhalt oder die Anzahl.
- Gib nur nummerierte Schritte aus, keine Einleitung, keine Zusammenfassung.
"""
    polierter_text = query_academiccloud(
        messages=[
            {"role": "system", "content": "/no_think Du polierst Texte sprachlich auf, ohne Fakten zu verändern. Du bist locker und freundlich wie ein Studi."},
            {"role": "user", "content": polier_prompt}
        ],
        max_tokens=1500,
        temperature=0.3,
        reasoning=False
    )

    if not polierter_text:
        return roher_text

    # ✅ Sicherheitsnetz: Prüfen, ob die KI wirklich ALLE Schritte übernommen hat
    anzahl_schritte_poliert = zaehle_schritte(polierter_text)
    if anzahl_schritte_poliert != anzahl_schritte_original:
        st.warning(f"⚠️ KI-Politur hat Schritte verändert ({anzahl_schritte_original} → {anzahl_schritte_poliert}). Nutze garantiert vollständige Version.")
        return roher_text

    return polierter_text

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
            

            messages = [
                {"role": "system", "content": "/no_think Du bist ein präziser Campus-Navigationssystem. Gib nur die Antwort im vorgegebenen Format aus."},
                {"role": "user", "content": prompt}
            ]

            response = query_academiccloud(messages, max_tokens=500, reasoning=False)

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

                start_kandidaten = finde_alle_orte(start_ort, ort_bedeutungen, ORTE)
                ziel_kandidaten = finde_alle_orte(ziel_ort, ort_bedeutungen, ORTE)

                if not start_kandidaten:
                        st.error(f"❌ Startort '{start_ort}' nicht gefunden.")
                elif not ziel_kandidaten:
                        st.error(f"❌ Zielort '{ziel_ort}' nicht gefunden.")
                else:
                        if len(start_kandidaten) > 1 or len(ziel_kandidaten) > 1:
                            namen_start = ", ".join(n for n, _ in start_kandidaten)
                            namen_ziel = ", ".join(n for n, _ in ziel_kandidaten)
                            st.info(f"🔀 Mehrdeutig! Mögliche Startorte: {namen_start} | Mögliche Ziele: {namen_ziel} → berechne kürzeste Kombination...")

                        st.info("📥 Lade Kartendaten...")
                        try:
                            G = ox.graph_from_xml("map-3.osm")
                            st.success("✅ Kartendaten geladen.")
                        except Exception as e:
                            st.error(f"❌ Fehler beim Laden der Karte: {e}")
                            st.stop()

                        st.info("🔍 Suche beste Kombination...")
                        try:
                            G_proj = ox.project_graph(G)
                            zielcrs = G_proj.graph["crs"]
                            transformer = pyproj.Transformer.from_crs("EPSG:4326", zielcrs, always_xy=True)

                            kombination = beste_kombination_finden(
                                G_proj, transformer, start_kandidaten, ziel_kandidaten
                            )
                        except Exception as e:
                            st.error(f"❌ Fehler bei Knotensuche: {e}")
                            st.stop()

                        if kombination is None:
                            st.error("❌ Es konnte keine gültige Route zwischen den gefundenen Orten berechnet werden.")
                            st.stop()

                        # Gewinner-Kombination übernehmen
                        start_ort = kombination["start_name"]
                        ziel_ort = kombination["ziel_name"]
                        start_lat, start_lon = kombination["start_coords"]
                        ziel_lat, ziel_lon = kombination["ziel_coords"]
                        orig = kombination["orig"]
                        dest = kombination["dest"]

                        if len(start_kandidaten) > 1 or len(ziel_kandidaten) > 1:
                            st.success(f"✅ Kürzeste Kombination: **{start_ort}** → **{ziel_ort}**")

                        st.info("🚀 Berechne kürzeste Route...")
                        try:
                            route = nx.shortest_path(G, orig, dest, weight="length")
                            st.success("✅ Route berechnet.")
                        except Exception as e:
                            st.error(f"❌ Fehler bei Routing: {e}")
                            st.stop()

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
                                [ziel_lat, ziel_lon],
                                popup=f"Ziel: {ziel_ort}",
                                icon=folium.Icon(color="red", icon="flag")
                            ).add_to(m)

                            with st.spinner("🗣️ Generiere Wegbeschreibung..."):
                                roher_text = erstelle_wegbeschreibung(
                                    start_ort, ziel_ort, abbiegungen, orte_mit_seite
                                )
                                beschreibung = poliere_mit_ki(roher_text)

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