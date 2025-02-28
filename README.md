# Gradio-Tutor mit Auto-Commits, Git-Tracking & LLM-Analyse

## 📌 Projektziel
Diese Anwendung bietet eine interaktive Umgebung für das Erlernen von C-Programmierung.
Besondere Funktionen:
- **Automatische Versionierung** von Code mittels Git.
- **Copy-Paste-Erkennung** mit adaptiven Fehlern.
- **LLM-gestützter Tutor**, der Fragen beantwortet, aber keine fertigen Lösungen gibt.
- **C-Code-Ausführung mit sicherer Umgebung.**
- **Erstellung eines passwortgeschützten Berichts** über den Lösungsprozess.

## 🛠 Setup & Installation
### 📌 Voraussetzungen
- Python 3.9+
- Git installiert
- Virtuelle Umgebung (venv)
- OPENAI_API_KEY in .env 

### 📌 Installation
1. **Virtuelle Umgebung erstellen und aktivieren**
   ```sh
   python -m venv venv
   source venv/bin/activate  # Mac/Linux
   venv\Scripts\activate  # Windows
   ```
2. **Notwendige Pakete installieren**
   ```sh
   pip install gradio openai fastapi uvicorn matplotlib reportlab cryptography pygit2
   ```
3. **Git-Repository initialisieren**
   ```sh
   git init
   ```

## 🚀 Nutzung
### 📌 Start der Anwendung
```sh
python concept_git.py
```
Die Anwendung wird auf `http://127.0.0.1:7860` gestartet und kann über den Browser genutzt werden.

### 📌 Funktionen
- **Code-Editor & Aufgabenwahl**
  - Aufgaben aus einer Dropdown-Liste auswählen.
  - C-Code im Editor schreiben & versionieren.
- **Automatische Commits & Git-Tracking**
  - Änderungen werden intelligent erfasst und gespeichert.
  - Copy-Paste wird erkannt und dokumentiert.
- **Tutor-Chat**
  - LLM beantwortet Fragen, gibt aber keine Lösungen vor.
- **Code-Ausführung & Debugging**
  - Kompilierung und Ausführung des Codes in der App.
- **Berichtserstellung**
  - Automatische Erstellung eines **PDF-Berichts** über den Lösungsprozess.

## 📄 Projektplan
Der vollständige Plan befindet sich in [`plan.md`](plan.md).

