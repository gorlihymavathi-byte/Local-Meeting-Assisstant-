# Local-Meeting-Assisstant-

# 🎙️ Local-First AI Meeting & Learning Assistant (macOS)

A 100% local, privacy-first, and zero-subscription automated meeting minutes and learning assistant built for macOS. Designed to record sessions, transcribe audio offline, generate structured AI summaries, and push formatted reports directly to Slack—without a single byte of data ever touching the public cloud.
---

## 💡 Why This Project?
Commercial AI meeting tools and platforms like Notion require recurring monthly SaaS subscriptions and rely on cloud servers, posing privacy risks when handling confidential team meetings or sensitive family data. 

This project was built to solve two primary use cases:
1. **Personal Learning Tracker:** Recording and tracking a 6-year-old child's English class progress, vocabulary, and milestones.
2. **Team Meeting Minutes:** Capturing professional internal team discussions while ensuring strict confidentiality and data compliance.

---

## 🛠️ The Tech Stack
* **Python (`sounddevice`)**: Lightweight local script to record room audio via a simple keystroke/trigger.
* **Faster-Whisper**: High-accuracy, offline speech-to-text processing running entirely on local hardware.
* **Ollama (`llama3.2`)**: Local LLM engine to synthesize raw transcripts into structured executive summaries, action items, or vocabulary lists.
* **n8n + Slack**: Workflow automation tool to package and pipe formatted reports straight into private Slack channels.

---

## 🚀 Architecture Flow

[ macOS Mic ] ➡️ [ Python / SoundDevice ] ➡️ [ Faster-Whisper (Local) ]
│
[ Slack Channel ] ⬅️ [ n8n Webhook ] ⬅️ [ Ollama / Llama 3.2 (Local) ]


1. **Record:** Python captures session audio locally.
2. **Transcribe:** Faster-Whisper translates speech to text offline.
3. **Summarize:** Ollama generates structured insights locally.
4. **Deliver:** n8n formats and drops the notes into Slack.

---

## ⚙️ Getting Started & Prerequisites

### 1. Prerequisites
Ensure you have the following installed on your macOS machine:
* Python 3.x
* [Ollama](https://ollama.com/) (running locally)
* An active [n8n](https://n8n.io/) instance (self-hosted or local) with a Slack webhook integration.

### 2. Install Dependencies
Clone this repository and install the required Python packages:
```bash
pip3 install sounddevice faster-whisper ollama numpy requests


Privacy & Compliance Note
When building and using local AI transcription tools, maintaining data compliance is critical. This tool is designed to operate completely offline to eliminate cloud-related data leakage risks.

Important: Always ensure compliance with local regulations (such as GDPR) by recording conversations only with the explicit, informed consent of all participants.
