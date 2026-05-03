import runpod
import gigaam
import tempfile
import os
import base64
import requests
import subprocess
import soundfile as sf
import numpy as np

model = gigaam.load_model("v2_ctc")

CHUNK_SEC = 25
SAMPLE_RATE = 16000

def to_wav(input_path: str) -> str:
    out_path = input_path + ".wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, "-ar", str(SAMPLE_RATE), "-ac", "1", out_path],
        capture_output=True, check=True
    )
    return out_path

def transcribe_long(wav_path: str) -> str:
    audio, _ = sf.read(wav_path, dtype="float32")
    chunk_size = CHUNK_SEC * SAMPLE_RATE
    parts = []

    for start in range(0, len(audio), chunk_size):
        chunk = audio[start:start + chunk_size]
        if len(chunk) < SAMPLE_RATE:
            continue
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            chunk_path = f.name
        sf.write(chunk_path, chunk, SAMPLE_RATE)
        try:
            parts.append(model.transcribe(chunk_path))
        finally:
            os.unlink(chunk_path)

    return " ".join(parts)

def handler(job):
    inp = job["input"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".audio") as f:
        if "audio_base64" in inp:
            f.write(base64.b64decode(inp["audio_base64"]))
        elif "audio_url" in inp:
            f.write(requests.get(inp["audio_url"], timeout=120).content)
        else:
            return {"error": "Provide audio_url or audio_base64"}
        tmp_path = f.name

    try:
        wav_path = to_wav(tmp_path)
        transcription = transcribe_long(wav_path)
        os.unlink(wav_path)
    finally:
        os.unlink(tmp_path)

    return {"transcription": transcription}

runpod.serverless.start({"handler": handler})
