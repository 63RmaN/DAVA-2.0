# DAVA-2.0
Distributed Autonomous Virtual Agent

# DAVA (Distributed Autonomous Virtual Agent)

> **Enterprise-grade, AI-driven endpoint administration and threat triage platform combining local LLM intelligence, cross-platform automation, and robust security guardrails.**

---

## 🚀 Overview
DAVA is an autonomous IT and cybersecurity operations agent engineered to streamline incident response, infrastructure administration, and remote threat triage. Designed around a decentralized multi-node architecture, DAVA bridges a local Windows control interface with dedicated GPU inference nodes and cross-platform Linux endpoints—leveraging real-time neural text-to-speech (TTS) and strict input security guardrails.

---

## 🏗️ System Architecture

```text
+-------------------------------------------------------------+
|               WINDOWS CONTROL DASHBOARD (GUI)               |
|  - Python/Tkinter Modular Console                           |
|  - Speech Recognition & Kokoro Neural TTS Feedback          |
|  - Live Script Runner & Terminal Operations                 |
+------------------------------+------------------------------+
                               |
            +------------------+------------------+
            | (Secure API / SSH)                  | (Encrypted Transport)
            v                                     v
+-----------------------+               +---------------------+
| REMOTE GPU AI NODE    |               | LINUX ENDPOINT      |
| IP: 10.0.0.152        |               | IP: 10.0.0.193      |
| - Local Ollama / LLM  |               | - Live SSH Triage   |
| - Threat Triage Engine|               | - Socket & Process  |
| - Payload Analysis    |               |   Integrity Checks  |
+-----------------------+               +---------------------+
Security & Guardrails

When operating an AI agent capable of executing infrastructure scripts or parsing security payloads, security must be built into the core layer:

    Input Boundary Encasement: Wraps incoming user data and scripts in strict structural boundaries, neutralizing direct prompt injection attempts and system-override commands.

    Command Whitelisting & Routing: Intercepts dangerous execution strings (iex, remote script downloads, etc.) and routes them to the AI triage engine for safe analysis rather than letting local shells execute unverified code blindly.

    Environment Isolation: Separation of control nodes, execution targets, and local credential stores to prevent privilege escalation.

🛠️ Core Features

    Multi-Node Orchestration: Remotely manages local and remote infrastructure across Windows and Linux environments.

    Automated Forensic Triage: Executes live diagnostic sequences on remote endpoints (e.g., checking active sockets, process integrity, and root persistence).

    Voice & Text Operations: Integrated speech-to-text for operational voice commands and Kokoro TTS for text-to-speech situational feedback.

    Modular Operations Terminal: A clean Tkinter-based control panel featuring live telemetry logging and script management.

📂 Project Structure
Plaintext

dava-security-agent/
│
├── main.py              # Application entry point & core loop
├── gui.py               # Tkinter dashboard, command router & terminal
├── ai_node.py           # Interface to local GPU intelligence brain (10.0.0.152)
├── actions.py           # PowerShell/Python system automation & tool wrappers
├── speech_engine.py     # Voice recognition & Kokoro TTS integration
├── config.py            # Environment & path management configuration
├── scripts/             # PowerShell (.ps1) and Python (.py) automation scripts
├── .gitignore           # Excludes caches, logs, and sensitive configurations
└── README.md            # Project documentation

⚙️ Quick Start

    Clone the Repository:
    Bash

    git clone [https://github.com/63RmaN/dava-security-agent.git](https://github.com/63RmaN/dava-security-agent.git)
    cd dava-security-agent

    Install Dependencies:
    Bash

    pip install -r requirements.txt

    Configure Settings:
    Set up your local configuration endpoints (such as your GPU node IP 10.0.0.152) inside your environment or config file.

    Launch DAVA:
    Bash

    python main.py

👤 Author

German Quezada

Cybersecurity Analyst | Senior Infrastructure Specialist | Automation Engineer

    LinkedIn Profile

    GitHub Profile

videos: https://gedwinquezada.wixsite.com/chaos2security/about-1
---
