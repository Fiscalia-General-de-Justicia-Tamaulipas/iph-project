from datetime import datetime, date, time as dtime
import json
import re
from io import BytesIO
from types import SimpleNamespace

from flask import Blueprint, current_app, request, jsonify, send_file
from werkzeug.exceptions import HTTPException, abort
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from sqlalchemy import inspect
from sqlalchemy.sql.sqltypes import Boolean, Date as SQLDate, DateTime as SQLDateTime, Float, Integer, Numeric, Time as SQLTime
from werkzeug.utils import secure_filename

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
    IPHCaptura,
    IPHEstadoWeb,
    IPHAdjunto,
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


def _fetch_one(sql, params=(), *, raise_errors=False):
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
        current_app.logger.exception("Falló una consulta SQL de lectura")
        if raise_errors:
            raise
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

PANTALLAS_CAPTURA = {
    "puesta_disposicion", "anexo_a", "anexo_b", "anexo_c_complemento",
    "anexo_d", "anexo_e", "anexo_f", "bitacora", "seccion_5_complemento",
}
PANTALLAS_PREVISUALIZABLES = PANTALLAS_CAPTURA | {
    "policias", "conocimiento_hecho", "acta_noticia", "acciones_realizadas",
    "actuaciones", "denunciante", "ofendido", "victima", "imputado", "testigo",
    "inspeccion_lugar", "inspeccion_persona", "inspeccion_vehiculo",
    "inspeccion_vehiculos", "narracion_primer_respondiente",
}
ESTADOS_WEB = {"EN_TRAMITE", "ACTIVA", "TERMINADA", "CANCELADA"}


def _validar_iph_legacy(iph_id):
    registro = _fetch_one("SELECT TOP 1 ID_IPH FROM IPH WHERE ID_IPH = ?", (iph_id,), raise_errors=True)
    if not registro:
        abort(404, description="IPH no encontrado.")
    return registro


def _tabla_web_disponible(modelo):
    """Comprueba explícitamente el objeto dbo requerido por una función web opcional."""
    tabla = modelo.__table__
    disponible = inspect(db.engine).has_table(tabla.name, schema=tabla.schema or "dbo")
    if not disponible:
        current_app.logger.warning(
            "No existe %s.%s; se usará el comportamiento legacy cuando sea posible.",
            tabla.schema or "dbo",
            tabla.name,
        )
    return disponible


def _actualizar_estado_web(iph_id, nuevo_estado="ACTIVA"):
    if not _tabla_web_disponible(IPHEstadoWeb):
        return False
    estado = IPHEstadoWeb.query.filter_by(iph_id=iph_id).first()
    if estado is None:
        estado = IPHEstadoWeb(iph_id=iph_id, estado=nuevo_estado)
        db.session.add(estado)
    elif estado.estado == "EN_TRAMITE" and nuevo_estado == "ACTIVA":
        estado.estado = "ACTIVA"
    elif nuevo_estado != "ACTIVA":
        estado.estado = nuevo_estado
    db.session.flush()
    return True


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
    """Mapea los nombres de API al modelo y convierte valores JSON a tipos SQL."""
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
    columnas = {c.name: c for c in inspect(modelo).columns}
    desconocidos = set(data) - columnas_validas - {"id", "iph_id"}
    if desconocidos:
        raise ValueError("Campos no reconocidos: " + ", ".join(sorted(desconocidos)))
    for campo, valor in data.items():
        if campo not in columnas_validas or campo in ("id", "iph_id"):
            continue
        tipo = columnas[campo].type
        if valor == "" and not isinstance(tipo, (SQLDate, SQLTime, SQLDateTime, Boolean)):
            valor = None
        elif valor == "" and isinstance(tipo, (SQLDate, SQLTime, SQLDateTime)):
            valor = None
        elif isinstance(tipo, SQLDateTime) and isinstance(valor, str):
            valor = datetime.fromisoformat(valor)
        elif isinstance(tipo, SQLDate) and isinstance(valor, str):
            valor = date.fromisoformat(valor)
        elif isinstance(tipo, SQLTime) and isinstance(valor, str):
            valor = dtime.fromisoformat(valor)
        elif isinstance(tipo, Boolean) and not isinstance(valor, bool):
            if valor in (1, "1", "true", "TRUE", "si", "SI", "yes", "YES"):
                valor = True
            elif valor in (0, "0", "false", "FALSE", "no", "NO", None, ""):
                valor = False
            else:
                raise ValueError(f"Valor booleano inválido para {campo}.")
        elif isinstance(tipo, Integer) and valor is not None:
            valor = int(valor)
        elif isinstance(tipo, (Numeric, Float)) and valor is not None:
            valor = float(valor)
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
    ids_iph = [item.get("ID_IPH") or item.get("id") for item in map(_normalize_iph_row, registros)]
    estados_web = {}
    if ids_iph and _tabla_web_disponible(IPHEstadoWeb):
        estados_web = {
            estado.iph_id: estado.estado
            for estado in IPHEstadoWeb.query.filter(IPHEstadoWeb.iph_id.in_(ids_iph)).all()
        }
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
            "ESTADO_CARPETA": estados_web.get(item.get("id")) or item.get("ESTADO_CARPETA") or item.get("estado") or "EN_TRAMITE",
            "estado": estados_web.get(item.get("id")) or item.get("estado") or item.get("ESTADO_CARPETA") or "EN_TRAMITE",
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
            raise_errors=True,
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

        if nuevo_id is None:
            raise RuntimeError("SQL Server no devolvió el ID del IPH creado.")
        if _tabla_web_disponible(IPHEstadoWeb):
            db.session.add(IPHEstadoWeb(iph_id=int(nuevo_id), estado="EN_TRAMITE"))
            db.session.commit()

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
        current_app.logger.error("No fue posible crear el IPH en la base principal (%s).", type(exc).__name__)
        return jsonify({"msg": "No se pudo generar el IPH en la base de datos principal. Verifica la conexión y vuelve a intentarlo."}), 503
    finally:
        cursor.close()
        conn.close()


@iph_bp.get("/<int:iph_id>")
@jwt_required()
def obtener_iph(iph_id):
    try:
        registro = _fetch_one("SELECT TOP 1 * FROM IPH WHERE ID_IPH = ?", (iph_id,), raise_errors=True)
    except Exception as exc:
        current_app.logger.error("No fue posible consultar el IPH solicitado (%s).", type(exc).__name__)
        return jsonify({"msg": "No fue posible consultar el IPH solicitado. Verifica la conexión y vuelve a intentarlo."}), 503

    if not registro:
        return jsonify({"msg": "IPH no encontrado"}), 404

    item = _normalize_iph_row(registro)
    estado_web = (
        IPHEstadoWeb.query.filter_by(iph_id=iph_id).first()
        if _tabla_web_disponible(IPHEstadoWeb)
        else None
    )
    return jsonify({
        "id": item.get("id"),
        "folio_interno": item.get("folio_interno") or item.get("IPH") or "",
        "no_referencia": item.get("NO_REFERENCIA") or item.get("no_referencia"),
        "no_expediente": item.get("no_expediente") or item.get("NUC") or "",
        "estado": estado_web.estado if estado_web else item.get("estado") or "EN_TRAMITE",
        "estado_modulos": {},
    }), 200


# ---------------------------------------------------------------------------
# Módulos de un solo registro (conocimiento_hecho, acta_noticia,
# inspeccion_lugar, narracion_primer_respondiente)
# ---------------------------------------------------------------------------

@iph_bp.get("/<int:iph_id>/<string:modulo>")
@jwt_required()
def obtener_modulo_unico(iph_id, modulo):
    if modulo in {"inspeccion_persona", "inspeccion_vehiculo"}:
        modelo = MODULOS_UNO_A_MUCHOS[modulo]
        instancia = modelo.query.filter_by(iph_id=iph_id).order_by(modelo.id).first()
        return jsonify(modelo_a_dict(instancia) if instancia else None), 200
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
    if modulo in {"inspeccion_persona", "inspeccion_vehiculo"}:
        _validar_iph_legacy(iph_id)
        modelo = MODULOS_UNO_A_MUCHOS[modulo]
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"msg": "El cuerpo debe ser un objeto JSON."}), 400
        try:
            instancia = modelo.query.filter_by(iph_id=iph_id).order_by(modelo.id).first()
            if instancia is None:
                instancia = modelo(iph_id=iph_id)
                db.session.add(instancia)
            asignar_campos(instancia, data, modelo)
            _actualizar_estado_web(iph_id)
            db.session.commit()
            return jsonify(modelo_a_dict(instancia)), 200
        except (TypeError, ValueError) as exc:
            db.session.rollback()
            return jsonify({"msg": str(exc)}), 422
        except Exception:
            db.session.rollback()
            current_app.logger.exception("Error guardando el módulo %s del IPH %s", modulo, iph_id)
            return jsonify({"msg": "No fue posible guardar el módulo en la base de datos."}), 503
    if modulo not in MODULOS_UNO_A_UNO:
        return jsonify({"msg": "Módulo no encontrado"}), 404

    _validar_iph_legacy(iph_id)
    modelo = MODULOS_UNO_A_UNO[modulo]
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"msg": "El cuerpo debe ser un objeto JSON."}), 400

    instancia = modelo.query.filter_by(iph_id=iph_id).first()
    if not instancia:
        instancia = modelo(iph_id=iph_id)
        db.session.add(instancia)

    try:
        asignar_campos(instancia, data, modelo)
        _actualizar_estado_web(iph_id)
        db.session.commit()
    except (TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"msg": str(exc)}), 422
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error guardando el módulo %s del IPH %s", modulo, iph_id)
        return jsonify({"msg": "No fue posible guardar el módulo en la base de datos."}), 503
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

    _validar_iph_legacy(iph_id)
    modelo = MODULOS_UNO_A_MUCHOS[modulo]
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"msg": "El cuerpo debe ser un objeto JSON."}), 400

    instancia = modelo(iph_id=iph_id)
    try:
        asignar_campos(instancia, data, modelo)
        _actualizar_estado_web(iph_id)
        db.session.add(instancia)
        db.session.commit()
    except (TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"msg": str(exc)}), 422
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error creando un registro de %s para IPH %s", modulo, iph_id)
        return jsonify({"msg": "No fue posible guardar el registro en la base de datos."}), 503
    return jsonify(modelo_a_dict(instancia)), 201


@iph_bp.put("/<int:iph_id>/<string:modulo>/lista/<int:item_id>")
@jwt_required()
def actualizar_item_modulo_multiple(iph_id, modulo, item_id):
    if modulo not in MODULOS_UNO_A_MUCHOS:
        return jsonify({"msg": "Módulo no encontrado"}), 404

    modelo = MODULOS_UNO_A_MUCHOS[modulo]
    instancia = modelo.query.filter_by(id=item_id, iph_id=iph_id).first_or_404()
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"msg": "El cuerpo debe ser un objeto JSON."}), 400
    try:
        asignar_campos(instancia, data, modelo)
        _actualizar_estado_web(iph_id)
        db.session.commit()
    except (TypeError, ValueError) as exc:
        db.session.rollback()
        return jsonify({"msg": str(exc)}), 422
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error actualizando un registro de %s para IPH %s", modulo, iph_id)
        return jsonify({"msg": "No fue posible guardar el registro en la base de datos."}), 503
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


@iph_bp.get("/<int:iph_id>/capturas/<string:pantalla>")
@jwt_required()
def obtener_captura_web(iph_id, pantalla):
    if pantalla not in PANTALLAS_CAPTURA:
        return jsonify({"msg": "Pantalla de captura no reconocida."}), 404
    _validar_iph_legacy(iph_id)
    if not _tabla_capturas_disponible():
        return jsonify({"msg": "No se pudo cargar esta pantalla desde el servidor."}), 503
    try:
        captura = IPHCaptura.query.filter_by(iph_id=iph_id, pantalla=pantalla).first()
        return jsonify(json.loads(captura.datos_json) if captura else None), 200
    except Exception:
        current_app.logger.exception("No se pudo cargar la pantalla %s del IPH %s", pantalla, iph_id)
        return jsonify({"msg": "No se pudo cargar esta pantalla desde el servidor."}), 503


def _tabla_capturas_disponible():
    tabla = IPHCaptura.__table__
    url = db.engine.url
    base_datos = url.database
    if not base_datos:
        odbc_connect = url.query.get("odbc_connect", "")
        coincidencia = re.search(r"(?:^|;)DATABASE\s*=\s*([^;]+)", odbc_connect, re.IGNORECASE)
        base_datos = coincidencia.group(1) if coincidencia else "(no especificada en la URI)"
    try:
        disponible = inspect(db.engine).has_table(tabla.name, schema=tabla.schema)
    except Exception:
        current_app.logger.exception(
            "No se pudo comprobar la tabla %s.%s en la base configurada %s",
            tabla.schema,
            tabla.name,
            base_datos,
        )
        return False
    if not disponible:
        current_app.logger.error(
            "Falta la tabla requerida %s.%s en la base configurada %s; "
            "aplique backend/migrations/sqlserver/001_create_iph_capturas_web.sql.",
            tabla.schema,
            tabla.name,
            base_datos,
        )
    return disponible


@iph_bp.put("/<int:iph_id>/capturas/<string:pantalla>")
@jwt_required()
def guardar_captura_web(iph_id, pantalla):
    if pantalla not in PANTALLAS_CAPTURA:
        return jsonify({"msg": "Pantalla de captura no reconocida."}), 404
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({"msg": "El cuerpo debe ser un objeto JSON."}), 400
    try:
        _validar_iph_legacy(iph_id)
        if not _tabla_capturas_disponible():
            return jsonify({"msg": "No se pudo guardar esta pantalla en el servidor."}), 503
        captura = IPHCaptura.query.filter_by(iph_id=iph_id, pantalla=pantalla).first()
        if captura is None:
            captura = IPHCaptura(iph_id=iph_id, pantalla=pantalla)
            db.session.add(captura)
        captura.datos_json = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
        _actualizar_estado_web(iph_id)
        db.session.commit()
        estado = (
            IPHEstadoWeb.query.filter_by(iph_id=iph_id).first()
            if _tabla_web_disponible(IPHEstadoWeb)
            else None
        )
        return jsonify({"pantalla": pantalla, "datos": datos,
                        "estado": estado.estado if estado else None}), 200
    except HTTPException:
        raise
    except Exception:
        db.session.rollback()
        current_app.logger.exception("No se pudo guardar la pantalla %s del IPH %s", pantalla, iph_id)
        return jsonify({"msg": "No se pudo guardar esta pantalla en el servidor."}), 503


@iph_bp.post("/<int:iph_id>/adjuntos")
@jwt_required()
def subir_adjunto(iph_id):
    max_bytes = 50 * 1024 * 1024
    archivo = request.files.get("file")
    anexo = (request.form.get("anexo") or "").strip()
    adjunto_id = (request.form.get("id") or "").strip()
    if archivo is None or not archivo.filename:
        return jsonify({"msg": "Selecciona un archivo para cargar."}), 400
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", adjunto_id):
        return jsonify({"msg": "El identificador del archivo no es válido."}), 400
    if not anexo or len(anexo) > 80:
        return jsonify({"msg": "El anexo asociado no es válido."}), 400
    nombre = secure_filename(archivo.filename)
    extension = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
    tipos_permitidos = {
        "jpg": "image/jpeg", "jpeg": "image/jpeg", "bmp": "image/bmp", "png": "image/png",
        "pdf": "application/pdf", "doc": "application/msword",
        "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "mp3": "audio/mpeg", "wav": "audio/wav", "mp4": "video/mp4",
        "mpeg": "video/mpeg", "mpg": "video/mpeg",
    }
    if extension not in tipos_permitidos:
        return jsonify({"msg": "Tipo de archivo no permitido. Revisa los formatos aceptados por esta pantalla."}), 415
    contenido = archivo.stream.read(max_bytes + 1)
    if not contenido:
        return jsonify({"msg": "El archivo está vacío."}), 400
    if len(contenido) > max_bytes:
        return jsonify({"msg": "El archivo supera el límite de 50 MB."}), 413
    firmas_imagen = {"jpg": contenido.startswith(b"\xff\xd8\xff"), "jpeg": contenido.startswith(b"\xff\xd8\xff"),
                     "bmp": contenido.startswith(b"BM"), "png": contenido.startswith(b"\x89PNG\r\n\x1a\n")}
    if extension in firmas_imagen and not firmas_imagen[extension]:
        return jsonify({"msg": "El contenido no coincide con el tipo de imagen indicado por el archivo."}), 415
    try:
        _validar_iph_legacy(iph_id)
        adjunto = IPHAdjunto.query.filter_by(id=adjunto_id, iph_id=iph_id).first()
        if adjunto is None:
            adjunto = IPHAdjunto(id=adjunto_id, iph_id=iph_id, anexo=anexo, nombre=nombre,
                                  mime_type=tipos_permitidos[extension],
                                  tamano=len(contenido), contenido=contenido)
            db.session.add(adjunto)
        else:
            adjunto.anexo, adjunto.nombre = anexo, nombre
            adjunto.mime_type = tipos_permitidos[extension]
            adjunto.tamano, adjunto.contenido = len(contenido), contenido
        _actualizar_estado_web(iph_id)
        db.session.commit()
        return jsonify({"id": adjunto.id, "iphId": str(iph_id), "anexo": adjunto.anexo,
                        "name": adjunto.nombre, "type": adjunto.mime_type, "size": adjunto.tamano}), 201
    except HTTPException:
        raise
    except Exception:
        db.session.rollback()
        current_app.logger.exception("No se pudo guardar el adjunto del IPH %s", iph_id)
        return jsonify({"msg": "No se pudo guardar el archivo en el servidor."}), 503


@iph_bp.get("/<int:iph_id>/adjuntos")
@jwt_required()
def listar_adjuntos(iph_id):
    _validar_iph_legacy(iph_id)
    query = IPHAdjunto.query.filter_by(iph_id=iph_id)
    anexo = request.args.get("anexo")
    if anexo:
        query = query.filter_by(anexo=anexo)
    return jsonify([{"id": a.id, "iphId": str(iph_id), "anexo": a.anexo,
                     "name": a.nombre, "type": a.mime_type, "size": a.tamano}
                    for a in query.order_by(IPHAdjunto.creado_en).all()]), 200


@iph_bp.get("/<int:iph_id>/adjuntos/<string:adjunto_id>")
@jwt_required()
def descargar_adjunto(iph_id, adjunto_id):
    adjunto = IPHAdjunto.query.filter_by(iph_id=iph_id, id=adjunto_id).first_or_404()
    return send_file(BytesIO(adjunto.contenido), mimetype=adjunto.mime_type,
                     as_attachment=True, download_name=adjunto.nombre)


@iph_bp.delete("/<int:iph_id>/adjuntos/<string:adjunto_id>")
@jwt_required()
def eliminar_adjunto(iph_id, adjunto_id):
    adjunto = IPHAdjunto.query.filter_by(iph_id=iph_id, id=adjunto_id).first_or_404()
    db.session.delete(adjunto)
    db.session.commit()
    return jsonify({"msg": "Archivo eliminado."}), 200


@iph_bp.patch("/<int:iph_id>/estado")
@jwt_required()
def actualizar_estado(iph_id):
    datos = request.get_json(silent=True) or {}
    estado = str(datos.get("estado", "")).strip().upper()
    if estado not in ESTADOS_WEB:
        return jsonify({"msg": "Estado no válido."}), 422
    try:
        _validar_iph_legacy(iph_id)
        if not _tabla_web_disponible(IPHEstadoWeb):
            return jsonify({"msg": "La tabla dbo.iph_estado_web no está instalada; no se puede actualizar el estado."}), 503
        estado_actual = IPHEstadoWeb.query.filter_by(iph_id=iph_id).first()
        if estado == "TERMINADA" and (estado_actual is None or estado_actual.estado != "ACTIVA"):
            return jsonify({"msg": "Solo se puede terminar un IPH que ya está activo."}), 409
        if estado_actual and estado_actual.estado == "TERMINADA" and estado != "TERMINADA":
            return jsonify({"msg": "Un IPH terminado no puede volver a un estado anterior."}), 409
        _actualizar_estado_web(iph_id, estado)
        db.session.commit()
        return jsonify({"id": iph_id, "estado": IPHEstadoWeb.query.get(iph_id).estado}), 200
    except HTTPException:
        raise
    except Exception:
        db.session.rollback()
        current_app.logger.exception("No se pudo actualizar el estado del IPH %s", iph_id)
        return jsonify({"msg": "No se pudo actualizar el estado del IPH."}), 503


# ---------------------------------------------------------------------------
# Exportación a PDF
# ---------------------------------------------------------------------------

def _campos_pdf_validos(datos):
    if not isinstance(datos, dict):
        return None
    campos_validos = {}
    for modulo, campos in datos.items():
        if not isinstance(modulo, str) or len(modulo) > 80 or not isinstance(campos, list) or len(campos) > 200:
            return None
        normalizados = []
        for campo in campos:
            if not isinstance(campo, dict):
                return None
            etiqueta = campo.get("label", "")
            valor = campo.get("value", "")
            if not isinstance(etiqueta, str) or not isinstance(valor, str) or len(etiqueta) > 1000 or len(valor) > 20000:
                return None
            normalizados.append({"label": etiqueta, "value": valor})
        campos_validos[modulo] = normalizados
    return campos_validos


def _capturas_pdf(iph_id):
    if not _tabla_capturas_disponible():
        current_app.logger.warning(
            "Se genera vista previa sin capturas persistidas para el IPH %s; "
            "la tabla dbo.iph_capturas_web aún no está disponible.",
            iph_id,
        )
        return {}
    capturas = {}
    for captura in IPHCaptura.query.filter_by(iph_id=iph_id).all():
        datos = json.loads(captura.datos_json)
        if not isinstance(datos, dict):
            raise ValueError(f"La captura {captura.pantalla} no contiene un objeto JSON.")
        capturas[captura.pantalla] = datos
    return capturas


def _registro_legacy_para_pdf(iph_id):
    fila = _fetch_one(
        "SELECT TOP 1 * FROM IPH WHERE ID_IPH = ?",
        (iph_id,),
        raise_errors=True,
    )
    if fila is None:
        abort(404, description="IPH no encontrado.")

    registro = SimpleNamespace(
        id=iph_id,
        folio_interno=_pick_value(fila, "IPH", "FOLIO_INTERNO", "FOLIO") or "",
        no_referencia=_pick_value(fila, "NO_REFERENCIA", "NUMERO_REFERENCIA"),
        no_expediente=_pick_value(fila, "NO_EXPEDIENTE", "NUC"),
        fecha_puesta_disposicion=_pick_value(
            fila,
            "FECHA_PUESTA_DISPOSICION",
            "FECHA_IPH",
            "FECHA_REGISTRO",
        ),
        hora_puesta_disposicion=_pick_value(fila, "HORA_PUESTA_DISPOSICION", "HORA_IPH"),
        institucion=_pick_value(fila, "INSTITUCION", "INSTITUCION_IPH"),
        adscripcion=_pick_value(fila, "ADSCRIPCION", "UNIDAD", "UNDD_DSCRPCION"),
        cargo=_pick_value(fila, "CARGO", "GRADO", "CARGO_IPH", "PUESTO"),
        estado=_pick_value(fila, "ESTADO", "ESTADO_IPH", "ESTATUS") or "EN_TRAMITE",
        datos_legacy=fila,
        policias=[],
        conocimiento_hecho=None,
        acta_noticia=None,
        inspeccion_lugar=None,
        narracion_primer_respondiente=None,
        denunciantes=[],
        ofendidos=[],
        victimas=[],
        testigos=[],
        imputados=[],
        inspecciones_vehiculo=[],
        acciones_realizadas=[],
        actuaciones=[],
    )
    return registro


def _crear_respuesta_pdf(registro, campos_por_modulo=None, as_attachment=True):
    try:
        documento = generar_pdf_iph(
            registro,
            capturas=_capturas_pdf(registro.id),
            campos_por_modulo=campos_por_modulo,
        )
    except Exception:
        current_app.logger.exception("No se pudo generar el PDF del IPH %s", registro.id)
        return jsonify({"msg": "No se pudo generar el PDF del IPH."}), 500
    return send_file(
        documento,
        as_attachment=as_attachment,
        download_name=f"IPH_{registro.folio_interno}.pdf",
        mimetype="application/pdf",
    )


def _estado_terminado(iph_id):
    if not _tabla_web_disponible(IPHEstadoWeb):
        return False, jsonify({"msg": "No se puede confirmar el estado final del IPH."}), 503
    estado = IPHEstadoWeb.query.filter_by(iph_id=iph_id).first()
    if estado is None or estado.estado != "TERMINADA":
        return False, jsonify({"msg": "El PDF final solo está disponible después de confirmar que el IPH está terminado."}), 409
    return True, None, None


@iph_bp.post("/<int:iph_id>/previsualizar-pdf")
@jwt_required()
def previsualizar_pdf(iph_id):
    try:
        registro = _registro_legacy_para_pdf(iph_id)
    except HTTPException:
        raise
    except Exception:
        current_app.logger.exception("No se pudo leer el IPH %s para la vista previa", iph_id)
        return jsonify({"msg": "No se pudo consultar el IPH para la vista previa."}), 503
    datos = request.get_json(silent=True) or {}
    if not isinstance(datos, dict):
        return jsonify({"msg": "El cuerpo debe contener los campos actuales de la vista previa."}), 400
    campos_por_modulo = _campos_pdf_validos(datos.get("camposPorModulo", {}))
    if campos_por_modulo is None:
        return jsonify({"msg": "Los campos de la vista previa tienen un formato no válido."}), 400
    return _crear_respuesta_pdf(registro, campos_por_modulo, as_attachment=False)


@iph_bp.post("/<int:iph_id>/capturas/<string:pantalla>/previsualizar-pdf")
@jwt_required()
def previsualizar_pdf_pantalla(iph_id, pantalla):
    if pantalla not in PANTALLAS_PREVISUALIZABLES:
        return jsonify({"msg": "Pantalla de captura no reconocida para vista previa."}), 404
    try:
        registro = _registro_legacy_para_pdf(iph_id)
    except HTTPException:
        raise
    except Exception:
        current_app.logger.exception("No se pudo leer el IPH %s para la vista previa", iph_id)
        return jsonify({"msg": "No se pudo consultar el IPH para la vista previa."}), 503
    datos = request.get_json(silent=True) or {}
    if not isinstance(datos, dict):
        return jsonify({"msg": "No se recibieron los datos actuales de la pantalla."}), 400
    campos_por_modulo = _campos_pdf_validos(datos.get("camposPorModulo", {}))
    if campos_por_modulo is None:
        return jsonify({"msg": "Los campos de la vista previa tienen un formato no válido."}), 400
    return _crear_respuesta_pdf(registro, campos_por_modulo, as_attachment=False)


@iph_bp.get("/<int:iph_id>/exportar-pdf")
@jwt_required()
def exportar_pdf(iph_id):
    registro = _registro_legacy_para_pdf(iph_id)
    terminado, respuesta, codigo = _estado_terminado(iph_id)
    if not terminado:
        return respuesta, codigo
    return _crear_respuesta_pdf(registro)


@iph_bp.post("/<int:iph_id>/exportar-pdf")
@jwt_required()
def exportar_pdf_final(iph_id):
    registro = _registro_legacy_para_pdf(iph_id)
    terminado, respuesta, codigo = _estado_terminado(iph_id)
    if not terminado:
        return respuesta, codigo
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({"msg": "El cuerpo debe contener los campos actuales del formulario."}), 400
    campos_por_modulo = _campos_pdf_validos(datos.get("camposPorModulo", {}))
    if campos_por_modulo is None:
        return jsonify({"msg": "Los campos del formulario tienen un formato no válido."}), 400
    return _crear_respuesta_pdf(registro, campos_por_modulo)
