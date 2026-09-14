from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from app.extensions import db

auth_bp = Blueprint("auth", __name__)


def _normalize_user_data(row):
    if not row:
        return {}

    payload = {}
    for key, value in row.items():
        if value is None:
            continue
        payload[str(key).upper()] = value

    user_id = (
        payload.get("ID_USUARIO")
        or payload.get("IDUSUARIO")
        or payload.get("ID")
        or payload.get("id_usuario")
        or payload.get("id")
    )
    if user_id is not None:
        payload["id"] = user_id
        payload["id_usuario"] = user_id

    usuario_name = (
        payload.get("USUARIO")
        or payload.get("USERNAME")
        or payload.get("NOMBRE_USUARIO")
        or payload.get("usuario")
        or payload.get("username")
    )

    nombre_completo = (
        payload.get("NMBRE")
        or payload.get("NOMBRE")
        or payload.get("NOMBRE_COMPLETO")
        or payload.get("nombre_completo")
    )
    if nombre_completo and payload.get("PTRNO"):
        nombre_completo = f"{nombre_completo} {payload.get('PTRNO')}".strip()
    if nombre_completo and payload.get("MTRNO"):
        nombre_completo = f"{nombre_completo} {payload.get('MTRNO')}".strip()

    if not nombre_completo:
        partes = [
            payload.get("NMBRE"),
            payload.get("PTRNO"),
            payload.get("MTRNO"),
        ]
        nombre_completo = " ".join(str(part).strip() for part in partes if part not in (None, "")).strip()

    municipio = (
        payload.get("ID_MNCPIO")
        or payload.get("ID_MUNICIPIO")
        or payload.get("IDMNCPIO")
        or payload.get("id_mncpio")
        or payload.get("id_municipio")
    )
    unidad = (
        payload.get("ID_UNDD")
        or payload.get("ID_UNIDAD")
        or payload.get("Id_Undd")
        or payload.get("id_unidad")
        or payload.get("id_undd")
    )
    puesto = payload.get("PUESTO") or payload.get("puesto") or payload.get("CARGO") or payload.get("cargo") or ""
    adscripcion = (
        payload.get("UNDD_DSCRPCION")
        or payload.get("ADSCRIPCION")
        or payload.get("UNIDAD")
        or payload.get("undd_dscrpcion")
        or payload.get("adscripcion")
        or ""
    )

    payload["usuario"] = usuario_name or payload.get("usuario") or ""
    payload["nombre_completo"] = nombre_completo or payload.get("usuario") or ""
    payload["adscripcion"] = adscripcion
    payload["puesto"] = puesto
    payload["PUESTO"] = puesto
    payload["UNDD_DSCRPCION"] = adscripcion
    payload["IdMunicipio"] = municipio
    payload["id_municipio"] = municipio
    payload["IdUnidad"] = unidad
    payload["id_unidad"] = unidad
    payload["rol"] = payload.get("ROL") or payload.get("rol") or "usuario"
    payload["cargo"] = payload.get("CARGO") or payload.get("cargo") or puesto
    payload["id_modulo"] = payload.get("ID_MODULO") or payload.get("id_modulo")
    payload["id_privilegio"] = payload.get("ID_PRIVILEGIO") or payload.get("id_privilegio")

    return {
        "id": payload.get("id"),
        "id_usuario": payload.get("id_usuario"),
        "usuario": payload.get("usuario"),
        "nombre_completo": payload.get("nombre_completo"),
        "adscripcion": payload.get("adscripcion"),
        "cargo": payload.get("cargo"),
        "puesto": payload.get("puesto"),
        "rol": payload.get("rol"),
        "id_modulo": payload.get("id_modulo"),
        "id_privilegio": payload.get("id_privilegio"),
        "id_municipio": payload.get("id_municipio"),
        "id_unidad": payload.get("id_unidad"),
        "IdMunicipio": payload.get("IdMunicipio"),
        "IdUnidad": payload.get("IdUnidad"),
        "UNDD_DSCRPCION": payload.get("UNDD_DSCRPCION"),
        "PUESTO": payload.get("PUESTO"),
        **{k: v for k, v in payload.items() if k not in {"id", "id_usuario", "usuario", "nombre_completo", "adscripcion", "cargo", "puesto", "rol", "id_modulo", "id_privilegio", "id_municipio", "id_unidad", "IdMunicipio", "IdUnidad", "UNDD_DSCRPCION", "PUESTO"}},
    }


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
    except Exception as exc:
        raise RuntimeError(f"No se pudo conectar a SQL Server: {exc}") from exc
    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None:
            conn.close()


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    usuario_input = (data.get("usuario") or "").strip()
    password = (data.get("password") or "").strip()

    if not usuario_input or not password:
        return jsonify({"msg": "Usuario y contraseña son requeridos"}), 400

    try:
        login_row = _fetch_one(
            "EXEC sp_Cargar_Usuario_Login @USUARIO = ?, @PASSWORD = ?",
            (usuario_input, password),
        )
    except RuntimeError as exc:
        return jsonify({"msg": "No se pudo conectar con la base de datos del sistema principal.", "detalle": str(exc)}), 503

    if login_row:
        usuario = _normalize_user_data(login_row)
        token = create_access_token(identity=str(usuario.get("id_usuario") or usuario.get("id") or usuario_input))
        return jsonify({"access_token": token, "usuario": usuario}), 200

    try:
        fail_row = _fetch_one(
            "EXEC sp_Cargar_Usuario_Login_Fail @USUARIO = ?",
            (usuario_input,),
        )
    except RuntimeError as exc:
        return jsonify({"msg": "No se pudo conectar con la base de datos del sistema principal.", "detalle": str(exc)}), 503

    if fail_row:
        usuario_id = fail_row.get("id_usuario") or fail_row.get("ID_USUARIO")
        if usuario_id in (None, "", 0):
            return jsonify({"msg": "USUARIO INVÁLIDO"}), 401

        intentos = fail_row.get("REINTENTOS") or fail_row.get("reintentos") or 0
        try:
            intentos = int(intentos)
        except (TypeError, ValueError):
            intentos = 0

        if intentos < 10:
            return jsonify({"msg": f"CONTRASEÑA INCORRECTA. LE QUEDA(N) {intentos} INTENTOS MÁS"}), 401
        return jsonify({"msg": "POR SEGURIDAD LA CONTRASEÑA HA SIDO DESACTIVADA POR 10 INTENTOS DE ACCESO FALLIDOS"}), 401

    return jsonify({"msg": "Credenciales inválidas"}), 401


@auth_bp.post("/registro")
def registro():
    return jsonify({"msg": "El registro de usuarios se maneja en la base de datos del sistema principal."}), 405


@auth_bp.get("/perfil")
@jwt_required()
def perfil():
    usuario_id = get_jwt_identity()
    perfil_row = _fetch_one("SELECT TOP 1 * FROM cat_usuario WHERE id_usuario = ?", (usuario_id,))

    if perfil_row:
        return jsonify(_normalize_user_data(perfil_row)), 200

    return jsonify({"id": usuario_id, "usuario": usuario_id}), 200
