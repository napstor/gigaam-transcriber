import runpod
import gigaam
import tempfile
import os
import requests
import subprocess

model = gigaam.load_model("v2_ctc")

def to_wav(input_path: str) -> str:
    """Конвертировать любой аудиоформат в WAV 16kHz mono через ffmpeg."""
    out_path = input_path + ".wav"
    subprocess.run(
        ["ffmpeg", "-y", "-i", input_path, "-ar", "16000", "-ac", "1", out_path],
        capture_output=True, check=True
    )
    return out_path

def handler(job):
    audio_url = job["input"]["audio_url"]

    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(requests.get(audio_url, timeout=120).content)
        tmp_path = f.name

    try:
        wav_path = to_wav(tmp_path)
        transcription = model.transcribe(wav_path)
        os.unlink(wav_path)
    finally:
        os.unlink(tmp_path)

    return {"transcription": transcription}

runpod.serverless.start({"handler": handler})
