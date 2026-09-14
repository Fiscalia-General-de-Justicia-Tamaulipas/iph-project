from datetime import datetime, date, time as dtime

from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import inspect

from app.extensions import db
from app.models.iph import (
    IPH,
    ConocimientoHecho,
    ActaNoticia,
    AccionRealizada,
    Denunciante,
    Ofendido,
    Victima,
    PolicíaActuante,
    Imputado,
    Testigo,
    InspeccionLugar,
    InspeccionPersona,
    InspeccionVehiculo,
    NarracionPrimerRespondiente,
    Actuacion,
)
from app.services.pdf_generator import generar_pdf_iph

iph_bp = Blueprint("iph", __name__)


def _fetch_all(sql, params=()):
    conn = None
    cursor = None
    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if not cursor.description:
            return []
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception:
        return []
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


def _fetch_one(sql, params=()):
    conn = None
    cursor = None
    try:
        conn = db.engine.raw_connection()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        if not cursor.description:
            return None
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    except Exception:
        return None
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


def _pick_value(row, *keys):
    if not row:
        return None
    normalized = {str(k).upper(): v for k, v in row.items()}
    for key in keys:
        if key in row:
            return row[key]
        if str(key).upper() in normalized:
            return normalized[str(key).upper()]
    return None


def _normalize_iph_row(row):
    if not row:
        return {}

    payload = {}
    for key, value in row.items():
        if value is None:
            continue
        payload[str(key).upper()] = value

    iph_id = (
        payload.get("ID_IPH")
        or payload.get("IDIPH")
        or payload.get("id_iph")
        or payload.get("ID")
    )
    if iph_id is not None:
        payload["id"] = iph_id
        payload["ID_IPH"] = iph_id

    folio = (
        payload.get("IPH")
        or payload.get("FOLIO_INTERNO")
        or payload.get("folio_interno")
        or payload.get("FOLIO")
    )
    if folio is not None:
        payload["folio_interno"] = folio
        payload["IPH"] = folio

    payload["no_expediente"] = payload.get("NUC") or payload.get("NO_EXPEDIENTE") or payload.get("no_expediente")
    payload["estado"] = payload.get("ESTADO") or payload.get("ESTADO_CARPETA") or payload.get("estado") or "EN_TRAMITE"
    payload["adscripcion"] = payload.get("UNIDAD") or payload.get("ADSCRIPCION") or payload.get("adscripcion") or ""
    payload["denunciante"] = payload.get("DENUNCIANTE") or payload.get("denunciante") or ""
    payload["imputado"] = payload.get("IMPUTADO") or payload.get("imputado") or ""
    payload["creado_en"] = payload.get("FECHA_IPH") or payload.get("FECHA_INICIO") or payload.get("creado_en")
    payload["FECHA_IPH"] = payload.get("creado_en") or payload.get("FECHA_IPH")
    payload["UNIDAD"] = payload.get("UNIDAD") or payload.get("adscripcion") or ""
    payload["ESTADO_CARPETA"] = payload.get("ESTADO_CARPETA") or payload.get("estado") or "EN_TRAMITE"
    payload["ID_CARPETA"] = payload.get("ID_CARPETA") or 0

    return {
        "id": payload.get("id"),
        "ID_IPH": payload.get("ID_IPH"),
        "ID_CARPETA": payload.get("ID_CARPETA"),
        "IPH": payload.get("IPH") or payload.get("folio_interno"),
        "folio_interno": payload.get("folio_interno") or payload.get("IPH"),
        "NUC": payload.get("NUC") or payload.get("no_expediente"),
        "no_expediente": payload.get("no_expediente"),
        "estado": payload.get("estado"),
        "ESTADO_CARPETA": payload.get("ESTADO_CARPETA"),
        "adscripcion": payload.get("adscripcion"),
        "UNIDAD": payload.get("UNIDAD"),
        "denunciante": payload.get("denunciante"),
        "DENUNCIANTE": payload.get("DENUNCIANTE") or payload.get("denunciante"),
        "imputado": payload.get("imputado"),
        "IMPUTADO": payload.get("IMPUTADO") or payload.get("imputado"),
        "creado_en": payload.get("creado_en"),
        "FECHA_IPH": payload.get("FECHA_IPH"),
        **payload,
    }


# Módulos donde solo existe UN registro por IPH (tarjetas de un solo apartado)
MODULOS_UNO_A_UNO = {
    "conocimiento_hecho": ConocimientoHecho,
    "acta_noticia": ActaNoticia,
    "inspeccion_lugar": InspeccionLugar,
    "narracion_primer_respondiente": NarracionPrimerRespondiente,
}

# Módulos donde puede haber VARIOS registros por IPH (listas repetibles)
MODULOS_UNO_A_MUCHOS = {
    "acciones_realizadas": AccionRealizada,
    "denunciantes": Denunciante,
    "ofendidos": Ofendido,
    "victimas": Victima,
    "policias": PolicíaActuante,
    "imputados": Imputado,
    "testigos": Testigo,
    "inspecciones_persona": InspeccionPersona,
    "inspecciones_vehiculo": InspeccionVehiculo,
    "actuaciones": Actuacion,
}


def modelo_a_dict(instancia):
    """Convierte una instancia de modelo SQLAlchemy en dict serializable a JSON."""
    resultado = {}
    for columna in inspect(instancia.__class__).columns:
        valor = getattr(instancia, columna.name)
        if isinstance(valor, (date, dtime, datetime)):
            valor = valor.isoformat()
        resultado[columna.name] = valor
    return resultado


def asignar_campos(instancia, data, modelo):
    """Asigna solo los campos que existen como columnas del modelo, ignorando el resto."""
    columnas_validas = {c.name for c in inspect(modelo).columns}
    for campo, valor in data.items():
        if campo in columnas_validas and campo not in ("id", "iph_id"):
            setattr(instancia, campo, valor)


# ---------------------------------------------------------------------------
# CRUD principal del folio IPH
# ---------------------------------------------------------------------------

@iph_bp.get("/")
@jwt_required()
def listar_iph():
    usuario_id = get_jwt_identity()

    perfil = None
    for sql in [
        "SELECT TOP 1 * FROM cat_usuario WHERE id_usuario = ?",
        "SELECT TOP 1 * FROM cat_usuario WHERE ID_USUARIO = ?",
        "SELECT TOP 1 * FROM usuarios WHERE id = ?",
        "SELECT TOP 1 * FROM usuarios WHERE id_usuario = ?",
    ]:
        perfil = _fetch_one(sql, (usuario_id,))
        if perfil:
            break

    if not perfil:
        return jsonify([]), 200

    municipio = _pick_value(
        perfil,
        "ID_MNCPIO",
        "ID_MUNICIPIO",
        "id_mncpio",
        "Id_Mncpio",
        "MNCPIO",
        "MUNICIPIO",
    )
    unidad = _pick_value(
        perfil,
        "Id_Undd",
        "ID_UNDD",
        "ID_UNIDAD",
        "id_unidad",
        "UNIDAD",
        "Unidad",
    )

    if municipio is None or unidad is None:
        return jsonify([]), 200

    registros = []
    for sql, params in [
        ("EXEC IPH_ConsultaIPH @IdMunicipio = ?, @IdUnidad = ?", (municipio, unidad)),
        ("EXEC IPH_ConsultaIPH @Municipio = ?, @Unidad = ?", (municipio, unidad)),
    ]:
        registros = _fetch_all(sql, params)
        if registros:
            break

    if not registros:
        return jsonify([]), 200

    catalogo = []
    for registro in registros:
        item = _normalize_iph_row(registro)
        if item.get("id") is None:
            continue
        catalogo.append({
            "id": item.get("id"),
            "ID_IPH": item.get("ID_IPH") or item.get("id"),
            "IPH": item.get("IPH") or item.get("folio_interno") or "",
            "folio_interno": item.get("folio_interno") or item.get("IPH") or "",
            "FECHA_IPH": item.get("FECHA_IPH") or item.get("creado_en") or "",
            "creado_en": item.get("creado_en") or item.get("FECHA_IPH") or "",
            "DENUNCIANTE": item.get("DENUNCIANTE") or item.get("denunciante") or "",
            "denunciante": item.get("denunciante") or item.get("DENUNCIANTE") or "",
            "IMPUTADO": item.get("IMPUTADO") or item.get("imputado") or "",
            "imputado": item.get("imputado") or item.get("IMPUTADO") or "",
            "NUC": item.get("NUC") or item.get("no_expediente") or "",
            "no_expediente": item.get("no_expediente") or item.get("NUC") or "",
            "UNIDAD": item.get("UNIDAD") or item.get("adscripcion") or "",
            "adscripcion": item.get("adscripcion") or item.get("UNIDAD") or "",
            "ESTADO_CARPETA": item.get("ESTADO_CARPETA") or item.get("estado") or "EN_TRAMITE",
            "estado": item.get("estado") or item.get("ESTADO_CARPETA") or "EN_TRAMITE",
            "ID_CARPETA": item.get("ID_CARPETA") or 0,
            "estado_modulos": {},
        })

    return jsonify(catalogo), 200


@iph_bp.post("/")
@jwt_required()
def crear_iph():
    return jsonify({"msg": "La creación de IPH se realiza en el sistema principal / base de datos original."}), 501


@iph_bp.get("/<int:iph_id>")
@jwt_required()
def obtener_iph(iph_id):
    try:
        registro = _fetch_one("SELECT TOP 1 * FROM IPH WHERE ID_IPH = ?", (iph_id,))
    except Exception as exc:
        return jsonify({"msg": "No fue posible consultar el IPH solicitado.", "detalle": str(exc)}), 503

    if not registro:
        return jsonify({"msg": "IPH no encontrado"}), 404

    item = _normalize_iph_row(registro)
    return jsonify({
        "id": item.get("id"),
        "folio_interno": item.get("folio_interno") or item.get("IPH") or "",
        "no_referencia": item.get("NO_REFERENCIA") or item.get("no_referencia"),
        "no_expediente": item.get("no_expediente") or item.get("NUC") or "",
        "estado": item.get("estado") or "EN_TRAMITE",
        "estado_modulos": {},
    }), 200


# ---------------------------------------------------------------------------
# Módulos de un solo registro (conocimiento_hecho, acta_noticia,
# inspeccion_lugar, narracion_primer_respondiente)
# ---------------------------------------------------------------------------

@iph_bp.get("/<int:iph_id>/<string:modulo>")
@jwt_required()
def obtener_modulo_unico(iph_id, modulo):
    if modulo not in MODULOS_UNO_A_UNO:
        return jsonify({"msg": "Módulo no encontrado"}), 404

    modelo = MODULOS_UNO_A_UNO[modulo]
    instancia = modelo.query.filter_by(iph_id=iph_id).first()
    if not instancia:
        return jsonify(None), 200
    return jsonify(modelo_a_dict(instancia)), 200


@iph_bp.put("/<int:iph_id>/<string:modulo>")
@jwt_required()
def guardar_modulo_unico(iph_id, modulo):
    if modulo not in MODULOS_UNO_A_UNO:
        return jsonify({"msg": "Módulo no encontrado"}), 404

    IPH.query.get_or_404(iph_id)  # valida que el folio exista
    modelo = MODULOS_UNO_A_UNO[modulo]
    data = request.get_json(silent=True) or {}

    instancia = modelo.query.filter_by(iph_id=iph_id).first()
    if not instancia:
        instancia = modelo(iph_id=iph_id)
        db.session.add(instancia)

    asignar_campos(instancia, data, modelo)
    db.session.commit()
    return jsonify(modelo_a_dict(instancia)), 200


# ---------------------------------------------------------------------------
# Módulos de varios registros (denunciantes, ofendidos, imputados, etc.)
# ---------------------------------------------------------------------------

@iph_bp.get("/<int:iph_id>/<string:modulo>/lista")
@jwt_required()
def listar_modulo_multiple(iph_id, modulo):
    if modulo not in MODULOS_UNO_A_MUCHOS:
        return jsonify({"msg": "Módulo no encontrado"}), 404

    modelo = MODULOS_UNO_A_MUCHOS[modulo]
    registros = modelo.query.filter_by(iph_id=iph_id).all()
    return jsonify([modelo_a_dict(r) for r in registros]), 200


@iph_bp.post("/<int:iph_id>/<string:modulo>/lista")
@jwt_required()
def crear_item_modulo_multiple(iph_id, modulo):
    if modulo not in MODULOS_UNO_A_MUCHOS:
        return jsonify({"msg": "Módulo no encontrado"}), 404

    IPH.query.get_or_404(iph_id)
    modelo = MODULOS_UNO_A_MUCHOS[modulo]
    data = request.get_json(silent=True) or {}

    instancia = modelo(iph_id=iph_id)
    asignar_campos(instancia, data, modelo)
    db.session.add(instancia)
    db.session.commit()
    return jsonify(modelo_a_dict(instancia)), 201


@iph_bp.put("/<int:iph_id>/<string:modulo>/lista/<int:item_id>")
@jwt_required()
def actualizar_item_modulo_multiple(iph_id, modulo, item_id):
    if modulo not in MODULOS_UNO_A_MUCHOS:
        return jsonify({"msg": "Módulo no encontrado"}), 404

    modelo = MODULOS_UNO_A_MUCHOS[modulo]
    instancia = modelo.query.filter_by(id=item_id, iph_id=iph_id).first_or_404()
    data = request.get_json(silent=True) or {}

    asignar_campos(instancia, data, modelo)
    db.session.commit()
    return jsonify(modelo_a_dict(instancia)), 200


@iph_bp.delete("/<int:iph_id>/<string:modulo>/lista/<int:item_id>")
@jwt_required()
def eliminar_item_modulo_multiple(iph_id, modulo, item_id):
    if modulo not in MODULOS_UNO_A_MUCHOS:
        return jsonify({"msg": "Módulo no encontrado"}), 404

    modelo = MODULOS_UNO_A_MUCHOS[modulo]
    instancia = modelo.query.filter_by(id=item_id, iph_id=iph_id).first_or_404()
    db.session.delete(instancia)
    db.session.commit()
    return jsonify({"msg": "Eliminado"}), 200


# ---------------------------------------------------------------------------
# Exportación a PDF
# ---------------------------------------------------------------------------

@iph_bp.get("/<int:iph_id>/exportar-pdf")
@jwt_required()
def exportar_pdf(iph_id):
    registro = IPH.query.get_or_404(iph_id)
    ruta_pdf = generar_pdf_iph(registro)
    nombre_descarga = f"IPH_{registro.folio_interno}.pdf"
    return send_file(ruta_pdf, as_attachment=True, download_name=nombre_descarga, mimetype="application/pdf")
