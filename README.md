# BMLD25_Readmeapp

**Dokument-Management-System für Lehrpersonen und Schüler**

## Überblick

Diese Streamlit-Anwendung ermöglicht Lehrpersonen, Lernmaterialien (PDF-Dokumente) hochzuladen und zu verwalten sowie die Aktivitäten ihrer Schüler nachzuverfolgen. Schüler können zugewiesene Dokumente ansehen, als gelesen markieren und zugehörige Quizzes absolvieren.

Die App richtet sich an Lehrpersonen und Schüler an Schulen, die digitale Lernfortschritte transparent tracken möchten.

---

## Hauptfunktionen

### Für Lehrpersonen

- **Dokumente hochladen**: PDFs in Klassenfolder hochladen mit Fälligkeitsdatum
- **Quiz erstellen**: Quizzes mit bis zu 10 Fragen pro Dokument definieren
- **Klassenzuordnungen**: Dokumente gezielt an Klassen zuweisen
- **Fortschritt überwachen**: Tabellenansicht mit Status (🟢 Erledigt, 🟡 In Arbeit, 🔴 Überfällig)
- **Logdaten einsehen**: Zeitstempel für Öffnen, Lesen, Quiz-Versuche und Scores

### Für Schüler

- **Zugewiesene Dokumente sehen**: Gefilterte Archiv-Ansicht nach Klasse
- **PDFs anzeigen**: Integrierte PDF-Viewer mit Download
- **Gelesen markieren**: Status-Button zur Markierung als gelesen
- **Quizzes absolvieren**: Interaktive Quiz-Formulare mit Bewertung
- **Fortschritt-Anzeige**: Persönlicher Profil-Überblick über alle Dokumente

---

## Installation

### Voraussetzungen

- Python 3.9+
- WebDAV-Zugang (z. B. Switch Drive)
- Streamlit secrets konfiguriert

### Schritt-für-Schritt

1. **Repository klonen / entpacken**

```bash
cd BMLD25_Readmeapp
