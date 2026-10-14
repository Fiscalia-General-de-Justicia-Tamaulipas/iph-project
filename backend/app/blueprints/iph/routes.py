from datetime import datetime, date, time as dtime

from flask import Blueprint, current_app, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
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


def _fetch_all(sql, params=(), *, raise_errors=False):
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
        if raise_errors:
            raise
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
    estados = (
        "ESTADO",
        "ESTADO_CARPETA",
        "ESTADO_IPH",
        "ESTATUS_IPH",
        "ESTATUS",
        "DESCRIPCION_ESTADO_IPH",
        "ID_ESTADO_IPH",
        "estado",
    )
    payload["estado"] = next(
        (payload[key] for key in estados if payload.get(key) is not None and payload[key] != ""),
        "EN_TRAMITE",
    )
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
    "imputado": Imputado,
    "testigos": Testigo,
    "testigo": Testigo,
    "inspecciones_persona": InspeccionPersona,
    "inspeccion_persona": InspeccionPersona,
    "inspecciones_vehiculo": InspeccionVehiculo,
    "inspeccion_vehiculo": InspeccionVehiculo,
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


def _normalizar_payload_conocimiento_hecho(data):
    if not isinstance(data, dict):
        return {}

    payload = dict(data)
    aliases = {
        "ID_INSTITUCION_INFORMANTE": "id_institucion_informante",
        "ID_INSTITUCION": "id_institucion_informante",
        "PUSO_DISPOSICION": "id_institucion_informante",
        "ID_CARGO": "id_cargo",
        "ID_ESTADO": "id_estado",
        "ID_ESTADO_CON": "id_estado",
        "ID_MUNICIPIO": "id_municipio",
        "ID_MUNICIPIO_CON": "id_municipio",
        "ID_USUARIO": "id_usuario",
        "FECHA_CONOCIMIENTO": "fecha_conocimiento",
        "HORA_CONOCIMIENTO": "hora_conocimiento",
        "FECHA_ARRIBO": "fecha_arribo",
        "HORA_ARRIBO": "hora_arribo",
    }

    for clave, valor in list(payload.items()):
        destino = aliases.get(str(clave).upper())
        if destino and clave != destino:
            payload[destino] = valor
            del payload[clave]

    return payload


def _normalizar_payload_acta_noticia(data):
    if not isinstance(data, dict):
        return {}

    payload = dict(data)
    aliases = {
        "TIPO_EVENTO": "tipo_evento",
        "DDLTIPOEVENTO": "tipo_evento",
        "RBNOTICIAS": "medio_noticia",
        "MEDIO_NOTICIA": "medio_noticia",
        "SE_RECIBIO_NOTICIA_MEDIANTE": "medio_noticia",
        "ESPECIFIQUE_NOTICIA": "especifica_noticia",
        "TXTESPECIFIQUENOTICIA": "especifica_noticia",
        "TIPO_DELITO": "tipo_delito",
        "DDLDELITO": "tipo_delito",
        "FECHA_ARRIBO": "fecha_arribo",
        "HORA_ARRIBO": "hora_arribo",
        "TIPO_DE_DELITO": "tipo_delito",
        "MUNICIPIO_ARRIBO": "municipio_arribo",
        "DDLMUNICIPIOARRIBO": "municipio_arribo",
        "LOCALIDAD_ARRIBO": "localidad_arribo",
        "DDLLOCALIDADARRIBO": "localidad_arribo",
        "REFERENCIAS_ARRIBO": "referencias_arribo",
        "TXTREFERENCIASARRIBO": "referencias_arribo",
        "REQUIERE_APOYO": "requiere_apoyo",
        "RBAPOYO": "requiere_apoyo",
        "ESPECIFIQUE_APOYO": "especifica_apoyo",
        "TXTESPECIFIQUEAPOYO": "especifica_apoyo",
        "ORGANIZACIONES_PARTICIPANTES": "organizaciones_participantes",
        "CHPROTECCION": "organizaciones_participantes",
        "CHBOMBEROS": "organizaciones_participantes",
        "CHURGENCIAS": "organizaciones_participantes",
        "ESPECIFIQUE_ORGANIZACION": "especifica_organizacion",
        "TXTESPECIFIQUEOORGANIZACION": "especifica_organizacion",
    }

    for clave, valor in list(payload.items()):
        destino = aliases.get(str(clave).upper())
        if destino and clave != destino:
            payload[destino] = valor
            del payload[clave]

    return payload


def _normalizar_payload_acciones_realizadas(data):
    if not isinstance(data, dict):
        return {}

    payload = dict(data)
    aliases = {
        "ID_ACCION": "id",
        "ORDEN": "orden",
        "NUMERO_ORDEN": "orden",
        "DESCRIPCION": "descripcion",
        "ACCION": "descripcion",
        "FECHA": "fecha",
        "HORA": "hora",
        "FECHA_ACCION": "fecha",
        "HORA_ACCION": "hora",
    }

    for clave, valor in list(payload.items()):
        destino = aliases.get(str(clave).upper())
        if destino and clave != destino:
            payload[destino] = valor
            del payload[clave]

    return payload


def _normalizar_payload_policia(data):
    if not isinstance(data, dict):
        return {}

    payload = dict(data)
    aliases = {
        "NOMBRE": "nombres",
        "NOMBRES": "nombres",
        "PATERNO": "primer_apellido",
        "PRIMER_APELLIDO": "primer_apellido",
        "MATERNO": "segundo_apellido",
        "SEGUNDO_APELLIDO": "segundo_apellido",
        "GRADO": "grado_cargo",
        "CARGO": "grado_cargo",
        "ID_CARGO": "id_cargo",
        "INSTITUCION": "institucion",
        "INSTITUCION_OTRA": "institucion_otra",
        "UNIDAD_ARRIBO": "unidad_arribo",
        "POL_RESPONSABLE": "pol_responsable",
        "RESPONSABLE": "pol_responsable",
        "HECHOS_CIERTOS": "hechos_ciertos",
        "ID_TIPO_ACTOR": "id_tipo_actor",
        "TIPO_ACTOR": "id_tipo_actor",
        "PRIMER_RESPONDIENTE": "es_primer_respondiente",
        "ES_PRIMER_RESPONDIENTE": "es_primer_respondiente",
    }

    for clave, valor in list(payload.items()):
        destino = aliases.get(str(clave).upper())
        if destino and clave != destino:
            payload[destino] = valor
            del payload[clave]

    if "nombres" not in payload and "nombre" in payload:
        payload["nombres"] = payload["nombre"]
    if "primer_apellido" not in payload and "paterno" in payload:
        payload["primer_apellido"] = payload["paterno"]
    if "segundo_apellido" not in payload and "materno" in payload:
        payload["segundo_apellido"] = payload["materno"]

    return payload


def _normalizar_payload_persona(data):
    if not isinstance(data, dict):
        return {}

    payload = dict(data)
    aliases = {
        "PRIMER_APELLIDO": "primer_apellido",
        "SEGUNDO_APELLIDO": "segundo_apellido",
        "NOMBRES": "nombres",
        "NOMBRE": "nombres",
        "SEXO": "sexo",
        "NACIONALIDAD": "nacionalidad",
        "FECHA_NACIMIENTO": "fecha_nacimiento",
        "EDAD": "edad",
        "TIPO_DOCUMENTO": "tipo_documento",
        "TIPO_IDENTIDAD": "tipo_documento",
        "NO_IDENTIFICACION": "no_identificacion",
        "NUMERO_IDENTIFICACION": "no_identificacion",
        "TELEFONO": "telefono",
        "CORREO": "correo",
        "EMAIL": "correo",
        "CALLE_TRAMO": "calle_tramo",
        "CALLE": "calle_tramo",
        "NO_EXTERIOR": "no_exterior",
        "NO_INTERIOR": "no_interior",
        "CODIGO_POSTAL": "codigo_postal",
        "COLONIA_LOCALIDAD": "colonia_localidad",
        "MUNICIPIO": "municipio",
        "ENTIDAD_FEDERATIVA": "entidad_federativa",
        "REFERENCIAS": "referencias",
        "ALIAS": "alias",
        "APODOS": "alias",
        "VESTIMENTA": "vestimenta",
        "HUELLAS": "huellas",
        "SEÑAS_PARTICULARES": "senas_particulares",
        "SENAS_PARTICULARES": "senas_particulares",
        "SEÑAS": "senas_particulares",
        "SENAS": "senas_particulares",
        "OTROS_RASGOS": "otros_rasgos",
        "CICATRICES": "cicatrices",
        "TATUAJES": "tatuajes",
        "PERFORACIONES": "perforaciones",
        "ESTATURA": "estatura",
        "COMPLEXION": "complexion",
        "COMPLEXIONES": "complexiones",
        "COLOR_OJOS": "color_ojos",
        "COLOR_PELO": "color_pelo",
    }

    for clave, valor in list(payload.items()):
        destino = aliases.get(str(clave).upper())
        if destino and clave != destino:
            payload[destino] = valor
            del payload[clave]

    for clave in ["alias", "vestimenta", "huellas", "senas_particulares", "cicatrices", "tatuajes", "perforaciones", "otros_rasgos"]:
        if isinstance(payload.get(clave), list):
            payload[clave] = "; ".join(str(item).strip() for item in payload[clave] if str(item).strip())

    return payload


def _normalizar_payload_inspeccion_persona(data):
    if not isinstance(data, dict):
        return {}

    payload = dict(data)
    aliases = {
        "ID_IMPUTADO": "imputado_id",
        "ID_PERSONA": "imputado_id",
        "IMPUTADO_ID": "imputado_id",
        "IMPUTADO": "imputado_id",
        "NARRATIVA": "narrativa",
        "NARRATIVA_INSPECCION": "narrativa",
        "ENCONTRO_OBJETO": "encontro_objeto",
        "RECOLECTO_PERTENENCIAS": "recolecto_pertenencias",
        "DESCRIPCION": "descripcion",
        "DESCRIPCION_OBJETO": "descripcion_objeto",
        "CANTIDAD_OBJETO": "cantidad_objeto",
        "TIPO_OBJETO": "tipo_objeto",
    }

    for clave, valor in list(payload.items()):
        destino = aliases.get(str(clave).upper())
        if destino and clave != destino:
            payload[destino] = valor
            del payload[clave]

    if "descripcion" in payload and isinstance(payload["descripcion"], list):
        payload["descripcion"] = "; ".join(str(item).strip() for item in payload["descripcion"] if str(item).strip())

    if "descripcion_objeto" in payload and isinstance(payload["descripcion_objeto"], list):
        payload["descripcion_objeto"] = "; ".join(str(item).strip() for item in payload["descripcion_objeto"] if str(item).strip())

    return payload


def asignar_campos(instancia, data, modelo):
    """Asigna solo los campos que existen como columnas del modelo, ignorando el resto."""
    columnas_validas = {c.name for c in inspect(modelo).columns}
    if modelo.__tablename__ == "conocimiento_hecho":
        data = _normalizar_payload_conocimiento_hecho(data)
    elif modelo.__tablename__ == "acta_noticia":
        data = _normalizar_payload_acta_noticia(data)
    elif modelo.__tablename__ == "acciones_realizadas":
        data = _normalizar_payload_acciones_realizadas(data)
    elif modelo.__tablename__ == "policias_actuantes":
        data = _normalizar_payload_policia(data)
    elif modelo.__tablename__ == "inspecciones_persona":
        data = _normalizar_payload_inspeccion_persona(data)
    elif modelo.__tablename__ in {"denunciantes", "ofendidos", "victimas", "testigos"}:
        data = _normalizar_payload_persona(data)
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
    claims = get_jwt()

    municipio = claims.get("id_municipio")
    if municipio is None:
        municipio = claims.get("IdMunicipio")
    unidad = claims.get("id_unidad")
    if unidad is None:
        unidad = claims.get("IdUnidad")

    if municipio is None or unidad is None:
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

        if perfil:
            if municipio is None:
                municipio = _pick_value(
                    perfil,
                    "ID_MNCPIO",
                    "ID_MUNICIPIO",
                    "id_mncpio",
                    "Id_Mncpio",
                    "MNCPIO",
                    "MUNICIPIO",
                )
            if unidad is None:
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
        return jsonify({
            "msg": "El usuario autenticado no tiene municipio o unidad asociados."
        }), 422

    registros = []
    consulta_exitosa = False
    for sql, params in [
        ("EXEC IPH_ConsultaIPH @IdMunicipio = ?, @IdUnidad = ?", (municipio, unidad)),
        ("EXEC IPH_ConsultaIPH @Municipio = ?, @Unidad = ?", (municipio, unidad)),
    ]:
        try:
            registros = _fetch_all(sql, params, raise_errors=True)
            consulta_exitosa = True
        except Exception:
            current_app.logger.exception("Falló una variante de IPH_ConsultaIPH")
            continue
        if registros:
            break

    if not consulta_exitosa:
        return jsonify({
            "msg": "No fue posible consultar los IPH. Revisa el registro de errores del backend."
        }), 503

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


def _parse_legacy_iph_folio(folio):
    if not folio:
        return None, None
    try:
        partes = str(folio).strip().split("/")
        if len(partes) == 5 and partes[0].isdigit() and partes[3].isdigit() and partes[4].isdigit():
            return int(partes[0]), int(partes[3])
    except Exception:
        return None, None
    return None, None


@iph_bp.post("/")
@jwt_required()
def crear_iph():
    usuario_id = get_jwt_identity()
    payload = request.get_json(silent=True) or {}

    claims = get_jwt()
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

    municipio = (
        payload.get("municipio")
        or payload.get("id_municipio")
        or payload.get("IdMunicipio")
        or (claims.get("id_municipio") if claims else None)
        or (claims.get("IdMunicipio") if claims else None)
    )
    unidad = (
        payload.get("unidad")
        or payload.get("id_unidad")
        or payload.get("IdUnidad")
        or (claims.get("id_unidad") if claims else None)
        or (claims.get("IdUnidad") if claims else None)
    )

    if municipio is None and perfil is not None:
        municipio = _pick_value(perfil, "ID_MNCPIO", "ID_MUNICIPIO", "id_mncpio", "Id_Mncpio", "MNCPIO")
    if unidad is None and perfil is not None:
        unidad = _pick_value(perfil, "Id_Undd", "ID_UNDD", "ID_UNIDAD", "id_unidad", "UNIDAD", "Unidad")

    if municipio is None or unidad is None:
        return jsonify({"msg": "El usuario no tiene municipio o unidad asociada."}), 400

    try:
        municipio = int(municipio)
        unidad = int(unidad)
    except (TypeError, ValueError):
        return jsonify({"msg": "El municipio o la unidad tienen un valor inválido."}), 400

    conn = db.engine.raw_connection()
    cursor = conn.cursor()
    try:
        ultimo = _fetch_one(
            "SELECT TOP 1 IPH FROM IPH WHERE ID_MUNICIPIO_IPH = ? ORDER BY ID_IPH DESC",
            (municipio,),
        )
        ultimo_folio = ultimo.get("IPH") if ultimo else None
        estado_code, ultimo_seq = _parse_legacy_iph_folio(ultimo_folio)
        if estado_code is None:
            estado_code = 28
        if ultimo_seq is None:
            ultimo_seq = 0

        siguiente = ultimo_seq + 1
        folio = f"{estado_code}/{municipio}/{unidad:03d}/{siguiente:05d}/{date.today().year}"

        cursor.execute(
            """
            INSERT INTO IPH (
                ID_MUNICIPIO_IPH,
                IPH,
                IDENTIFICACION,
                ID_ESTADO_IPH,
                FECHA_ESTADO_IPH,
                ID_USUARIO_IPH,
                ACTIVO_IPH,
                ID_FORMA_INICIO,
                FECHA_REGISTRO,
                IPH_MEXICO
            ) VALUES (?, ?, ?, ?, GETDATE(), ?, 1, 1, GETDATE(), ?)
            """,
            (municipio, folio, "", 10, usuario_id, folio),
        )
        conn.commit()
        cursor.execute("SELECT SCOPE_IDENTITY() AS ID_IPH")
        row = cursor.fetchone()
        nuevo_id = row[0] if row else None
        if nuevo_id is None:
            cursor.execute("SELECT MAX(ID_IPH) AS ID_IPH FROM IPH WHERE IPH = ?", (folio,))
            row = cursor.fetchone()
            nuevo_id = row[0] if row else None

        return jsonify({
            "id": nuevo_id,
            "ID_IPH": nuevo_id,
            "folio_interno": folio,
            "IPH": folio,
            "id_carpeta": 0,
            "estado_carpeta": "TRAMITE",
            "msg": "IPH generado correctamente",
        }), 201
    except Exception as exc:
        conn.rollback()
        return jsonify({"msg": "No se pudo generar el IPH en la base de datos principal.", "detalle": str(exc)}), 503
    finally:
        cursor.close()
        conn.close()


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
