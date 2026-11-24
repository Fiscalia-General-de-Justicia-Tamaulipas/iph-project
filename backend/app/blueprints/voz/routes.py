from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
import requests


voz_bp = Blueprint("voz", __name__)


@voz_bp.post("/transcribir")
@jwt_required()
def transcribir():
    max_audio_bytes = current_app.config["VOICE_MAX_AUDIO_BYTES"]
    # El multipart agrega cabeceras y boundary; este margen solo contempla el envoltorio.
    max_request_bytes = max_audio_bytes + 256 * 1024
    if request.content_length is None:
        return jsonify({"code": "content_length_required", "msg": "La solicitud debe indicar el tamaño del audio."}), 411
    if request.content_length > max_request_bytes:
        return jsonify({"code": "audio_too_large", "msg": "El audio supera el límite de 10 MB."}), 413

    archivo = request.files.get("audio")
    if archivo is None:
        return jsonify({"code": "audio_required", "msg": "Adjunta una grabación de audio."}), 400

    audio = archivo.stream.read(max_audio_bytes + 1)
    if not audio:
        return jsonify({"code": "audio_empty", "msg": "La grabación está vacía."}), 400
    if len(audio) > max_audio_bytes:
        return jsonify({"code": "audio_too_large", "msg": "El audio supera el límite de 10 MB."}), 413

    mime_type = (archivo.mimetype or "application/octet-stream").lower()
    if mime_type not in {"audio/mp4", "audio/webm", "audio/ogg", "audio/wav", "application/octet-stream"}:
        return jsonify({"code": "audio_type_unsupported", "msg": "El formato de audio no está admitido."}), 415

    try:
        response = requests.post(
            f"{current_app.config['VOICE_SERVICE_URL'].rstrip('/')}/transcribir",
            files={"audio": ("dictado", audio, mime_type)},
            timeout=(
                current_app.config["VOICE_CONNECT_TIMEOUT_SECONDS"],
                current_app.config["VOICE_READ_TIMEOUT_SECONDS"],
            ),
        )
    except requests.Timeout:
        return jsonify({"code": "voice_timeout", "msg": "La transcripción excedió el tiempo límite. Inténtalo de nuevo."}), 504
    except requests.RequestException:
        return jsonify({"code": "voice_unavailable", "msg": "El servicio de voz no está disponible temporalmente."}), 503

    if response.status_code == 429:
        return jsonify({"code": "voice_busy", "msg": "El servicio de voz está ocupado. Espera unos segundos y vuelve a intentar."}), 429
    if response.status_code == 413:
        return jsonify({"code": "audio_too_large", "msg": "El audio supera el límite de 10 MB."}), 413
    if response.status_code == 422:
        try:
            upstream_code = response.json().get("code")
        except ValueError:
            upstream_code = ""
        if upstream_code == "no_speech":
            return jsonify({"code": "no_speech", "msg": "No se detectó voz en la grabación."}), 422
        return jsonify({"code": "audio_too_long", "msg": "La grabación no puede superar 60 segundos."}), 422
    if response.status_code == 400:
        return jsonify({"code": "audio_invalid", "msg": "No se pudo leer el audio. Vuelve a grabarlo."}), 400
    if response.status_code != 200:
        return jsonify({"code": "voice_error", "msg": "No se pudo completar la transcripción."}), 502

    try:
        result = response.json()
        texto = result.get("text", "")
    except (ValueError, AttributeError):
        return jsonify({"code": "voice_error", "msg": "El servicio de voz devolvió una respuesta inválida."}), 502

    return jsonify({"text": texto}), 200
