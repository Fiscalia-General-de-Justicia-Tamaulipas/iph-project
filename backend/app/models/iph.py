"""
Modelos de datos para el Informe Policial Homologado (IPH).

IMPORTANTE: la base de datos SQL Server YA EXISTE en otro servidor.
Estos modelos son la propuesta de estructura para los módulos mostrados
en el panel (Conocimiento de Hecho, Acta de Noticia, Acciones Realizadas,
Denunciante, Ofendido, Víctima, Policías, Imputado, Testigo, Inspección de
Lugar, Inspección de Persona, Inspección de Vehículos, Narración del Primer
Respondiente, Actuaciones).

AJUSTA nombres de tabla (__tablename__) y columnas para que coincidan
exactamente con el esquema real ya existente en el servidor SQL Server.
Si el esquema real difiere, este archivo es el único lugar que necesitas
modificar (los blueprints ya consumen estos modelos mediante los servicios).
"""

from datetime import datetime
from app.extensions import db


ESTADOS_MODULO = ("PENDIENTE", "EN_PROCESO", "COMPLETADO")
ESTADOS_IPH = ("EN_TRAMITE", "ACTIVA", "CERRADA", "CANCELADA")


class IPH(db.Model):
    """Registro principal del Informe Policial Homologado (folio)."""
    __tablename__ = "iph"

    id = db.Column(db.Integer, primary_key=True)
    folio_interno = db.Column(db.String(50), unique=True, nullable=False)
    no_referencia = db.Column(db.String(50))       # EDO-INST-GOB-MPIO-DD-MM-AAAA-HH-MM
    no_expediente = db.Column(db.String(80))
    fecha_puesta_disposicion = db.Column(db.Date)
    hora_puesta_disposicion = db.Column(db.Time)

    institucion = db.Column(db.String(150))        # ej. "Policía Investigadora"
    adscripcion = db.Column(db.String(200))         # ej. "Segunda Unidad General de Investigación en Victoria"
    estado = db.Column(db.String(20), default="EN_TRAMITE")

    usuario_creador_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # --- Relaciones uno-a-uno (un solo apartado por IPH) ---
    conocimiento_hecho = db.relationship("ConocimientoHecho", uselist=False, back_populates="iph", cascade="all, delete-orphan")
    acta_noticia = db.relationship("ActaNoticia", uselist=False, back_populates="iph", cascade="all, delete-orphan")
    inspeccion_lugar = db.relationship("InspeccionLugar", uselist=False, back_populates="iph", cascade="all, delete-orphan")
    narracion_primer_respondiente = db.relationship("NarracionPrimerRespondiente", uselist=False, back_populates="iph", cascade="all, delete-orphan")

    # --- Relaciones uno-a-muchos (varios registros posibles por IPH) ---
    acciones_realizadas = db.relationship("AccionRealizada", back_populates="iph", cascade="all, delete-orphan")
    denunciantes = db.relationship("Denunciante", back_populates="iph", cascade="all, delete-orphan")
    ofendidos = db.relationship("Ofendido", back_populates="iph", cascade="all, delete-orphan")
    victimas = db.relationship("Victima", back_populates="iph", cascade="all, delete-orphan")
    policias = db.relationship("PolicíaActuante", back_populates="iph", cascade="all, delete-orphan")
    imputados = db.relationship("Imputado", back_populates="iph", cascade="all, delete-orphan")
    testigos = db.relationship("Testigo", back_populates="iph", cascade="all, delete-orphan")
    inspecciones_persona = db.relationship("InspeccionPersona", back_populates="iph", cascade="all, delete-orphan")
    inspecciones_vehiculo = db.relationship("InspeccionVehiculo", back_populates="iph", cascade="all, delete-orphan")
    actuaciones = db.relationship("Actuacion", back_populates="iph", cascade="all, delete-orphan")

    def estado_modulos(self):
        """Devuelve el estado (PENDIENTE/COMPLETADO) de cada tarjeta del panel."""
        return {
            "conocimiento_hecho": bool(self.conocimiento_hecho),
            "acta_noticia": bool(self.acta_noticia),
            "acciones_realizadas": len(self.acciones_realizadas) > 0,
            "denunciante": len(self.denunciantes) > 0,
            "ofendido": len(self.ofendidos) > 0,
            "victima": len(self.victimas) > 0,
            "policias": len(self.policias) > 0,
            "imputado": len(self.imputados) > 0,
            "testigo": len(self.testigos) > 0,
            "inspeccion_lugar": bool(self.inspeccion_lugar),
            "inspeccion_persona": len(self.inspecciones_persona) > 0,
            "inspeccion_vehiculos": len(self.inspecciones_vehiculo) > 0,
            "narracion_primer_respondiente": bool(self.narracion_primer_respondiente),
            "actuaciones": len(self.actuaciones) > 0,
        }


class ConocimientoHecho(db.Model):
    """Sección 3: Conocimiento del hecho y seguimiento de la actuación."""
    __tablename__ = "conocimiento_hecho"

    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)

    como_se_entero = db.Column(db.String(30))  # denuncia, flagrancia, localizacion, mandamiento_judicial, llamada_emergencia, descubrimiento, aportacion
    numero_911 = db.Column(db.String(20))

    fecha_conocimiento = db.Column(db.Date)
    hora_conocimiento = db.Column(db.Time)
    fecha_arribo = db.Column(db.Date)
    hora_arribo = db.Column(db.Time)

    iph = db.relationship("IPH", back_populates="conocimiento_hecho")


class ActaNoticia(db.Model):
    """Acta de noticia del hecho + Sección 4 (lugar de la intervención)."""
    __tablename__ = "acta_noticia"

    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)

    contenido = db.Column(db.Text)

    calle_tramo = db.Column(db.String(200))
    no_exterior = db.Column(db.String(20))
    no_interior = db.Column(db.String(20))
    codigo_postal = db.Column(db.String(10))
    colonia_localidad = db.Column(db.String(150))
    municipio = db.Column(db.String(100))
    entidad_federativa = db.Column(db.String(100))
    referencias = db.Column(db.Text)
    latitud = db.Column(db.Numeric(10, 6))
    longitud = db.Column(db.Numeric(10, 6))

    iph = db.relationship("IPH", back_populates="acta_noticia")


class AccionRealizada(db.Model):
    """Bitácora de acciones realizadas durante la intervención."""
    __tablename__ = "acciones_realizadas"

    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)

    orden = db.Column(db.Integer, default=1)
    descripcion = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.Date)
    hora = db.Column(db.Time)

    iph = db.relationship("IPH", back_populates="acciones_realizadas")


class _PersonaBase:
    """Mixin con campos comunes de identidad usados por Denunciante/Ofendido/Víctima/Testigo."""
    primer_apellido = db.Column(db.String(100))
    segundo_apellido = db.Column(db.String(100))
    nombres = db.Column(db.String(150))
    sexo = db.Column(db.String(10))
    nacionalidad = db.Column(db.String(20))     # mexicana / extranjera
    fecha_nacimiento = db.Column(db.Date)
    edad = db.Column(db.Integer)
    tipo_documento = db.Column(db.String(30))   # credencial_ine / licencia / pasaporte / otro
    no_identificacion = db.Column(db.String(50))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(150))

    calle_tramo = db.Column(db.String(200))
    no_exterior = db.Column(db.String(20))
    no_interior = db.Column(db.String(20))
    codigo_postal = db.Column(db.String(10))
    colonia_localidad = db.Column(db.String(150))
    municipio = db.Column(db.String(100))
    entidad_federativa = db.Column(db.String(100))
    referencias = db.Column(db.Text)


class Denunciante(db.Model, _PersonaBase):
    __tablename__ = "denunciantes"
    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)
    relato = db.Column(db.Text)
    iph = db.relationship("IPH", back_populates="denunciantes")


class Ofendido(db.Model, _PersonaBase):
    __tablename__ = "ofendidos"
    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)
    relato = db.Column(db.Text)
    iph = db.relationship("IPH", back_populates="ofendidos")


class Victima(db.Model, _PersonaBase):
    __tablename__ = "victimas"
    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)
    lesiones_visibles = db.Column(db.Boolean, default=False)
    grupo_vulnerable = db.Column(db.Boolean, default=False)
    cual_grupo_vulnerable = db.Column(db.String(150))
    relato = db.Column(db.Text)
    iph = db.relationship("IPH", back_populates="victimas")


class PolicíaActuante(db.Model):
    """Sección 2: Primer respondiente / Policías que participaron."""
    __tablename__ = "policias_actuantes"

    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)

    primer_apellido = db.Column(db.String(100))
    segundo_apellido = db.Column(db.String(100))
    nombres = db.Column(db.String(150))
    institucion = db.Column(db.String(50))  # guardia_nacional, policia_federal_ministerial, policia_ministerial, policia_mando_unico, policia_estatal, policia_municipal, otra
    institucion_otra = db.Column(db.String(150))
    grado_cargo = db.Column(db.String(100))
    unidad_arribo = db.Column(db.String(100))
    es_primer_respondiente = db.Column(db.Boolean, default=False)

    iph = db.relationship("IPH", back_populates="policias")


class Imputado(db.Model):
    """Anexo A: Detención(es). Un registro por persona detenida."""
    __tablename__ = "imputados"

    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)

    numero_detencion_rnd = db.Column(db.String(20))
    primer_apellido = db.Column(db.String(100))
    segundo_apellido = db.Column(db.String(100))
    nombres = db.Column(db.String(150))
    apodo_alias = db.Column(db.String(100))
    nacionalidad = db.Column(db.String(20))
    sexo = db.Column(db.String(10))
    fecha_nacimiento = db.Column(db.Date)
    edad = db.Column(db.Integer)
    tipo_documento = db.Column(db.String(30))
    no_identificacion = db.Column(db.String(50))
    telefono = db.Column(db.String(20))

    calle_tramo = db.Column(db.String(200))
    no_exterior = db.Column(db.String(20))
    no_interior = db.Column(db.String(20))
    codigo_postal = db.Column(db.String(10))
    colonia_localidad = db.Column(db.String(150))
    municipio = db.Column(db.String(100))
    entidad_federativa = db.Column(db.String(100))
    referencias = db.Column(db.Text)

    lesiones_visibles = db.Column(db.Boolean, default=False)
    padecimiento = db.Column(db.Boolean, default=False)
    cual_padecimiento = db.Column(db.String(200))
    grupo_vulnerable = db.Column(db.Boolean, default=False)
    cual_grupo_vulnerable = db.Column(db.String(150))
    grupo_delictivo = db.Column(db.Boolean, default=False)
    cual_grupo_delictivo = db.Column(db.String(150))

    descripcion_fisica = db.Column(db.Text)
    fecha_detencion = db.Column(db.Date)
    hora_detencion = db.Column(db.Time)
    informado_derechos = db.Column(db.Boolean, default=False)

    iph = db.relationship("IPH", back_populates="imputados")


class Testigo(db.Model, _PersonaBase):
    __tablename__ = "testigos"
    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)
    relato = db.Column(db.Text)
    iph = db.relationship("IPH", back_populates="testigos")


class InspeccionLugar(db.Model):
    """Apartado 4.2: Inspección del lugar."""
    __tablename__ = "inspecciones_lugar"

    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)

    realizo_inspeccion = db.Column(db.Boolean, default=False)
    encontro_objeto = db.Column(db.Boolean, default=False)
    preservo_lugar = db.Column(db.Boolean, default=False)
    realizo_priorizacion = db.Column(db.Boolean, default=False)
    tipo_riesgo = db.Column(db.String(20))   # sociales / naturales
    especifique_riesgo = db.Column(db.Text)
    croquis_imagen_url = db.Column(db.String(300))

    iph = db.relationship("IPH", back_populates="inspeccion_lugar")


class InspeccionPersona(db.Model):
    """Apartado A.5: Inspección a la persona detenida."""
    __tablename__ = "inspecciones_persona"

    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)
    imputado_id = db.Column(db.Integer, db.ForeignKey("imputados.id"))

    encontro_objeto = db.Column(db.Boolean, default=False)
    recolecto_pertenencias = db.Column(db.Boolean, default=False)
    descripcion = db.Column(db.Text)

    iph = db.relationship("IPH", back_populates="inspecciones_persona")
    imputado = db.relationship("Imputado")


class InspeccionVehiculo(db.Model):
    """Anexo C: Inspección de vehículo. Uno por cada vehículo inspeccionado."""
    __tablename__ = "inspecciones_vehiculo"

    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)

    tipo = db.Column(db.String(20))          # terrestre / acuatico / aereo
    procedencia = db.Column(db.String(20))   # nacional / extranjero
    uso = db.Column(db.String(30))           # particular / transporte_publico / carga
    marca = db.Column(db.String(100))
    submarca = db.Column(db.String(100))
    modelo = db.Column(db.String(20))
    color = db.Column(db.String(50))
    placa_matricula = db.Column(db.String(30))
    no_serie = db.Column(db.String(50))
    situacion = db.Column(db.String(30))     # con_reporte_robo / sin_reporte_robo / no_es_posible_saberlo
    encontro_objetos = db.Column(db.Boolean, default=False)
    observaciones = db.Column(db.Text)
    fecha_inspeccion = db.Column(db.Date)
    hora_inspeccion = db.Column(db.Time)

    iph = db.relationship("IPH", back_populates="inspecciones_vehiculo")


class NarracionPrimerRespondiente(db.Model):
    """Sección 5: Narrativa de los hechos y actuación de la autoridad."""
    __tablename__ = "narracion_primer_respondiente"

    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)

    narrativa = db.Column(db.Text, nullable=False)
    continua_en_anexo_g = db.Column(db.Boolean, default=False)

    iph = db.relationship("IPH", back_populates="narracion_primer_respondiente")


class Actuacion(db.Model):
    """Módulo genérico de actuaciones adicionales realizadas."""
    __tablename__ = "actuaciones"

    id = db.Column(db.Integer, primary_key=True)
    iph_id = db.Column(db.Integer, db.ForeignKey("iph.id"), nullable=False)

    tipo_actuacion = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    responsable = db.Column(db.String(150))
    fecha = db.Column(db.Date)
    hora = db.Column(db.Time)

    iph = db.relationship("IPH", back_populates="actuaciones")
