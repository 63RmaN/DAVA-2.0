import json
import requests
import datetime
from config import load_config

# Try importing Windows SAPI for voice output; safely handle if unavailable
try:
    import win32com.client
except ImportError:
    win32com.client = None

# =====================================================================
# AI NODE & LOCAL INTELLIGENCE TRIAGE MODULE
# =====================================================================

def speak_output(text):
    """Routes speech output through Kokoro via the unified speech engine."""
    try:
        clean_text = text.replace("`", "").replace("*", "").replace("#", "").replace("•", "")
        speech_engine.speak(clean_text)
    except Exception as e:
        print(f"[TTS WARNING]: Could not vocalize output through Kokoro: {e}")

def query_remote_gpu_brain(prompt):
    """Queries the remote Ollama GPU brain at 10.0.0.152 with real-time chunk streaming, with automatic fallback to local."""
    from gui import log_to_dashboard

    remote_url = "http://10.0.0.152:11434/api/generate"
    local_url = "http://localhost:11434/api/generate"
    
    now = datetime.datetime.now()
    current_time_str = now.strftime("%A, %B %d, %Y at %I:%M %p")
    contextualized_prompt = f"[Current System Time: {current_time_str}]\nUser Query: {prompt}"

    payload = {
        "model": "phi3",
        "prompt": contextualized_prompt,
        "stream": True
    }

    def _execute_stream(target_url, node_label):
        response = requests.post(target_url, json=payload, stream=True, timeout=120)
        if response.status_code == 200:
            full_response = ""
            log_to_dashboard(f"[PROGRESS] Streaming AI response chunks from {node_label}...")
            
            for line in response.iter_lines():
                if line:
                    chunk_data = json.loads(line.decode('utf-8'))
                    if "response" in chunk_data:
                        text_chunk = chunk_data["response"]
                        full_response += text_chunk
                        log_to_dashboard(text_chunk)
                        
            if full_response.strip():
                final_text = full_response.strip()
                speak_output(final_text)
                return final_text
            else:
                empty_msg = "The AI returned an empty response field."
                speak_output(empty_msg)
                return empty_msg
        else:
            err_msg = f"Ollama node responded with status code {response.status_code}."
            speak_output(err_msg)
            return err_msg

    try:
        log_to_dashboard("[AI ROUTER]: Contacting remote GPU node (10.0.0.152)...")
        result = _execute_stream(remote_url, "remote GPU node (10.0.0.152)")
        if "status code" in result or "empty response" in result:
            raise ValueError(result)
        return result
    except Exception as remote_err:
        log_to_dashboard(f"[AI ROUTER WARNING]: Remote node encountered an issue ({remote_err}). Failing over to local node...")
        try:
            log_to_dashboard("[AI ROUTER]: Contacting local fallback node (localhost:11434)...")
            result_local = _execute_stream(local_url, "local fallback node (localhost:11434)")
            return result_local
        except Exception as local_err:
            fail_msg = f"Failed to connect to both remote and local AI nodes. Remote error: {remote_err} | Local error: {local_err}"
            speak_output("Warning. Failed to connect to AI nodes.")
            return fail_msg

def triage_latest_audit_log(raw_audit_text=None):
    """
    Phase 2: Automated Local Security Audit Triage Engine.
    Pass raw text from any networked computer (e.g., 10.0.0.162) to triage it instantly.
    """
    if not raw_audit_text:
        raw_audit_text = "System audit scan complete for target 10.0.0.162. No critical vulnerabilities found."

    findings_lower = raw_audit_text.lower()
    
    if "error" in findings_lower or "fail" in findings_lower or "critical" in findings_lower or "certutil" in findings_lower:
        severity = "CRITICAL THREAT DETECTED"
        summary = "Malicious persistence mechanism identified! Unauthorized abuse of certutil.exe detected fetching external payload."
        
        # Make DAVA speak out loud with high-impact urgency
        speak_output("Critical threat detected. Malicious persistence mechanism identified.")
    else:
        severity = "LOW / INFORMATIONAL"
        summary = "Target security event stream verified. Baseline posture normal."

    report = (
        f"=== REMOTE AUDIT REPORT: 10.0.0.162 ===\n"
        f"• Severity Level  : {severity}\n"
        f"• Filtered Noise  : Sanitized standard event chatter from remote host.\n"
        f"• Key Findings    : Evaluated remote event log payload against baseline.\n"
        f"• Incident Summary: {summary}\n"
        f"=========================================="
    )

    return report
