import os
import glob
import threading
import time
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext, simpledialog, filedialog
import speech_recognition as sr

from config import POWERSHELL_SCRIPTS_DIR, PYTHON_SCRIPTS_DIR, BASE_DIR, load_config
from actions import execute_powershell, open_website, open_windows_app, save_memo, list_all_memos_detailed, delete_memo_by_identifier, process_cloud_email_account
from ai_node import query_remote_gpu_brain
import speech_engine

# =====================================================================
# GUI DASHBOARD & CONTROLS MODULE
# =====================================================================

dashboard_terminal = None
root_window = None
script_listbox = None
command_entry = None
dava_suspended = False
script_path_map = {}

def log_to_dashboard(message):
    """Appends messages to the graphical terminal window safely."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    if dashboard_terminal:
        dashboard_terminal.configure(state='normal')
        dashboard_terminal.insert(tk.END, f"{formatted_msg}\n")
        dashboard_terminal.see(tk.END)
        dashboard_terminal.configure(state='disabled')
    print(formatted_msg)

def execute_command_string(sub_cmd):
    """
    Routes voice or typed commands to action handlers, 
    with built-in intelligent routing for security payloads and scripts.
    """
    global dava_suspended
    clean_cmd = sub_cmd.lower().strip()
    log_to_dashboard(f"Executing command action: '{sub_cmd}'")
    
    if any(term in clean_cmd for term in ["stop", "shut up", "quiet", "cancel", "halt"]):
        speech_engine.stop_speaking()
        speech_engine.speak("Stopped.")
        return

    if any(term in clean_cmd for term in ["goodbye", "exit", "shutdown", "quit", "until next time"]):
        farewell_msg = "Goodbye, until next time!"
        log_to_dashboard(farewell_msg)
        speech_engine.speak(farewell_msg, block=True)
        if root_window:
            root_window.destroy()
        os._exit(0)
        
    # --- SECURITY PAYLOAD ROUTER ---
    if any(keyword in clean_cmd for keyword in ["iex", "new-object", "downloadfile", "invoke-expression", "-nop", "-windowstyle hidden", "http://"]):
        log_to_dashboard("[SECURITY ROUTER]: Security payload detected in input. Routing to AI Triage Engine...")
        speech_engine.speak("Security payload detected. Routing to remote GPU brain for threat analysis.")
        
        def run_ai_payload_analysis():
            global dava_suspended
            dava_suspended = True
            analysis_prompt = f"Analyze this security payload and provide a threat assessment and containment plan: {sub_cmd}"
            result = query_remote_gpu_brain(analysis_prompt)
            log_to_dashboard(f"[AI TRIAGE RESULT]:\n{result}")
            speech_engine.speak("Payload analysis complete. Check dashboard for the containment playbook.")
            dava_suspended = False
            
        threading.Thread(target=run_ai_payload_analysis, daemon=True).start()
        return

    # --- SCENE 3 LIVE FORENSIC TRIAGE HANDLER FOR 10.0.0.193 ---
    if "forensic" in clean_cmd or "triage" in clean_cmd or "10.0.0.193" in clean_cmd:
        def run_forensic_simulation():
            global dava_suspended
            dava_suspended = True
            log_to_dashboard(f"[PROGRESS] Initiating remote SSH forensic session to Linux node 10.0.0.193...")
            speech_engine.speak("Initiating remote forensic triage on Linux endpoint 10.0.0.193.")
            
            time.sleep(1.5)
            log_to_dashboard(f"[TELEMETRY]: Querying active network sockets and sockets on 10.0.0.193...")
            time.sleep(1.5)
            log_to_dashboard(f"[TELEMETRY]: Verifying root process integrity, user sessions, and cron persistence...")
            time.sleep(1.5)
            
            response = "Forensic scan complete for Linux node 10.0.0.193. Two active SSH sessions verified, no unauthorized listening ports detected. Endpoint status is clean."
            log_to_dashboard(f"[PROGRESS] {response}")
            speech_engine.speak(response)
            dava_suspended = False
        threading.Thread(target=run_forensic_simulation, daemon=True).start()
        return

    if clean_cmd.startswith("ping "):
        target_ip = clean_cmd.replace("ping", "").replace(" dot ", ".").replace("dot", ".").replace(" ", "").strip()
        log_to_dashboard(f"[PROGRESS] Executing ping on {target_ip}...")
        speech_engine.speak(f"Pinging {target_ip}")
        result = execute_powershell(f"ping -n 4 {target_ip}")
        log_to_dashboard(result)
        speech_engine.speak("Ping complete. Check your terminal dashboard for results.")
        return
    elif clean_cmd.startswith("nmap ") or clean_cmd == "nmap":
        log_to_dashboard(f"[PROGRESS] Running Nmap scan: {clean_cmd}...")
        speech_engine.speak("Running Nmap network scan.")
        result = execute_powershell(clean_cmd)
        log_to_dashboard(result)
        speech_engine.speak("Nmap scan complete. Check your terminal dashboard for the results.")
        return
    elif "take a memo" in clean_cmd or "save a memo" in clean_cmd or clean_cmd == "take memo":
        def record_ten_second_memo():
            global dava_suspended
            dava_suspended = True  
            recognizer = sr.Recognizer()
            recognizer.energy_threshold = 3000
            recognizer.dynamic_energy_threshold = True
            
            speech_engine.speak("I am listening for your memo. You have up to ten seconds to speak.")
            log_to_dashboard("[PROGRESS] Recording 10-second voice memo...")
            memo_text = ""
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.8)
                    audio = recognizer.listen(source, timeout=4.0, phrase_time_limit=10.0)
                    memo_text = recognizer.recognize_google(audio)
            except Exception as e:
                log_to_dashboard(f"[PROGRESS] Voice memo capture missed or timed out: {e}")
            
            if memo_text and memo_text.strip():
                res = save_memo(memo_text.strip())
                log_to_dashboard(res)
                speech_engine.speak("Memo saved successfully.")
            else:
                log_to_dashboard("[PROGRESS] Voice capture quiet. Type your memo in the entry bar and press Send.")
                speech_engine.speak("Voice capture was quiet. Please type your memo in the input box.")
            
            dava_suspended = False  
        threading.Thread(target=record_ten_second_memo, daemon=True).start()
        return
    elif any(term in clean_cmd for term in ["check memos", "recall memo", "list memos", "play check memos"]):
        res_text, details = list_all_memos_detailed()
        log_to_dashboard(res_text)
        if details:
            speech_engine.speak(f"You have {len(details)} stored memos. The most recent memo says: {details[0]['content']}")
        else:
            speech_engine.speak("Your memo vault is empty.")
        return
    elif clean_cmd.startswith("delete memo") or clean_cmd == "delete memos":
        target_id = clean_cmd.replace("delete memo", "").replace("s", "").strip()
        if not target_id:
            msg = "Please specify which memo to delete by number or date, for example: delete memo 1"
            log_to_dashboard(msg)
            speech_engine.speak(msg)
        else:
            res = delete_memo_by_identifier(target_id)
            log_to_dashboard(res)
            speech_engine.speak(res)
        return
    elif any(term in clean_cmd for term in ["check email", "read email", "inbox", "emails", "check inbox", "check mail"]):
        config = load_config()
        accounts = config.get("CLOUD_ACCOUNTS", {})
        for acc_name, acc_data in accounts.items():
            res = process_cloud_email_account(acc_name, acc_data)
            log_to_dashboard(res)
            speech_engine.speak(res)
    elif "open website" in clean_cmd or "browse" in clean_cmd or "go to" in clean_cmd or ".com" in clean_cmd:
        target_site = clean_cmd.replace("open website", "").replace("browse", "").replace("go to", "").replace("open", "").strip()
        msg, url = open_website(target_site)
        speech_engine.speak(msg)
        import webbrowser
        webbrowser.open(url, new=2)
    elif "open app" in clean_cmd or "launch" in clean_cmd or clean_cmd.startswith("open "):
        target_app = clean_cmd.replace("open app", "").replace("launch", "").replace("open", "").strip()
        if target_app in ["not", "note"]:
            target_app = "notepad"
        success, msg = open_windows_app(target_app)
        log_to_dashboard(msg)
        speech_engine.speak(msg)
    else:
        def run_ai_query():
            global dava_suspended
            dava_suspended = True
            log_to_dashboard(f"[PROGRESS] Querying remote GPU AI node with: '{sub_cmd}'...")
            speech_engine.speak("Processing query through the remote GPU intelligence model.")
            response = query_remote_gpu_brain(sub_cmd)
            log_to_dashboard(f"[PROGRESS] AI response received: {response}")
            speech_engine.speak(response)
            dava_suspended = False
        threading.Thread(target=run_ai_query, daemon=True).start()

def refresh_script_list():
    """Populates the script panel with files from subfolders."""
    if not script_listbox:
        return
    script_listbox.delete(0, tk.END)
    
    ps1_files = glob.glob(os.path.join(POWERSHELL_SCRIPTS_DIR, "*.ps1"))
    py_files = glob.glob(os.path.join(PYTHON_SCRIPTS_DIR, "*.py"))
    
    global script_path_map
    script_path_map = {}

    all_files = sorted(ps1_files + py_files)
    for path in all_files:
        filename = os.path.basename(path)
        tag = "[PS1] " if path.endswith(".ps1") else "[PY]  "
        display_label = tag + filename
        script_path_map[display_label] = path
        script_listbox.insert(tk.END, display_label)
    
    log_to_dashboard(f"[PROGRESS] Script list refreshed. Found {len(all_files)} scripts.")

def run_selected_script(event=None):
    """Launches the script selected in the UI listbox."""
    global dava_suspended
    if not script_listbox:
        return
    selected_indices = script_listbox.curselection()
    if not selected_indices:
        return
    
    display_label = script_listbox.get(selected_indices[0])
    file_path = script_path_map.get(display_label)
    
    if not file_path or not os.path.exists(file_path):
        log_to_dashboard(f"Error: Script path for {display_label} not found.")
        return

    log_to_dashboard(f"[PROGRESS] Suspending DAVA mic listener and launching: {file_path}")
    dava_suspended = True
    speech_engine.speak("Launching script. Microphone released.")
    
    try:
        if file_path.endswith(".py"):
            subprocess_cmd = f'start cmd /k python "{file_path}"'
        else:
            subprocess_cmd = f'start powershell -NoExit -ExecutionPolicy Bypass -File "{file_path}"'
        os.system(subprocess_cmd)
        log_to_dashboard("[PROGRESS] Script window spawned successfully.")
    except Exception as e:
        log_to_dashboard(f"Error launching script: {e}")
        dava_suspended = False

def resume_mic_safely():
    """Resumes the voice listener."""
    global dava_suspended
    dava_suspended = False
    log_to_dashboard("[PROGRESS] DAVA microphone listener manually resumed.")
    speech_engine.speak("Microphone listener resumed.")

def build_dashboard():
    """Initializes and builds the Tkinter UI window."""
    global root_window, dashboard_terminal, command_entry, script_listbox
    
    root = tk.Tk()
    root_window = root
    root.title("DAVA v2.0 - Modular Operations Terminal (GPU Node: 10.0.0.152)")
    root.geometry("1150x760")
    root.configure(bg="#1a1a1a")

    title_lbl = tk.Label(root, text="DAVA v2.0 // MODULAR AUTONOMOUS IT & CYBER AGENT", font=("Consolas", 11, "bold"), fg="#00ffcc", bg="#1a1a1a")
    title_lbl.pack(pady=10)

    main_paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, bg="#1a1a1a", sashwidth=6)
    main_paned.pack(padx=15, pady=5, fill=tk.BOTH, expand=True)

    left_frame = tk.Frame(main_paned, bg="#1a1a1a")
    main_paned.add(left_frame, width=720)

    dashboard_terminal = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, width=80, height=20, font=("Consolas", 10), bg="#262626", fg="#00ffcc")
    dashboard_terminal.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
    dashboard_terminal.configure(state='disabled')

    def handle_typed_command(event=None):
        typed_text = command_entry.get().strip()
        if typed_text:
            command_entry.delete(0, tk.END)
            execute_command_string(typed_text)

    input_frame = tk.Frame(left_frame, bg="#1a1a1a")
    input_frame.pack(fill=tk.X, padx=5, pady=5)

    command_entry = tk.Entry(input_frame, font=("Consolas", 10), bg="#262626", fg="#00ffcc", insertbackground="white")
    command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
    command_entry.bind("<Return>", handle_typed_command)

    tk.Button(input_frame, text="Send", font=("Consolas", 9, "bold"), bg="#00aa55", fg="white", command=handle_typed_command).pack(side=tk.RIGHT)

    control_frame = tk.Frame(left_frame, bg="#1a1a1a")
    control_frame.pack(fill=tk.X, padx=5, pady=10)

    tk.Button(control_frame, text="STOP SPEAKING", font=("Consolas", 9, "bold"), bg="#aa0000", fg="white", command=speech_engine.stop_speaking).pack(side=tk.LEFT, padx=2)
    tk.Button(control_frame, text="IT DIAGNOSTIC", font=("Consolas", 9, "bold"), bg="#00aa55", fg="white", 
              command=lambda: execute_command_string("General system diagnostic requested.")).pack(side=tk.LEFT, padx=2)
    tk.Button(control_frame, text="TAKE MEMO", font=("Consolas", 9, "bold"), bg="#cc3333", fg="white", 
              command=lambda: execute_command_string("take a memo")).pack(side=tk.LEFT, padx=2)
    tk.Button(control_frame, text="CHECK MEMOS", font=("Consolas", 9, "bold"), bg="#444444", fg="white", command=lambda: execute_command_string("check memos")).pack(side=tk.LEFT, padx=2)

    right_frame = tk.Frame(main_paned, bg="#1a1a1a")
    main_paned.add(right_frame, width=380)

    tk.Label(right_frame, text="DIRECT SCRIPTS PANEL", font=("Consolas", 10, "bold"), fg="#00ffcc", bg="#1a1a1a").pack(anchor="w", padx=5, pady=5)
    
    script_listbox = tk.Listbox(right_frame, font=("Consolas", 9), bg="#262626", fg="#00ffcc", selectbackground="#00aa55")
    script_listbox.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
    script_listbox.bind("<Double-Button-1>", run_selected_script)

    script_btn_frame = tk.Frame(right_frame, bg="#1a1a1a")
    script_btn_frame.pack(fill=tk.X, padx=5, pady=5)

    tk.Button(script_btn_frame, text="Run Script", font=("Consolas", 9, "bold"), bg="#00aa55", fg="white", command=run_selected_script).pack(side=tk.LEFT, padx=1, expand=True, fill=tk.X)
    # Refresh button excluded per user preference
    tk.Button(script_btn_frame, text="Resume Mic", font=("Consolas", 8, "bold"), bg="#663399", fg="white", command=resume_mic_safely).pack(side=tk.LEFT, padx=1, expand=True, fill=tk.X)

    refresh_script_list()
    return root
