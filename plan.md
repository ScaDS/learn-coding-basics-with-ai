Plan:
🔹 Projektplan: Gradio-Tutor mit Auto-Commits, Git-Tracking, LLM-Analyse & Adaptiven Fehlern
📌 Ziel

Wir bauen eine Gradio-Webanwendung, die:

    C-Programmieraufgaben stellt
    Automatisch Änderungen versioniert (Git-Tracking & Auto-Commits)
    Copy-Paste erkennt und adaptive Fehler einfügt
    Fragen zum Code beantwortet (LLM-Tutor, aber ohne Lösungen zu verraten!)
    C-Code ausführt und den Output zeigt
    Einen passwortgeschützten Bericht über die gelöste Aufgabe erstellt (Git-Graph, Diffs, Tutor-Feedback, Copy-Paste-Analyse)

🔹 1. Setup & Umgebung vorbereiten
📌 Anforderungen

    Python 3.9+
    Git installiert
    Virtuelle Umgebung (venv)
    Benötigte Libraries:
        gradio – UI
        openai – LLM
        dotenv - laden von .env für API-Calls und Authentifizierung
        reportlab – PDF-Berichte
        cryptography – Passwortschutz für Berichte
        gitpython oder subprocess – Git-Steuerung
        markdown - Formatierung in md-Format 
        docker (optional) – Sichere Code-Ausführung

📝 Schritte

    Virtuelle Umgebung erstellen:

python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

Notwendige Pakete installieren:

pip install gradio openai reportlab cryptography gitpython dotenv markdown


🔹 2. Benutzer- & Aufgabenstruktur
📌 Ziel

    Jeder Teilnehmer erhält ein dauerhaftes Pseudonym, das persistiert wird und über Sessions hinweg gleich bleibt.
    Git-Repo pro Aufgabe UND pro User, um den Fortschritt pro Aufgabe getrennt zu verfolgen.

📌 Umsetzung

    Pseudonym wird einmalig generiert und gespeichert (user_data.json).
    Ordnerstruktur:

    user_codes/
      ├── {pseudonym}/
      │    ├── aufgabe_1/
      │    │    ├── solution.c
      │    │    ├── .git/
      │    │    ├── history.log
      │    │    ├── report.pdf
      │    ├── aufgabe_2/

    Laden des Pseudonyms beim Start: Falls kein Pseudonym existiert, wird eines zufällig generiert.

🔹 3. Auto-Commit-Strategie
📌 Ziel

    Automatische Speicherung und Versionierung ohne User-Interaktion.
    Commit nur bei signifikanten Änderungen, nicht bei jedem Tastenanschlag.

📌 Umsetzung

    Änderungserkennung:
        git diff wird genutzt, um den neuen Code mit der letzten Version zu vergleichen.
        Commit nur, wenn mind. 10 Zeichen oder 3 Zeilen geändert wurden.
    Timer-Fallback:
        Alle 60 Sekunden ein Commit, falls Änderungen vorhanden sind.
    Commit-Nachrichten automatisch generieren:
        Statt manuelle Commit-Messages: Diff-Analyse schreibt eine Zusammenfassung.

🔹 4. LLM-Tutor mit Sicherem System-Prompt
📌 Ziel

    Teilnehmer können Fragen stellen, aber keine fertigen Lösungen erhalten.
    LLM erkennt Eigenleistung vs. Copy-Paste und passt die Antworten an.

📌 Umsetzung

    System-Prompt:
    „Du bist ein Tutor für C-Programmierung. Erkläre, stelle Fragen, aber verrate niemals fertige Lösungen. Falls der Teilnehmer seinen Code kopiert hat, gib ihm gezielte Hinweise zum Debuggen.“
    LLM antwortet nur, wenn eigenständige Eingaben nachgewiesen wurden.
    Falls zu oft gefragt wird, ohne Änderungen → LLM gibt keine Antwort.

🔹 5. C-Code-Ausführung in der App
📌 Ziel

    Code soll in der App kompiliert und ausgeführt werden.
    Ergebnis soll angezeigt werden.
    Sicherheit: Kein schädlicher Code (rm -rf / usw.).

📌 Umsetzung

    Code wird in solution.c gespeichert
    Kompilierung mit gcc

    gcc solution.c -o solution

    Ausführung in einer sicheren Umgebung (Docker oder chroot)
    Timeout nach 3 Sekunden, falls Endlosschleife

🔹 6. Copy-Paste-Erkennung & Adaptive Fehler-Einfügung
📌 Ziel

    Erkennen, wenn ein User Copy-Paste verwendet.
    Falls Copy-Paste zu stark ist, baut das LLM gezielt Fehler in den Code ein.
    Teilnehmer muss die Fehler selbst entdecken und korrigieren.

📌 Umsetzung

    Copy-Paste-Detektion:
        git diff zeigt an, ob eine komplette Datei eingefügt wurde.
        Falls der erste Commit über 80 % des Codes enthält, wird das erkannt.
    LLM-generierte Fehler:
        Falls Copy-Paste zu hoch → LLM erstellt subtile Fehler.
        Typische Fehler: Syntaxfehler, falsche Variablen, Speicherzugriffsfehler.
    User bekommt eine Meldung:
        „Dein Code wurde automatisch angepasst. Finde die Fehler und behebe sie.“

🔹 7. Git-Analyse & Berichterstellung
📌 Ziel

    ? Git-Graph als Zeitstrahl mit Diffs & Notizen.
    Bewertung des Lernfortschritts durch LLM.
    PDF-Bericht mit Passwortschutz speichern.

📌 Umsetzung

    ? Graph mit matplotlib generieren.
    LLM-gestützte Code-Analyse:
        Wie viel wurde selbst geschrieben?
        War Copy-Paste dabei?
        Qualität der Änderungen?
    Bericht speichern als passwortgeschütztes PDF (reportlab, cryptography).

🔹 8. UI/UX: Gradio-App mit Tabs

Aufbau der App:

    Tab 1: Code-Editor + Aufgabenstellung
    Tab 2: Tutor-Chat
    Tab 3: Git-Analyse & Fortschritt (Graph)
    Tab 4: Bericht-Download
