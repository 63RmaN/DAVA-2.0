import os
import platform
import threading
import time
import tempfile
import winsound
import subprocess
import speech_recognition as sr
import gui

# =====================================================================
# STABLE KOKORO-ONLY SPEECH ENGINE MODULE (ABSOLUTE DAVID ELIMINATION)
# =====================================================================

if platform.system() == "Windows":
    espeak_candidates = [
        r"C:\Program Files\eSpeak NG\libespeak-ng.dll",
        r"C:\Program Files (x86)\eSpeak NG\libespeak-ng.dll",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\eSpeak NG\libespeak-ng.dll")
    ]
    for dll_path in espeak_candidates:
        if os.path.exists(dll_path):
            os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = dll_path
            break

kokoro_pipeline = None

try:
    from pykokoro import build_pipeline, PipelineConfig, GenerationConfig
    kokoro_pipeline = build_pipeline(
        config=PipelineConfig(generation=GenerationConfig(lang="en-us"), voice="af_heart")
    )
    print("[Speech Engine]: Kokoro neural TTS pipeline built successfully.")
except Exception as e:
    print(f"[Speech Engine Warning]: Kokoro build failed: {e}. Will attempt inline generation if needed.")

speech_lock = threading.Lock()

def speak(text, block=False):
    """Speaks text exclusively using Kokoro. Hard-terminates any stray audio channels first."""
    def run_speech():
        with speech_lock:
            try:
                # Absolute audio channel reset
                winsound.PlaySound(None, 0)
                if platform.system() == "Windows":
                    subprocess.run(["taskkill", "/f", "/im", "SpeechUXWiz.exe"], capture_output=True)
                
                if kokoro_pipeline:
                    result = kokoro_pipeline.run(text, lang="en-us")
                    fd, temp_path = tempfile.mkstemp(suffix=".wav")
                    os.close(fd)
                    result.save_wav(temp_path)
                    
                    if block:
                        winsound.PlaySound(temp_path, winsound.SND_FILENAME)
                    else:
                        winsound.PlaySound(temp_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                else:
                    # Fallback inline Kokoro generation
                    try:
                        from pykokoro import build_pipeline, PipelineConfig, GenerationConfig
                        temp_pipeline = build_pipeline(
                            config=PipelineConfig(generation=GenerationConfig(lang="en-us"), voice="af_heart")
                        )
                        result = temp_pipeline.run(text, lang="en-us")
                        fd, temp_path = tempfile.mkstemp(suffix=".wav")
                        os.close(fd)
                        result.save_wav(temp_path)
                        
                        if block:
                            winsound.PlaySound(temp_path, winsound.SND_FILENAME)
                        else:
                            winsound.PlaySound(temp_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                    except Exception as kokoro_err:
                        gui.log_to_dashboard(f"[Speech Text (Kokoro Failed): {text}] (Error: {kokoro_err})")
            except Exception as err:
                gui.log_to_dashboard(f"[Speech Generation Error]: {err}")
                
    if block:
        run_speech()
    else:
        threading.Thread(target=run_speech, daemon=True).start()

def stop_speaking():
    """Immediately halts all audio output and clears sound buffers."""
    try:
        winsound.PlaySound(None, 0)
        if platform.system() == "Windows":
            subprocess.run(["taskkill", "/f", "/im", "SpeechUXWiz.exe"], capture_output=True)
    except Exception:
        pass

def start_voice_listener():
    """Continuously listens for voice commands in the background unless suspended, ignoring background chatter."""
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 3000
    recognizer.dynamic_energy_threshold = True

    def listen_loop():
        time.sleep(2)  
        gui.log_to_dashboard("Voice listener active. Say 'Computer' followed by your command.")
        
        while True:
            if gui.dava_suspended:
                time.sleep(0.5)
                continue

            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, timeout=3.0, phrase_time_limit=8.0)
                
                command = recognizer.recognize_google(audio).lower().strip()
                gui.log_to_dashboard(f"[MIC HEARD]: '{command}'")
                
                if not command or gui.dava_suspended:
                    continue

                if "computer" in command:
                    clean_cmd = command.replace("computer", "").strip()
                    if clean_cmd:
                        gui.execute_command_string(clean_cmd)
                    else:
                        gui.log_to_dashboard("[FILTERED] Wake word heard, but no command followed.")
                else:
                    gui.log_to_dashboard("[FILTERED] Background speech ignored (missing wake word 'computer').")
                    continue
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except Exception:
                time.sleep(1.0)

    listener_thread = threading.Thread(target=listen_loop, daemon=True)
    listener_thread.start()
