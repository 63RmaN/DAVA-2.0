Actions.py

import os
import glob
import subprocess
import webbrowser
import smtplib
import imaplib
import email
import base64
from datetime import datetime
from config import BASE_DIR, MEMO_DIR, load_config

# =====================================================================
# LOCAL SYSTEM ACTIONS & ROUTING MODULE
# =====================================================================

SITE_ALIASES = {
    "miter": "mitre.org", "mitre": "mitre.org", "you tube": "youtube.com", 
    "git hub": "github.com", "linked in": "linkedin.com", 
    "stack overflow": "stackoverflow.com", "google": "google.com"
}

def execute_powershell(command):
    """Executes a system or PowerShell command string directly via the shell."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120,
            encoding='utf-8',
            errors='ignore'
        )
        return result.stdout.strip() if result.stdout.strip() else result.stderr.strip()
    except Exception as e:
        return f"Error executing command: {e}"
def open_website(target):
    """Opens a website or matched alias in the default browser."""
    clean_target = target.lower().strip()
    for alias, domain in SITE_ALIASES.items():
        if alias in clean_target:
            clean_target = domain
            break
    if "." not in clean_target:
        clean_target += ".com"
    url = f"https://{clean_target}" if not clean_target.startswith("http") else clean_target
    return f"Opening {target}", url

def open_windows_app(app_name):
    """Maps and launches Windows desktop applications and control panels robustly using Windows start."""
    clean_app = app_name.lower().strip()
    
    app_mappings = {
        "notepad": "notepad", "not": "notepad", "note": "notepad",
        "calc": "calc", "calculator": "calc",
        "cmd": "cmd", "cm": "cmd",
        "powershell": "powershell", "power": "powershell", "powers": "powershell",
        "task manager": "taskmgr", "taskmgr": "taskmgr",
        "control panel": "control", "control pan": "control", "control": "control",
        "firewall": "wf.msc", "windows defender fire": "wf.msc", "defender firewall": "wf.msc",
        "regedit": "regedit",
        "region": "control international", 
        "sync center": "mobsync",
        "recovery": "rstrui", 
        "windows defender": "windowsdefender:",
        "user accounts": "netplwiz", "use your account": "netplwiz",
        "system": "sysdm.cpl",
        "credential man": "credwiz", "credential manager": "credwiz",
        "device": "devmgmt.msc", "device manager": "devmgmt.msc",
        "explorer": "explorer", "file explorer": "explorer",
        "power opt": "powercfg.cpl", "power options": "powercfg.cpl",
        "windows tool": "control admintools", "windows tools": "control admintools",
        "date and time": "timedate.cpl",
        "programs and features": "appwiz.cpl",
        "word": "winword", "microsoft word": "winword",
        "excel": "excel", "microsoft excel": "excel",
        "powerpoint": "powerpnt", "microsoft powerpoint": "powerpnt",
        "outlook": "outlook", "microsoft outlook": "outlook",
        "chrome": "chrome", "google chrome": "chrome",
        "adobe": "acrobat", "adobe acrobat": "acrobat", "bobby acrobat": "acrobat",
        "wireshark": "wireshark", "wire": "wireshark",
        "nmap": "nmap"
    }
    
    target_exec = app_mappings.get(clean_app)
    if not target_exec:
        for key, val in app_mappings.items():
            if key in clean_app:
                target_exec = val
                break
                
    if not target_exec:
        target_exec = clean_app

    try:
        subprocess.Popen(f'start "" {target_exec}', shell=True)
        return True, f"Successfully launched {app_name}"
    except Exception as e:
        return False, f"Failed to launch app {app_name}: {e}"

def save_memo(memo_text):
    """Saves a text memo to the memos folder with a precise timestamp."""
    if not memo_text:
        return "Memo content was empty."
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(MEMO_DIR, f"memo_{timestamp_str}.txt")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(memo_text)
        return f"Memo saved successfully [{timestamp_str}]: {memo_text[:50]}..."
    except Exception as e:
        return f"Failed to save memo: {e}"

def list_all_memos_detailed():
    """Retrieves all memos sorted by date with index numbers and timestamps."""
    try:
        memo_files = sorted(glob.glob(os.path.join(MEMO_DIR, "*.txt")), key=os.path.getmtime, reverse=True)
        if not memo_files:
            return "Your memo vault is empty.", []
        
        memo_details = []
        response_lines = [f"You have {len(memo_files)} stored memos:"]
        
        for idx, filepath in enumerate(memo_files, 1):
            filename = os.path.basename(filepath)
            timestamp_part = filename.replace("memo_", "").replace(".txt", "")
            try:
                dt = datetime.strptime(timestamp_part, "%Y%m%d_%H%M%S")
                date_str = dt.strftime("%B %d, %Y at %H:%M:%S")
            except Exception:
                date_str = timestamp_part
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().strip()
            
            memo_details.append({"index": idx, "filepath": filepath, "date": date_str, "content": content})
            response_lines.append(f"[{idx}] Date: {date_str} -> {content[:60]}...")
            
        return "\n".join(response_lines), memo_details
    except Exception as e:
        return f"Error scanning memos: {e}", []

def delete_memo_by_identifier(identifier):
    """Deletes a memo by its index number or date/content snippet."""
    memo_files = sorted(glob.glob(os.path.join(MEMO_DIR, "*.txt")), key=os.path.getmtime, reverse=True)
    if not memo_files:
        return "No memos found to delete."
    
    target_file = None
    clean_id = str(identifier).lower().strip()
    
    if clean_id.isdigit():
        idx = int(clean_id)
        if 1 <= idx <= len(memo_files):
            target_file = memo_files[idx - 1]
    else:
        for filepath in memo_files:
            filename = os.path.basename(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read().lower()
            if clean_id in filename.lower() or clean_id in content:
                target_file = filepath
                break
                
    if target_file and os.path.exists(target_file):
        try:
            os.remove(target_file)
            return f"Successfully deleted memo: {os.path.basename(target_file)}"
        except Exception as e:
            return f"Failed to delete memo file: {e}"
            
    return f"Could not find a memo matching '{identifier}'. Please check the number or date."

def process_cloud_email_account(account_name, account_config):
    """Connects via IMAP to check unread emails."""
    try:
        mail = imaplib.IMAP4_SSL(account_config["imap"])
        mail.login(account_config["email"], account_config["password"])
        mail.select("inbox")

        status, unread_messages = mail.search(None, "UNSEEN")
        if status != "OK":
            mail.logout()
            return f"Could not search {account_name} inbox."

        unread_ids = unread_messages[0].split()
        unread_count = len(unread_ids)
        mail.logout()
        
        return f"Account {account_name}: {unread_count} new unread emails found."
    except Exception as e:
        return f"Failed to connect to your {account_name} account: {e}"

# =====================================================================
# NEW: Live Web Search Integration (Appended safely without breaking anything)
# =====================================================================
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
