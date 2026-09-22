# UWB-HomeTracker

Web-Anwendung zur Visualisierung einer Indoor-Lokalisierung eines UWB-Tags innerhalb einer simulierten Wohnung

Das Projekt bildet eine Plattform für UWB-basierte Lokalisation ohne reale Hardware. Das Python-Backend simuliert die Signallaufzeiten zwischen vier Ankern und einem Tag und berechnet daraus die geschätzte Position des Tags und stellt sie über eine API-Schnittstelle bereit. Die Webmap wurde mit React.js und OpenLayers erstellt. Diese bildet Position des Tags in Echtzeit auf einem selbst gewählten Wohnungsgrundriss.

---

## Inhaltsverzeichnis

- [Architektur](#architektur)
- [Komponenten](#komponenten)
  - [Python-Backend](#python-backend)
  - [React-Frontend](#react-frontend)
- [Positionsberechnung (TDoA)](#positionsberechnung-tdoa)
- [API-Schnittstelle](#api-schnittstelle)
- [Setup & Ausführung](#setup--ausführung)
- [Genauigkeit der Simulation](#genauigkeit-der-simulation)
- [Bekannte Einschränkungen & Ausblick](#bekannte-einschränkungen--ausblick)

---

## Architektur

Das Projekt besteht aus zwei Komponenten die über eine FastAPI-Schnittstelle kommunizieren 

```
┌─────────────────────────┐        HTTP/JSON        ┌───────────────────────────┐
│   Python-Backend         │  ───────────────────▶   │   React-Webmap             │
│   (Qt-UI + Simulation)   │   /signal, /misc         │   (OpenLayers, Pixel-CRS)  │
└─────────────────────────┘                          └───────────────────────────┘
```

Da beide Seiten ausschließlich über die API kommunizieren, ist die Datenquelle austauschbar. Die Simulation könnte später durch reale UWB-Hardware ersetzt werden, ohne das Frontend anzupassen.

## Komponenten

### Python-Backend

Das Backend übernimmt Setup, Simulation und Bereitstellung der Daten via FastAPI.

| Datei | Aufgabe |
|---|---|
| **`main.py`** | Zentrales Skript mit UI. startet FastAPI in einem Hintergrund-Thread und definiert die Endpunkte `/signal` und `/misc`. Verknüpft alle übrigen Module. |
| **`Floorplan_Processor.py`** | Lässt den Nutzer einen Grundriss aus dem `public`-Verzeichnis der Webmap auswählen. Ermittelt den Bild-`Extent` (Breite/Höhe) und berechnet aus den Pixelfarben eine Maske gültiger Positionen (`valid_positions.npy`) — schwarze bzw. transparente Pixel (Wände/Außenbereich) werden ausgeschlossen, sodass der simulierte Tag nur innerhalb der Wohnung platziert wird. |
| **`Anchor_Picker.py`** | UI zum manuellen Setzen der Anker-Positionen. Klickkoordinaten werden über `mapToScene` in reale Bildpixel umgerechnet. |
| **`UWB_Signals.py`** | Skript zur Simulation. Erzeugt eine zufällige, gültige Tag-Position, berechnet daraus TDoA-Messwerte inkl. Zeitmessrauschen und schätzt die Position per nichtlinearem Least-Squares-Verfahren zurück (siehe [Positionsberechnung](#positionsberechnung-tdoa)). |

Das User Interface bietet vier Aktionen: 
Grundriss festlegen, Anker setzen, eine einzelne zufällige Position simulieren oder eine Serie von Positionen (Implementierung in die WebMap noch verbuggt).

### React-Frontend

Schlichte Webmap im Still von Home Assistent mit drei Ansichten (Home/Karte, About, FAQ).

| Datei | Aufgabe |
|---|---|
| **`header.jsx`** | Navigation zwischen den Seiten sowie ein "Refresh Map"-Button, der die Karte neu initialisiert. |
| **`body.jsx`** | Baut beim Laden aus den Backend-Daten eine **Custom-Pixelprojektion** (`Projection` mit `units: "pixels"`) auf, deren Extent exakt der Grundriss-Auflösung entspricht. Der Grundriss wird als `ImageLayer` (`Static`-Quelle) dargestellt. Ein `VectorLayer` zeigt die vier Anker (grün) sowie den beweglichen Tag (rot). Zoom, Pan, Rotation und sonstige Interaktionen wurden bewusst deaktiviert. Alle 5 Sekunden wird `/signal` erneut abgefragt und die Tag-Koordinate aktualisiert. |
| **`apihandling.jsx`** | Separiert die beiden API_Calls an das Backend damit `body.jsx` cleaner ist. |
| **`about.jsx`** | Kurze Projektbeschreibung. |
| **`faq.jsx`** | Häufige Fragen zu UWB, TDoA und der Simulation. |

## Positionsberechnung (TDoA)

Die Lokalisierung basiert auf **Time Difference of Arrival (TDoA)**:

1. **Wahre Position wählen** — ein zufälliger Punkt aus den zulässigen Pixeln (`valid_positions.npy`) wird als tatsächliche Tag-Position `tag_true` angenommen.
2. **Distanzen berechnen** — der euklidische Abstand von `tag_true` zu jedem der vier Anker wird bestimmt.
3. **TDoA ableiten** — statt absoluter Laufzeiten werden die Laufzeitdifferenzen relativ zu Anker 0 berechnet (`(distanz_i − distanz_0) / c`), wie es ein reales TDoA-System messen würde.
4. **Rauschen hinzufügen** — auf die Zeitdifferenzen wird ein gaußsches Zeitmessrauschen (σ ≈ 0,1 ns) addiert, um reale Messungenauigkeit zu simulieren.
5. **Least-Squares-Schätzung** — ausgehend von einem festen Startwert wird ein ein nichtlineares Gleichungssystem gelöst, das die Positionsschätzung `tag_est` liefert, indem die Residuen zwischen gemessenen und aus der Schätzung resultierenden Distanzdifferenzen minimiert werden.
6. **Fehler bestimmen** — die Distanz zwischen `tag_true` und `tag_est` ergibt den Positionsfehler, der pro Messung in der Konsole ausgegeben wird.

Diese wahre und geschätzte Position sowie der Fehler werden über `/signal` an das Frontend übertragen; die Webmap zeigt ausschließlich `tag_est` als beweglichen Marker an. Die wahre Position und die Abweichung werden in der Konsole ausgegeben

## API-Schnittstelle

FastAPI-Server unter `http://localhost:8000`.

| Endpunkt | Methode | Beschreibung | Antwort |
|---|---|---|---|
| `/` | GET | Default | `{"message": "UWB Signal Simulator API"}` |
| `/signal` | GET | Aktuelle geschätzte, wahre Tag-Position und Fehler in Pixeln. Liefert `400`, solange noch keine Simulation gestartet wurde. | `{"estimated": {"x": .., "y": ..}, "true": {"x": .., "y": ..}, "error": ..}` |
| `/misc` | GET | Grundrisspfad zum /public Ordner, Bild-Extent und Anker-Koordinaten. Liefert `400`, solange kein Grundriss gesetzt wurde. | `{"Floorplan_Path": "/grundriss.png", "Extent": {"x": .., "y": ..}, "Anchors": [[..,..], ...]}` |


## Setup & Ausführung

**Backend:**
```bash
pip install -r requirements.txt
python main.py
```
Anschließend im UI: Siehe Video

**Frontend:**
```bash
npm install
npm run dev
```

Die Webmap ruft die Daten beim Laden bzw. per "Refresh Map" erneut von `http://localhost:8000` ab.

## Genauigkeit der Simulation

Das Zeitmessrauschen ist fest auf σ = 0,1 ns eingestellt, was einer Distanzunsicherheit von rund 3 cm entspricht (c · σ). Da der Least-Squares-Solver ohne Beschränkung des Lösungsraums und mit festem Startwert (`[5.0, 5.0]`) arbeitet, hängt die tatsächlich erreichte Genauigkeit zusätzlich von der Anker-Geometrie und der Lage der simulierten Tag-Position ab. Der Fehler wird bei jeder Messung neu berechnet und ausgegeben, sodass die Lokalisierungsgüte fortlaufend nachvollzogen werden kann.

## Bekannte Einschränkungen & Ausblick

- Moving Position" ist noch nicht vollständig funktional, da die Webmap nur alle 5 Sekunden abfragt, werden schnell aufeinanderfolgenden simulierten Positionen übersprungen.
- Denkbare Erweiterungen: Legende, Historie der Tag-Bewegungen, mobile optimierte Ansicht.
- Perspektivisch ließe sich die Simulation durch reale UWB-Hardware ersetzen, ohne die Webmap anpassen zu müssen, da beide Komponenten ausschließlich über die FastAPI-Schnittstelle gekoppelt sind.

