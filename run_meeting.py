import time
import wave
import sys
import urllib.request
import json
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel
import ollama

# --- CONFIGURATION ---
SAMPLE_RATE = 16000
CHANNELS = 1
AUDIO_FILE = "meeting_audio.wav"
TRANSCRIPT_FILE = "transcript.txt"
SUMMARY_FILE = "meeting_summary.md"
MODEL_SIZE = "base"
OLLAMA_MODEL = "llama3.2"
N8N_WEBHOOK_URL = "http://localhost:5678/webhook-test/meeting-notes"
MAX_DURATION_SECONDS = 7200

def record_flexible_meeting():
    """Records audio flexibly. Press Ctrl + C anytime to stop and process."""
    print(f"\n🎙️ [1/3] Meeting Assistant Active (Max Duration: 2 Hours)")
    print("👉 Recording started...")
    print("💡 **TIP:** When your meeting is over, press **Ctrl + C** to stop and send to n8n!\n")

    chunk_duration = 5
    chunks = []
    
    start_time = time.time()
    try:
        while (time.time() - start_time) < MAX_DURATION_SECONDS:
            elapsed = int(time.time() - start_time)
            mins, secs = divmod(elapsed, 60)
            sys.stdout.write(f"\r🔴 Recording in progress... Time elapsed: {mins:02d}:{secs:02d} (Press Ctrl + C to stop)")
            sys.stdout.flush()

            audio_chunk = sd.rec(
                int(chunk_duration * SAMPLE_RATE),
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                dtype='int16'
            )
            sd.wait()
            chunks.append(audio_chunk)

    except KeyboardInterrupt:
        print("\n\n⏹️ Meeting stopped by user! Processing notes...")

    full_recording = np.concatenate(chunks, axis=0)

    with wave.open(AUDIO_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(full_recording.tobytes())
    
    print(f"💾 Audio saved to '{AUDIO_FILE}'")

def transcribe_audio():
    """Step 2: Transcribe audio offline using Faster-Whisper."""
    print(f"\n🔄 [2/3] Transcribing meeting offline...")

    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

    try:
        segments, info = model.transcribe(
            AUDIO_FILE,
            beam_size=5,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
    except Exception as e:
        print(f"❌ Transcription error: {e}")
        return ""

    print(f"🌍 Detected language '{info.language}' with probability {info.language_probability:.2f}\n")

    full_transcript = []
    for segment in segments:
        timestamp = f"[{segment.start/60:.1f}m -> {segment.end/60:.1f}m]"
        text = segment.text.strip()
        line = f"{timestamp} {text}"
        print(line)
        full_transcript.append(line)

    transcript_text = "\n".join(full_transcript)

    with open(TRANSCRIPT_FILE, "w", encoding="utf-8") as f:
        f.write(transcript_text)

    return transcript_text

def summarize_text(transcript_text):
    """Step 3: Generate structured notes via local Ollama."""
    if not transcript_text.strip():
        print("⚠️ Transcript was empty. Skipping summarization.")
        return ""

    print(f"\n🤖 [3/3] Generating Executive Summary using local Ollama ({OLLAMA_MODEL})...")

    prompt = f"""
    You are an expert Executive Meeting Assistant. Analyze the following meeting transcript and produce a detailed, high-level summary:

    ## 1. Executive Summary
    (Concise high-level overview of the main purpose and outcomes of the meeting)

    ## 2. Key Discussion Topics & Themes
    (Detailed bullet points organized by topic)

    ## 3. Important Decisions
    (Numbered list of agreed items and policies)

    ## 4. Action Items & Next Steps
    (Checklist format `[ ]` assigning clear owners and tasks wherever specified)

    Meeting Transcript:
    {transcript_text}
    """

    response = ollama.chat(model=OLLAMA_MODEL, messages=[
        {
            'role': 'system',
            'content': 'You are a precise enterprise executive assistant that synthesizes meeting transcripts into clear action plans factually and neutrally.'
        },
        {
            'role': 'user',
            'content': prompt,
        },
    ])

    summary = response['message']['content']

    print("\n--- 📊 MEETING SUMMARY ---")
    print(summary)
    print("----------------------------")

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"\n💾 Summary saved locally to '{SUMMARY_FILE}'!")
    return summary

def send_to_n8n(summary_text, transcript_text):
    """Step 4: Sends summary and transcript payload to n8n webhook."""
    if not N8N_WEBHOOK_URL:
        print("⚠️ n8n Webhook URL not configured.")
        return

    print("\n🚀 Dispatching meeting data to n8n workflow...")
    
    payload = {
        "summary": summary_text,
        "transcript": transcript_text,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    req = urllib.request.Request(
        N8N_WEBHOOK_URL,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status in (200, 201):
                print("✅ Successfully triggered n8n workflow!")
            else:
                print(f"⚠️ n8n responded with status code: {response.status}")
    except Exception as e:
        print(f"❌ Error communicating with n8n: {e}")

if __name__ == "__main__":
    print("🚀 Starting Flexible Local AI Meeting Assistant with n8n...")

    # 1. Record
    record_flexible_meeting()

    # 2. Transcribe
    transcript = transcribe_audio()

    # 3. Summarize & Dispatch
    if transcript.strip():
        summary = summarize_text(transcript)
        send_to_n8n(summary, transcript)
    else:
        print("⚠️ Transcript was empty. Skipping summarization and n8n trigger.")
    
    print("\n✨ Process completed successfully!")
