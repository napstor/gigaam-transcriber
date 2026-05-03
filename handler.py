import runpod
import gigaam
import tempfile
import os
import base64
import requests
import subprocess

model = gigaam.load_model("v2_ctc")

def to_wav(input_path: str) -> str:
    out_path = input_path + ".wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", out_path],
        capture_output=True, check=True
    )
    return out_path

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
        transcription = model.transcribe(wav_path)
        os.unlink(wav_path)
    finally:
        os.unlink(tmp_path)

    return {"transcription": transcription}

runpod.serverless.start({"handler": handler})
