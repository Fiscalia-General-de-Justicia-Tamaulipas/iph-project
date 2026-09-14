"""
Generador de PDF del Informe Policial Homologado (IPH).

Enfoque actual: se construye un PDF nuevo con reportlab que reproduce la
estructura y el orden de las secciones del formato oficial IPH2019
(SESNSP/CNSP), a partir de los datos capturados en el formulario.

Alternativa a futuro: si el PDF oficial (IPH-DELITOS.pdf) cuenta con
campos de formulario (AcroForm) reales, se puede usar pypdf para RELLENAR
directamente esa plantilla en vez de generar el documento desde cero.
Este archivo es el único punto que habría que tocar para ese cambio,
ya que el resto del proyecto solo llama a generar_pdf_iph(iph).
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from app.config import Config

styles = getSampleStyleSheet()
estilo_titulo_seccion = ParagraphStyle(
    "TituloSeccion",
    parent=styles["Heading2"],
    textColor=colors.white,
    backColor=colors.HexColor("#4b4b3f"),
    borderPadding=6,
    spaceAfter=8,
)
estilo_texto = styles["BodyText"]


def _fmt(valor):
    if valor is None:
        return "—"
    return str(valor)


def _tabla_pares(pares, col_widths=(6 * cm, 10 * cm)):
    """Genera una tabla simple de 'Etiqueta: valor' a partir de una lista de tuplas."""
    data = [[Paragraph(f"<b>{etiqueta}</b>", estilo_texto), Paragraph(_fmt(valor), estilo_texto)] for etiqueta, valor in pares]
    tabla = Table(data, colWidths=list(col_widths))
    tabla.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f2f2ee")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tabla


def generar_pdf_iph(iph):
    """
    Recibe una instancia del modelo IPH (con sus relaciones ya cargadas
    por SQLAlchemy) y genera un PDF en PDF_OUTPUT_DIR. Devuelve la ruta
    del archivo generado.
    """
    os.makedirs(Config.PDF_OUTPUT_DIR, exist_ok=True)
    ruta_salida = os.path.join(Config.PDF_OUTPUT_DIR, f"IPH_{iph.folio_interno}.pdf")

    doc = SimpleDocTemplate(
        ruta_salida,
        pagesize=letter,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
    )

    elementos = []

    elementos.append(Paragraph("INFORME POLICIAL HOMOLOGADO (IPH)", styles["Title"]))
    elementos.append(Paragraph(f"Folio interno: {iph.folio_interno}", styles["Heading3"]))
    elementos.append(Spacer(1, 12))

    # Sección 1: Puesta a disposición
    elementos.append(Paragraph("SECCIÓN 1. PUESTA A DISPOSICIÓN", estilo_titulo_seccion))
    elementos.append(_tabla_pares([
        ("No. de expediente", iph.no_expediente),
        ("No. de referencia", iph.no_referencia),
        ("Fecha", iph.fecha_puesta_disposicion),
        ("Hora", iph.hora_puesta_disposicion),
        ("Institución", iph.institucion),
        ("Adscripción", iph.adscripcion),
        ("Estado del IPH", iph.estado),
    ]))
    elementos.append(Spacer(1, 14))

    # Sección 2: Primer respondiente / Policías
    elementos.append(Paragraph("SECCIÓN 2. PRIMER RESPONDIENTE / POLICÍAS ACTUANTES", estilo_titulo_seccion))
    if iph.policias:
        for p in iph.policias:
            elementos.append(_tabla_pares([
                ("Nombre completo", f"{p.primer_apellido or ''} {p.segundo_apellido or ''} {p.nombres or ''}".strip()),
                ("Institución", p.institucion_otra if p.institucion == "otra" else p.institucion),
                ("Grado/Cargo", p.grado_cargo),
                ("Unidad de arribo", p.unidad_arribo),
                ("¿Primer respondiente?", "Sí" if p.es_primer_respondiente else "No"),
            ]))
            elementos.append(Spacer(1, 8))
    else:
        elementos.append(Paragraph("Sin policías capturados.", estilo_texto))
    elementos.append(Spacer(1, 10))

    # Sección 3: Conocimiento del hecho
    elementos.append(Paragraph("SECCIÓN 3. CONOCIMIENTO DEL HECHO", estilo_titulo_seccion))
    ch = iph.conocimiento_hecho
    if ch:
        elementos.append(_tabla_pares([
            ("¿Cómo se enteró?", ch.como_se_entero),
            ("No. 911", ch.numero_911),
            ("Fecha de conocimiento", ch.fecha_conocimiento),
            ("Hora de conocimiento", ch.hora_conocimiento),
            ("Fecha de arribo", ch.fecha_arribo),
            ("Hora de arribo", ch.hora_arribo),
        ]))
    else:
        elementos.append(Paragraph("Sin información capturada.", estilo_texto))
    elementos.append(Spacer(1, 14))

    # Sección 4: Lugar de la intervención + Acta de noticia
    elementos.append(Paragraph("SECCIÓN 4. LUGAR DE LA INTERVENCIÓN", estilo_titulo_seccion))
    an = iph.acta_noticia
    if an:
        elementos.append(_tabla_pares([
            ("Calle/Tramo carretero", an.calle_tramo),
            ("No. exterior / interior", f"{_fmt(an.no_exterior)} / {_fmt(an.no_interior)}"),
            ("Código postal", an.codigo_postal),
            ("Colonia/Localidad", an.colonia_localidad),
            ("Municipio", an.municipio),
            ("Entidad federativa", an.entidad_federativa),
            ("Referencias", an.referencias),
            ("Latitud / Longitud", f"{_fmt(an.latitud)} / {_fmt(an.longitud)}"),
        ]))
        elementos.append(Spacer(1, 8))
        elementos.append(Paragraph("<b>Acta de noticia del hecho:</b>", estilo_texto))
        elementos.append(Paragraph(_fmt(an.contenido), estilo_texto))
    else:
        elementos.append(Paragraph("Sin información capturada.", estilo_texto))
    elementos.append(Spacer(1, 8))

    il = iph.inspeccion_lugar
    if il:
        elementos.append(Paragraph("Apartado 4.2 Inspección del lugar", styles["Heading4"]))
        elementos.append(_tabla_pares([
            ("¿Realizó la inspección?", "Sí" if il.realizo_inspeccion else "No"),
            ("¿Encontró algún objeto?", "Sí" if il.encontro_objeto else "No"),
            ("¿Preservó el lugar?", "Sí" if il.preservo_lugar else "No"),
            ("¿Priorización?", "Sí" if il.realizo_priorizacion else "No"),
            ("Tipo de riesgo", il.tipo_riesgo),
            ("Especifique", il.especifique_riesgo),
        ]))
    elementos.append(Spacer(1, 14))

    # Denunciante / Ofendido / Víctima / Testigos
    def _bloque_personas(titulo, lista):
        elementos.append(Paragraph(titulo, estilo_titulo_seccion))
        if not lista:
            elementos.append(Paragraph("Ninguno capturado.", estilo_texto))
            return
        for persona in lista:
            elementos.append(_tabla_pares([
                ("Nombre completo", f"{persona.primer_apellido or ''} {persona.segundo_apellido or ''} {persona.nombres or ''}".strip()),
                ("Sexo", persona.sexo),
                ("Nacionalidad", persona.nacionalidad),
                ("Edad", persona.edad),
                ("Teléfono", persona.telefono),
                ("Domicilio", f"{_fmt(persona.calle_tramo)}, {_fmt(persona.colonia_localidad)}, {_fmt(persona.municipio)}, {_fmt(persona.entidad_federativa)}"),
            ]))
            elementos.append(Spacer(1, 6))
        elementos.append(Spacer(1, 8))

    _bloque_personas("DENUNCIANTE(S)", iph.denunciantes)
    _bloque_personas("OFENDIDO(S)", iph.ofendidos)
    _bloque_personas("VÍCTIMA(S)", iph.victimas)
    _bloque_personas("TESTIGO(S)", iph.testigos)

    # Imputados (Anexo A)
    elementos.append(Paragraph("ANEXO A. PERSONA(S) DETENIDA(S) / IMPUTADO(S)", estilo_titulo_seccion))
    if iph.imputados:
        for imp in iph.imputados:
            elementos.append(_tabla_pares([
                ("RND", imp.numero_detencion_rnd),
                ("Nombre completo", f"{imp.primer_apellido or ''} {imp.segundo_apellido or ''} {imp.nombres or ''}".strip()),
                ("Apodo/Alias", imp.apodo_alias),
                ("Sexo", imp.sexo),
                ("Nacionalidad", imp.nacionalidad),
                ("Edad", imp.edad),
                ("Fecha/Hora detención", f"{_fmt(imp.fecha_detencion)} {_fmt(imp.hora_detencion)}"),
                ("Lesiones visibles", "Sí" if imp.lesiones_visibles else "No"),
                ("Grupo vulnerable", imp.cual_grupo_vulnerable if imp.grupo_vulnerable else "No"),
                ("Grupo delictivo", imp.cual_grupo_delictivo if imp.grupo_delictivo else "No"),
                ("Se le informaron sus derechos", "Sí" if imp.informado_derechos else "No"),
                ("Descripción física", imp.descripcion_fisica),
            ]))
            elementos.append(Spacer(1, 8))
    else:
        elementos.append(Paragraph("Sin personas detenidas registradas.", estilo_texto))
    elementos.append(Spacer(1, 14))

    # Inspección de vehículos (Anexo C)
    elementos.append(Paragraph("ANEXO C. INSPECCIÓN DE VEHÍCULO(S)", estilo_titulo_seccion))
    if iph.inspecciones_vehiculo:
        for veh in iph.inspecciones_vehiculo:
            elementos.append(_tabla_pares([
                ("Tipo", veh.tipo),
                ("Marca/Submarca/Modelo", f"{_fmt(veh.marca)} / {_fmt(veh.submarca)} / {_fmt(veh.modelo)}"),
                ("Color", veh.color),
                ("Placa/Matrícula", veh.placa_matricula),
                ("No. de serie", veh.no_serie),
                ("Situación", veh.situacion),
                ("Observaciones", veh.observaciones),
            ]))
            elementos.append(Spacer(1, 8))
    else:
        elementos.append(Paragraph("Sin vehículos inspeccionados.", estilo_texto))
    elementos.append(Spacer(1, 14))

    # Acciones realizadas
    elementos.append(Paragraph("ACCIONES REALIZADAS", estilo_titulo_seccion))
    if iph.acciones_realizadas:
        for accion in sorted(iph.acciones_realizadas, key=lambda a: a.orden or 0):
            elementos.append(Paragraph(f"• {_fmt(accion.fecha)} {_fmt(accion.hora)} — {_fmt(accion.descripcion)}", estilo_texto))
    else:
        elementos.append(Paragraph("Sin acciones registradas.", estilo_texto))
    elementos.append(Spacer(1, 14))

    # Actuaciones
    elementos.append(Paragraph("ACTUACIONES", estilo_titulo_seccion))
    if iph.actuaciones:
        for act in iph.actuaciones:
            elementos.append(Paragraph(
                f"• [{_fmt(act.tipo_actuacion)}] {_fmt(act.fecha)} {_fmt(act.hora)} — {_fmt(act.descripcion)} (Responsable: {_fmt(act.responsable)})",
                estilo_texto,
            ))
    else:
        elementos.append(Paragraph("Sin actuaciones registradas.", estilo_texto))
    elementos.append(PageBreak())

    # Sección 5: Narrativa
    elementos.append(Paragraph("SECCIÓN 5. NARRATIVA DE LOS HECHOS", estilo_titulo_seccion))
    narr = iph.narracion_primer_respondiente
    if narr:
        elementos.append(Paragraph(_fmt(narr.narrativa), estilo_texto))
    else:
        elementos.append(Paragraph("Sin narrativa capturada.", estilo_texto))

    doc.build(elementos)
    return ruta_salida
