"""Servicio interno de transcripción. Se ejecuta con un worker de Gunicorn."""

import os
import subprocess
import tempfile
import threading

from flask import Flask, jsonify, request
from faster_whisper import WhisperModel
from werkzeug.exceptions import RequestEntityTooLarge


MAX_AUDIO_BYTES = 10 * 1024 * 1024
MAX_AUDIO_SECONDS = 60
MODEL_DIR = os.getenv("VOICE_MODEL_DIR", "/models")
CPU_THREADS = int(os.getenv("VOICE_CPU_THREADS", "4"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_AUDIO_BYTES + 256 * 1024

# Una sola instancia por proceso; Gunicorn se configura con exactamente un worker.
model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8",
    cpu_threads=CPU_THREADS,
    num_workers=1,
    download_root=MODEL_DIR,
)
inferencia = threading.BoundedSemaphore(value=1)


@app.get("/health")
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None}), 200


@app.post("/transcribir")
def transcribir():
    if request.content_length is None:
        return jsonify({"code": "content_length_required"}), 411
    if request.content_length > MAX_AUDIO_BYTES + 256 * 1024:
        return jsonify({"code": "audio_too_large"}), 413
    if not inferencia.acquire(blocking=False):
        return jsonify({"code": "voice_busy", "msg": "El servicio de voz está ocupado."}), 429

    ruta_temporal = None
    try:
        archivo = request.files.get("audio")
        if archivo is None:
            return jsonify({"code": "audio_required"}), 400

        audio = archivo.stream.read(MAX_AUDIO_BYTES + 1)
        if not audio:
            return jsonify({"code": "audio_empty"}), 400
        if len(audio) > MAX_AUDIO_BYTES:
            return jsonify({"code": "audio_too_large"}), 413

        mime_type = (archivo.mimetype or "").lower()
        if mime_type not in {"audio/mp4", "audio/webm", "audio/ogg", "audio/wav", "application/octet-stream"}:
            return jsonify({"code": "audio_type_unsupported"}), 400
        extension = ".mp4" if mime_type == "audio/mp4" else ".webm" if mime_type == "audio/webm" else ".audio"

        with tempfile.NamedTemporaryFile(prefix="iph-voice-", suffix=extension, dir="/tmp", delete=False) as temporary:
            ruta_temporal = temporary.name
            temporary.write(audio)
        del audio

        probe = subprocess.run(
            [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", ruta_temporal,
            ],
            check=True,
            capture_output=True,
            text=True,
            timeout=8,
        )
        duracion = float(probe.stdout.strip())
        if duracion <= 0:
            return jsonify({"code": "audio_invalid"}), 400
        if duracion > MAX_AUDIO_SECONDS:
            return jsonify({"code": "audio_too_long"}), 422

        segmentos, info = model.transcribe(
            ruta_temporal,
            language="es",
            beam_size=1,
            vad_filter=True,
            condition_on_previous_text=False,
        )
        if info.duration > MAX_AUDIO_SECONDS:
            return jsonify({"code": "audio_too_long"}), 422
        texto = "".join(segment.text for segment in segmentos).strip()
        if not texto:
            return jsonify({"code": "no_speech", "msg": "No se detectó voz en la grabación."}), 422
        return jsonify({"text": texto}), 200
    except subprocess.TimeoutExpired:
        return jsonify({"code": "audio_decode_timeout"}), 400
    except RequestEntityTooLarge:
        return jsonify({"code": "audio_too_large"}), 413
    except (subprocess.CalledProcessError, ValueError, OSError):
        return jsonify({"code": "audio_invalid"}), 400
    except Exception as error:
        # Solo se registra la clase de error; nunca audio, texto ni datos de la solicitud.
        app.logger.error("Local transcription failed (%s)", type(error).__name__)
        return jsonify({"code": "transcription_failed"}), 500
    finally:
        if ruta_temporal:
            try:
                os.unlink(ruta_temporal)
            except FileNotFoundError:
                pass
        inferencia.release()
