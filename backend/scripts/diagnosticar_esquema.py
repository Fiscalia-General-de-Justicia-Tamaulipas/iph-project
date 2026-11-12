"""Compara el metadata SQLAlchemy con SQL Server. Solo lee metadatos; no ejecuta DDL."""

import json
import re

from sqlalchemy import inspect as sa_inspect

from app import create_app
from app.extensions import db
from app.models import iph as _iph_models  # noqa: F401; registra todos los modelos


def tipo_normalizado(tipo):
    return re.sub(r"\s+", " ", str(tipo).lower()).strip()


def diagnosticar(engine):
    inspector = sa_inspect(engine)
    resultado = {"tablas_faltantes": [], "columnas_faltantes": {}, "diferencias": {}}
    for tabla in db.metadata.sorted_tables:
        esquema = tabla.schema or "dbo"
        nombre_completo = f"{esquema}.{tabla.name}"
        if not inspector.has_table(tabla.name, schema=esquema):
            resultado["tablas_faltantes"].append(nombre_completo)
            resultado["columnas_faltantes"][nombre_completo] = [c.name for c in tabla.columns]
            continue

        existentes = {c["name"]: c for c in inspector.get_columns(tabla.name, schema=esquema)}
        faltantes, diferencias = [], []
        for columna in tabla.columns:
            actual = existentes.get(columna.name)
            if actual is None:
                faltantes.append(columna.name)
                continue
            esperado_tipo = tipo_normalizado(columna.type)
            actual_tipo = tipo_normalizado(actual["type"])
            if esperado_tipo != actual_tipo:
                diferencias.append({"columna": columna.name, "tipo_modelo": esperado_tipo, "tipo_bd": actual_tipo})
            esperado_nullable = bool(columna.nullable)
            actual_nullable = bool(actual.get("nullable", True))
            if esperado_nullable != actual_nullable:
                diferencias.append({"columna": columna.name, "nullable_modelo": esperado_nullable, "nullable_bd": actual_nullable})
        if faltantes:
            resultado["columnas_faltantes"][nombre_completo] = faltantes
        if diferencias:
            resultado["diferencias"][nombre_completo] = diferencias
    return resultado


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        print(json.dumps(diagnosticar(db.engine), ensure_ascii=False, indent=2))
