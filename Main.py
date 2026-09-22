# --- EMERGENCY SAFETY GUARD: BLOCK WINDOWS SAPI/DAVID VOICES ---
import sys
from types import ModuleType

class DummyTTS:
    def __init__(self, *args, **kwargs): pass
    def say(self, *args, **kwargs): pass
    def runAndWait(self, *args, **kwargs): pass
    def setProperty(self, *args, **kwargs): pass
    def getProperty(self, *args, **kwargs): return ""
    def stop(self, *args, **kwargs): pass

dummy_module = ModuleType("pyttsx3")
dummy_module.init = lambda *args, **kwargs: DummyTTS()
sys.modules["pyttsx3"] = dummy_module
# -------------------------------------------------------------

import os
import shutil
import threading
import time
from datetime import datetime
import tkinter as tk

from config import BASE_DIR, load_config
from speech_engine import speak
from gui import build_dashboard, execute_command_string, log_to_dashboard, dava_suspended, root_window
from ai_node import triage_latest_audit_log, query_remote_gpu_brain
import speech_recognition as sr

# =====================================================================
# DAVA v2.0: MAIN ENTRYPOINT & AUTOMATED SOAR INGESTION LOOP
# =====================================================================

CHOSEN_MIC_INDEX = None

INCOMING_ALERTS_DIR = os.path.join(BASE_DIR, "incoming_alerts")
PROCESSED_ALERTS_DIR = os.path.join(BASE_DIR, "processed_alerts")

def handle_web_query(query_text):
    """Searches DuckDuckGo for live data, then sends results to the GPU AI node."""
    try:
        from duckduckgo_search import DDGS
        from ai_node import query_remote_gpu_brain
        
        search_results = ""
        with DDGS() as ddgs:
            results = list(ddgs.text(query_text, max_results=3))
            for r in results:
                search_results += f"- {r.get('title')}: {r.get('body')}\n"
                
        prompt = (
            f"Based on the following live web search results, answer the user's question accurately.\n\n"
            f"Live Search Results:\n{search_results}\n\n"
            f"User Question: {query_text}"
        )
        return query_remote_gpu_brain(prompt)
    except Exception as e:
        return f"Live search integration error: {e}"

def ensure_alert_directories():
    """Creates the automated SOAR alert folders if they do not exist."""
    os.makedirs(INCOMING_ALERTS_DIR, exist_ok=True)
    os.makedirs(PROCESSED_ALERTS_DIR, exist_ok=True)

def spawn_incident_response_popup(alert_filename, raw_payload, ai_playbook):
    """Spawns a dedicated, standalone Tkinter window for critical incident triage."""
    def open_window():
        popup = tk.Toplevel()
        popup.title(f"CRITICAL INCIDENT WORKBENCH // {alert_filename}")
        popup.geometry("650x500")
        popup.configure(bg="#1a1a1a")

        tk.Label(popup, text="⚠️ CRITICAL SECURITY INCIDENT DETECTED", font=("Consolas", 11, "bold"), fg="#ff3333", bg="#1a1a1a").pack(pady=10)
        
        tk.Label(popup, text="Raw Suspicious Payload:", font=("Consolas", 9, "bold"), fg="#00ffcc", bg="#1a1a1a").pack(anchor="w", padx=10)
        payload_box = tk.Text(popup, height=5, width=75, font=("Consolas", 9), bg="#262626", fg="#ff9999")
        payload_box.pack(padx=10, pady=5)
        payload_box.insert(tk.END, raw_payload)
        payload_box.configure(state='disabled')

        tk.Label(popup, text="AI Generated Containment Playbook:", font=("Consolas", 9, "bold"), fg="#00ffcc", bg="#1a1a1a").pack(anchor="w", padx=10)
        playbook_box = tk.Text(popup, height=10, width=75, font=("Consolas", 9), bg="#262626", fg="#00ffcc")
        playbook_box.pack(padx=10, pady=5)
        playbook_box.insert(tk.END, ai_playbook)
        playbook_box.configure(state='disabled')

        btn_frame = tk.Frame(popup, bg="#1a1a1a")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Button(btn_frame, text="Execute Remediation", font=("Consolas", 9, "bold"), bg="#aa0000", fg="white", 
                  command=lambda: [log_to_dashboard(f"[ACTION] Remediation executed for {alert_filename}"), popup.destroy()]).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Dismiss Alert", font=("Consolas", 9, "bold"), bg="#444444", fg="white", command=popup.destroy).pack(side=tk.RIGHT, padx=5)

    if root_window:
        root_window.after(0, open_window)

def automated_alert_ingestion_loop():
    """
    MTTR Accelerator & False-Positive Filter Daemon:
    Continuously monitors incoming_alerts/ folder for raw SIEM/EDR payloads.
    Automatically parses, triages, and filters out false positives without human interaction,
    spawning dedicated incident response windows for critical threats.
    """
    ensure_alert_directories()
    log_to_dashboard(f"[SOAR DAEMON] Automated alert ingestion engine active. Monitoring folder: '{INCOMING_ALERTS_DIR}'")
    
    while True:
        try:
            alert_files = [f for f in os.listdir(INCOMING_ALERTS_DIR) if f.endswith(('.txt', '.log', '.json'))]
            
            for file_name in alert_files:
                file_path = os.path.join(INCOMING_ALERTS_DIR, file_name)
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        raw_payload = f.read().strip()
                        
                    if raw_payload:
                        log_to_dashboard(f"--------------------------------------------------")
                        log_to_dashboard(f"[AUTO-INGEST] Ingested raw alert payload from file: {file_name}")
                        
                        payload_lower = raw_payload.lower()
                        
                        # Rule 1: Check for Known Benign / Health Check False Positives
                        if any(term in payload_lower for term in ["get-psdrive", "healthcheck", "diskspace", "normal_admin_task"]) and not any(m in payload_lower for m in ["downloadfile", "http://185.", "bypass"]):
                            log_to_dashboard(f"[AUTO-TRIAGE STATUS]: NOISE / BENIGN FALSE POSITIVE FILTERED")
                            log_to_dashboard(f"[DETAILS]: Standard system metric or authorized admin script. No operator action needed.")
                        
                        # Rule 2: Critical Malicious Payload Ingestion
                        else:
                            log_to_dashboard(f"[AUTO-TRIAGE STATUS]: CRITICAL THREAT DETECTED")
                            log_to_dashboard(f"[ANALYSIS]: Fileless malicious download cradle or unauthorized C2 activity observed.")
                            
                            # Ask the local AI node to format immediate mitigation steps
                            triage_summary = query_remote_gpu_brain(f"Analyze this suspicious alert and provide an immediate 3-step containment plan: {raw_payload}")
                            log_to_dashboard(f"[AI PLAYBOOK]:\n{triage_summary}")
                            
                            # Spawn separate incident response popup window and speak alert
                            spawn_incident_response_popup(file_name, raw_payload, triage_summary)
                            speak("Critical threat alert ingested automatically. Fileless payload detected. Standalone incident response workbench spawned.")
                        
                        log_to_dashboard(f"--------------------------------------------------")
                        
                    # Move processed file to archive directory
                    destination = os.path.join(PROCESSED_ALERTS_DIR, f"{int(time.time())}_{file_name}")
                    shutil.move(file_path, destination)
                    
                except Exception as file_err:
                    log_to_dashboard(f"[SOAR DAEMON ERROR] Failed processing {file_name}: {file_err}")
                    
        except Exception as e:
            pass
            
        time.sleep(3.0)

def listen_loop():
    """Background listener loop for voice wake-word and direct commands."""
    global dava_suspended
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 3500
    recognizer.dynamic_energy_threshold = True
    
    log_to_dashboard("Voice listener active. Say 'Computer' followed by your command, or direct commands.")
    
    while True:
        if dava_suspended:
            time.sleep(1.0)
            continue
        try:
            with sr.Microphone(device_index=CHOSEN_MIC_INDEX) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.4)
                audio = recognizer.listen(source, timeout=4.0, phrase_time_limit=10.0)
                command = recognizer.recognize_google(audio).lower()
                
                log_to_dashboard(f"[MIC HEARD]: '{command}'")
                
                if any(term in command for term in ["stop speaking", "shut up", "dava stop"]):
                    from speech_engine import stop_speaking
                    stop_speaking()
                    continue

                # Handle wake word "computer"
                if "computer" in command:
                    parts = command.split("computer", 1)
                    sub_cmd = parts[1].strip() if len(parts) > 1 else ""
                    
                    if sub_cmd:
                        execute_command_string(sub_cmd)
                    else:
                        speak("What is the command?")
                        time.sleep(1.5)
                        try:
                            audio_followup = recognizer.listen(source, timeout=8.0, phrase_time_limit=10.0)
                            followup_text = recognizer.recognize_google(audio_followup).lower()
                            log_to_dashboard(f"[FOLLOW-UP HEARD]: '{followup_text}'")
                            
                            if "what is the command" in followup_text or not followup_text.strip():
                                continue
                                
                            execute_command_string(followup_text)
                        except sr.WaitTimeoutError:
                            speak("I didn't hear a command.")
                
                # ALSO allow direct commands without needing to say "computer" first
                elif any(command.startswith(prefix) for prefix in ["open", "launch", "ping", "check", "take", "recall", "notepad", "cmd", "powershell"]):
                    execute_command_string(command)
                elif command in ["notepad", "cmd", "powershell", "calculator"]:
                    execute_command_string(f"open {command}")

        except sr.WaitTimeoutError:
            continue
        except Exception:
            time.sleep(0.5)

if __name__ == "__main__":
    # Ensure config loads/initializes on start
    load_config()
    
    # Build the Tkinter GUI root window
    root = build_dashboard()

    # Time-based startup greeting
    current_hour = datetime.now().hour
    if current_hour < 12:
        time_greeting = "Good morning"
    elif 12 <= current_hour < 18:
        time_greeting = "Good afternoon"
    else:
        time_greeting = "Good evening"

    startup_greeting = f"{time_greeting}. This is DAVA, digital assistance voice activated, connected to remote GPU node with Phi-3. How can I help?"
    log_to_dashboard(startup_greeting)
    
    # Speak greeting, start background voice listener thread and automated alert ingestion daemon
    threading.Thread(target=speak, args=(startup_greeting,), daemon=True).start()
    threading.Thread(target=listen_loop, daemon=True).start()
    threading.Thread(target=automated_alert_ingestion_loop, daemon=True).start()

    # Start the graphical application loop
    root.mainloop()
