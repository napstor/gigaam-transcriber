FROM runpod/pytorch:2.2.0-py3.10-cuda12.1.1-devel-ubuntu22.04

WORKDIR /app

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir gigaam runpod requests soundfile numpy

# Скачать модель при сборке — не при каждом запросе
RUN python3 -c "import gigaam; gigaam.load_model('v2_ctc')"

COPY handler.py .

CMD ["python3", "-u", "handler.py"]
