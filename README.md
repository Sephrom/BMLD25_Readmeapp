# BMLD25 ReadMeApp

## Kurzbeschreibung

Die ReadMeApp ist eine Streamlit-Anwendung zur digitalen Verwaltung von PDF-Lernmaterialien. Lehrpersonen koennen Dokumente hochladen, Klassen zuweisen, Fristen setzen und optional Quizfragen erstellen. Schuelerinnen und Schueler sehen nur die ihnen zugewiesenen Dokumente, koennen diese lesen, als gelesen markieren und ein Quiz absolvieren.

Ziel der Anwendung ist es, Lehrpersonen eine einfache Uebersicht darueber zu geben, welche Lernmaterialien von welchen Lernenden bearbeitet wurden.

## Zielgruppe

- Lehrpersonen, die Dokumente digital bereitstellen und den Bearbeitungsstand nachvollziehen moechten
- Schuelerinnen und Schueler, die zugewiesene Unterlagen lesen und ihren Fortschritt pruefen moechten

## Hauptfunktionen

### Lehrpersonen

- Registrierung als Lehrperson mit separatem Zugangscode
- PDF-Dokumente in Ordnern/Klassen hochladen
- Fristen fuer Dokumente setzen
- Quizfragen pro Dokument erstellen
- Dokumente bestimmten Klassen zuweisen
- Aktivitaeten der Schuelerinnen und Schueler einsehen
- Statusanzeige mit Ampellogik:
  - Gruen: erledigt
  - Gelb: gelesen, Quiz noch offen
  - Rot: nicht begonnen oder ueberfaellig

### Schuelerinnen und Schueler

- Registrierung mit Klassenzuweisung
- Anzeige der zugewiesenen Dokumente
- PDF-Dokumente direkt in der App ansehen
- Dokumente als gelesen markieren
- Quiz absolvieren
- Eigene Fortschritte im Profil ansehen

## Installation

### Voraussetzungen

- Python 3.9 oder neuer
- Zugang zu einem kompatiblen WebDAV-Speicher
- Streamlit Community Cloud oder lokale Streamlit-Installation

### Lokale Installation

1. Repository herunterladen oder klonen.

2. In den Projektordner wechseln:

```bash
cd BMLD25_Readmeapp
```

3. Abhaengigkeiten installieren:

```bash
pip install -r requirements.txt
```

4. Lokale Secrets-Datei erstellen:

```text
.streamlit/secrets.toml
```

5. App starten:

```bash
streamlit run app.py
```

## Konfiguration der Secrets

Die App benoetigt Zugangsdaten fuer WebDAV und Authentifizierungswerte. Lokal werden diese in `.streamlit/secrets.toml` gespeichert. In Streamlit Community Cloud muessen dieselben Werte unter **Manage app -> Settings -> Secrets** eingetragen werden.

Beispiel:

```toml
[webdav]
base_url = "https://drive.switch.ch/remote.php/webdav/"
username = "deine-mail@example.ch"
password = "dein-webdav-app-passwort"

[auth]
teacher_code = "LEHRER2025"
cookie_key = "eine-lange-zufaellige-geheime-zeichenkette"
```

Wichtig:

- `teacher_code` ist der Code, mit dem sich Lehrpersonen registrieren koennen.
- `cookie_key` sollte eine lange, zufaellige Zeichenkette sein.
- Das WebDAV-Passwort sollte ein App-Passwort/App-Passcode sein, nicht zwingend das normale Login-Passwort.
- Echte Secrets duerfen nicht ins GitHub-Repository committed werden.

## Projektstruktur

```text
BMLD25_Readmeapp/
  app.py
  requirements.txt
  README.md
  utils/
    data_handler.py
    data_manager.py
    document_manager.py
    log_manager.py
    login_manager.py
  functions/
    class_management_functions.py
    profile_functions.py
    student_archive_functions.py
    teacher_archive_functions.py
    ui_helpers.py
  views/
    home.py
    archive_student.py
    archive_teacher.py
    class_assignment.py
    profile.py
  docs/
    Persona.md
    Product-Roadmap.md
    Wireframe-Nutzertest.md
```

## Wichtige Module

- `app.py`: Einstiegspunkt, Login und rollenbasierte Navigation
- `utils/data_manager.py`: Verbindung zu WebDAV oder lokalem Dateisystem
- `utils/document_manager.py`: Verwaltung von Dokumenten, Quiz, Metadaten und Klassenzuweisungen
- `utils/log_manager.py`: Speichert und berechnet Bearbeitungsstatus
- `utils/login_manager.py`: Registrierung, Login und Rollenlogik
- `views/archive_teacher.py`: Lehreransicht fuer Upload, Quiz, Zuweisung und Fortschritt
- `views/archive_student.py`: Schueleransicht fuer Dokumente, Lesen und Quiz

## Manuelles Testprotokoll

Vor einer Abgabe oder Praesentation sollte folgender Ablauf getestet werden:

1. App lokal oder in Streamlit Cloud starten.
2. Neue Lehrperson mit gueltigem `teacher_code` registrieren.
3. Neue Schuelerin oder neuen Schueler registrieren.
4. In der Lehreransicht eine Klasse erstellen.
5. Schuelerin oder Schueler einer Klasse zuweisen.
6. PDF-Dokument hochladen und Frist setzen.
7. Optional ein Quiz mit vollstaendigen Fragen erstellen.
8. Dokument einer Klasse zuweisen.
9. Mit Schueleraccount einloggen.
10. Zugewiesenes Dokument oeffnen.
11. Dokument als gelesen markieren.
12. Falls vorhanden: Quiz absolvieren.
13. Mit Lehreraccount einloggen und Status kontrollieren.

## Bekannte Grenzen

- Die App nutzt Dateien auf WebDAV als einfache Datenhaltung. Bei sehr vielen gleichzeitigen Nutzenden kann es zu Konflikten kommen.
- Es gibt keine feingranulare Rechteverwaltung ausser den Rollen `teacher` und `student`.
- Quizfragen unterstuetzen aktuell Multiple-Choice mit vier Antwortoptionen.
- Es gibt noch keine automatische Benachrichtigung bei neuen oder ueberfaelligen Dokumenten.
- Die App enthaelt aktuell kein automatisiertes Test-Setup.

## Moegliche Weiterentwicklung

- Automatisierte Tests fuer Statuslogik und Dateiverwaltung
- Bessere Dashboard-Uebersicht pro Klasse
- Benachrichtigungen bei neuen Dokumenten oder Fristueberschreitungen
- Export von Fortschrittsdaten als CSV
- Erweiterung des Quizsystems um weitere Fragetypen
- Verbesserte UI-Struktur mit Tabs fuer Upload, Quiz, Klassen und Fortschritt

## Autorinnen und Autoren

- Bal Jasleen (baljas01@students.zhaw.ch)
- Britone Luana (birtolua@students.zhaw.ch)
- Suter Kaj (suterkaj@students.zhaw.ch)
- Trueb Larissa (trueblar@students.zhaw.ch)

Das Grundgeruest der App wurde im Rahmen des Unterrichts bereitgestellt und im Projekt weiterentwickelt.
