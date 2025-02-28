import os
import json
import gradio as gr
import openai
import git
import time
import threading
import difflib
from pathlib import Path
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus einer .env-Datei
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def setup_directories():
    """Erstellt die nötige Verzeichnisstruktur für Benutzerlösungen und Berichte, falls sie noch nicht existieren."""
    base_dirs = ["user_codes"]
    for directory in base_dirs:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("Benutzerverzeichnisse wurden überprüft/erstellt.")

def generate_pseudonym():
    """Generiert und speichert ein persistentes Pseudonym für den User."""
    pseudonym_file = "user_pseudonym.json"
    if Path(pseudonym_file).exists():
        with open(pseudonym_file, "r") as f:
            return json.load(f)["pseudonym"]
    
    import random, string
    pseudonym = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    with open(pseudonym_file, "w") as f:
        json.dump({"pseudonym": pseudonym}, f)
    return pseudonym

def setup_git_repo(user_id):
    """Initialisiert ein Git-Repository für einen User, falls nicht vorhanden."""
    user_dir = Path(f"user_codes/{user_id}")
    user_dir.mkdir(parents=True, exist_ok=True)  # Sicherstellen, dass das Verzeichnis existiert
    repo_path = user_dir / ".git"
    if not repo_path.exists():
        repo = git.Repo.init(user_dir)
        repo.config_writer().set_value("user", "name", "AutoCommit").release()
        repo.config_writer().set_value("user", "email", "autocommit@localhost").release()

def detect_copy_paste(old_code, new_code):
    """Vergleicht alten und neuen Code und erkennt plötzliche große Einfügungen."""
    d = difflib.Differ()
    diff = list(d.compare(old_code.splitlines(), new_code.splitlines()))
    added_lines = sum(1 for line in diff if line.startswith('+ '))
    return added_lines > 5  # Schwellwert für Copy-Paste-Erkennung

def save_code(user_id, new_code, old_code):
    """Speichert den Code und erstellt einen Git-Commit, falls Änderungen vorhanden sind."""
    user_dir = Path(f"user_codes/{user_id}")
    file_path = user_dir / "solution.c"
    user_dir.mkdir(parents=True, exist_ok=True)
    
    if detect_copy_paste(old_code, new_code):
        print("⚠️ Copy-Paste erkannt! Tutor wird informiert.")
        with open(user_dir / "copy_paste_log.txt", "a") as log_file:
            log_file.write(f"Copy-Paste erkannt am {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        return  # Keine Speicherung, stattdessen Warnung oder Fehlereinfügung durch LLM
    
    with open(file_path, "w") as f:
        f.write(new_code)
    
    repo = git.Repo(user_dir)
    repo.git.add("solution.c")
    if repo.is_dirty():  # Nur committen, wenn Änderungen vorhanden sind
        repo.index.commit("Auto-Commit")
        print("commit done")

def modify_code_with_llm(code):
    """Verändert den Code mittels OpenAI, um subtile Fehler einzufügen."""
    SYSTEM_PROMPT = """
    Du bist ein C-Programmierungstutor. Falls Copy-Paste erkannt wird, füge kleine, realistische Fehler ein, die den Lernprozess unterstützen. Ziel ist es, dass der Lernende wieder zum Bug-Fixer wird. SEHR WICHTIG IST, DASS DU DIE STRUKTUR DES URSPRÜNGLICHEN CODES MÖGLICHST BEIBEHÄLTST UND DIE FEHLER SUBTIL ABER SCHON ANSPRUCHSVOLL SIND. GIB NUR DEN CODE OHNE IRGENDETWAS ANDERES ZURÜCK. LASS KOMMENTARE DEINERSEITS UNBEDINGT WEG! Erkläre nichts und vor allem nicht die von dir eingebauten Fehler!
    """
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Originalcode:\n{code}\nBitte leicht modifizieren und Fehler einfügen."}
        ]
    )
    print(response.choices[0].message.content.strip().replace("```c", "").replace("```", "").strip())
    return response.choices[0].message.content.strip().replace("```c", "").replace("```", "").strip()

def list_tasks():
    """Listet alle verfügbaren Aufgaben im /tasks Verzeichnis auf."""
    tasks_path = Path("tasks")
    if not tasks_path.exists():
        tasks_path.mkdir()
    tasks = [file.stem for file in tasks_path.glob("*.tex")]
    return tasks

def get_task_content(task_name):
    """Lädt den Inhalt der .tex Datei einer Aufgabe."""
    task_path = Path(f"tasks/{task_name}.tex")
    if task_path.exists():
        with open(task_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Keine Aufgabenbeschreibung gefunden."

def tutor_response(user_input, history=[]):
    """Kommuniziert mit OpenAI GPT-4o-mini unter striktem Tutor-Filter."""
    SYSTEM_PROMPT = """
    Du bist ein Tutor für C-Programmierung. Deine Aufgabe ist es, den Teilnehmern zu helfen, aber niemals vollständige Lösungen bereitzustellen. Stattdessen gibst du motivierende Hinweise, stellst Fragen zum besseren Verständnis und leitest den Teilnehmer Schritt für Schritt in die richtige Richtung. Niemals soll Code ausgegeben werden! Fordere zur Reflexion auf und unterstütze mit Erklärungen.
    """
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *[{"role": "user", "content": msg["content"]} for msg in history],
            {"role": "user", "content": user_input}
        ]
    )
    return response.choices[0].message.content.strip()

def gradio_ui():
    """Erstellt die Gradio-Oberfläche mit Copy-Paste-Erkennung und LLM-Modifikation."""
    tasks = list_tasks()
    default_task = tasks[0] if tasks else ""
    default_task_content = get_task_content(default_task) if default_task else "Keine Aufgaben verfügbar."
    user_id = generate_pseudonym()
    setup_git_repo(user_id)
    
    def on_code_change(new_code):
        """Wird ausgelöst, wenn der Nutzer den Code ändert."""
        old_code = Path(f"user_codes/{user_id}/solution.c").read_text() if Path(f"user_codes/{user_id}/solution.c").exists() else ""
        if detect_copy_paste(old_code, new_code):
            new_code = modify_code_with_llm(new_code)
            print("⚠️ Code wurde verändert! Bitte Fehler finden und korrigieren.")
        save_code(user_id, new_code, old_code)
        return new_code
    
    with gr.Blocks() as app:
        with gr.Row():
            with gr.Column(scale=1):
                selected_task = gr.Dropdown(label="Aufgabe auswählen", choices=tasks, value=default_task)
            with gr.Column(scale=3):
                task_display = gr.Textbox(label="Aufgabenbeschreibung", lines=10, value=default_task_content)
                code_input = gr.Textbox(label="Code-Editor", lines=15)
                test_button = gr.Button("Test-Code ausführen")
                output_display = gr.Textbox(label="Terminal-Ausgabe", lines=10)
            with gr.Column(scale=1):
                chat_interface = gr.ChatInterface(fn=tutor_response, type='messages')

        def update_task_content(task_name):
            return get_task_content(task_name)

        selected_task.change(update_task_content, inputs=[selected_task], outputs=[task_display])
        code_input.input(on_code_change, inputs=[code_input], outputs=[code_input])
    
        app.launch()

# Setup aufrufen
setup_directories()
pseudonym = generate_pseudonym()
print(f"Benutzerpseudonym: {pseudonym}")

# Starte UI
gradio_ui()
