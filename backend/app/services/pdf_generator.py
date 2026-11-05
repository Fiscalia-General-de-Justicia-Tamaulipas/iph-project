"""Rellena la plantilla oficial IPH2019 sin reconstruir su diseño."""

from datetime import date, datetime, time
from io import BytesIO
from pathlib import Path
import re
import unicodedata
from copy import deepcopy

from pypdf import PdfReader, PdfWriter
from reportlab.lib.utils import simpleSplit
from reportlab.pdfgen import canvas


PLANTILLA_IPH = Path(__file__).resolve().parents[1] / "assets" / "iph-delitos.pdf"
FUENTE = "Helvetica"
TAMANO_FUENTE = 7
INTERLINEADO = 9

# Página (índice PDF), x, línea inicial, ancho, línea final. El contenido
# secundario se imprime en los espacios de escritura de la sección respectiva.
ZONAS_MODULO = {
    "puesta_disposicion": [(0, 38, 198, 532, 153)],
    "policias": [(1, 38, 613, 532, 550)],
    "conocimiento_hecho": [(1, 38, 493, 532, 450)],
    "acta_noticia": [(1, 38, 288, 532, 205)],
    "inspeccion_lugar": [(2, 38, 226, 532, 158)],
    "narracion_primer_respondiente": [(3, 38, 695, 532, 205)],
    "anexo_a": [(4, 38, 391, 532, 296), (5, 38, 520, 532, 458), (6, 38, 682, 532, 613)],
    "anexo_b": [(7, 38, 650, 532, 420)],
    "anexo_c": [(8, 38, 510, 532, 465), (8, 38, 290, 532, 250)],
    "inspeccion_vehiculo": [(8, 38, 510, 532, 465), (8, 38, 290, 532, 250)],
    "anexo_d": [(9, 38, 608, 532, 570), (10, 38, 731, 532, 689), (10, 38, 337, 532, 315)],
    "anexo_e": [(11, 38, 423, 532, 96), (12, 38, 650, 532, 604)],
    "anexo_f": [(13, 38, 704, 532, 590), (13, 38, 315, 532, 240)],
    "bitacora": [(14, 38, 708, 532, 68)],
    "seccion_5_complemento": [(14, 38, 708, 532, 68)],
}

def _normalizar(texto):
    texto = unicodedata.normalize("NFKD", str(texto or ""))
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return re.sub(r"[^a-z0-9]+", " ", texto.lower()).strip()


def _formatear(valor):
    if valor is None:
        return ""
    if isinstance(valor, datetime):
        return valor.strftime("%d/%m/%Y %H:%M")
    if isinstance(valor, date):
        return valor.strftime("%d/%m/%Y")
    if isinstance(valor, time):
        return valor.strftime("%H:%M")
    if isinstance(valor, bool):
        return "X" if valor else ""
    texto = str(valor).replace("\r", " ").replace("\x00", "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
        return datetime.strptime(texto, "%Y-%m-%d").strftime("%d/%m/%Y")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?", texto):
        formato = "%Y-%m-%dT%H:%M:%S" if "T" in texto and texto.count(":") == 2 else (
            "%Y-%m-%d %H:%M:%S" if texto.count(":") == 2 else
            "%Y-%m-%dT%H:%M" if "T" in texto else "%Y-%m-%d %H:%M"
        )
        return datetime.strptime(texto, formato).strftime("%d/%m/%Y %H:%M")
    return texto


def _texto_seguro(valor):
    return valor.encode("cp1252", "replace").decode("cp1252")


def _captura_a_campos(datos, prefijo=""):
    campos = []
    if isinstance(datos, dict):
        for clave, valor in datos.items():
            etiqueta = f"{prefijo} / {clave}" if prefijo else str(clave)
            campos.extend(_captura_a_campos(valor, etiqueta))
    elif isinstance(datos, list):
        for indice, valor in enumerate(datos, 1):
            campos.extend(_captura_a_campos(valor, f"{prefijo} {indice}".strip()))
    elif datos not in (None, ""):
        campos.append({"label": prefijo, "value": _formatear(datos)})
    return campos


def _campos_por_modulo(capturas, campos_actuales):
    resultado = {}
    modulos = set(capturas or {}) | set(campos_actuales or {})
    for modulo in modulos:
        actuales = (campos_actuales or {}).get(modulo)
        fuente = actuales if isinstance(actuales, list) and actuales else _captura_a_campos(
            (capturas or {}).get(modulo, {})
        )
        campos = []
        for campo in fuente:
            if not isinstance(campo, dict):
                continue
            etiqueta = _formatear(campo.get("label"))
            valor = _formatear(campo.get("value"))
            if valor:
                campos.append({"label": etiqueta, "value": valor})
        if campos:
            resultado[modulo] = campos
    return resultado


def _valor_de(campo):
    return _texto_seguro(_formatear(campo.get("value")))


def _dibujar_texto(canvas_pdf, texto, x, y, ancho, tamano=TAMANO_FUENTE):
    texto = _texto_seguro(texto)
    lineas = simpleSplit(texto, FUENTE, tamano, ancho)
    canvas_pdf.setFont(FUENTE, tamano)
    for linea in lineas:
        canvas_pdf.drawString(x, y, linea)
        y -= INTERLINEADO
    return y


def _ancla_directa(modulo, etiqueta, ocurrencias):
    clave = _normalizar(etiqueta)
    if modulo == "puesta_disposicion":
        if "fecha" in clave:
            return (0, 77, 591, 110, 7)
        if "hora" in clave:
            return (0, 244, 591, 48, 7)
        if "expediente" in clave:
            return (0, 445, 591, 130, 7)
        if "folio" in clave:
            return (0, 356, 681, 195, 7)
        if "cantidad" in clave and "anexo a" in clave:
            return (0, 210, 553, 36, 6)
        if "cantidad" in clave and "anexo c" in clave:
            return (0, 210, 518, 36, 6)
        if "cantidad" in clave and "arma" in clave:
            return (0, 210, 505, 28, 6)
        if "cantidad" in clave and "objeto" in clave:
            return (0, 246, 505, 28, 6)
        if "primer apellido" in clave or "apellido paterno" in clave:
            indice = ocurrencias.get("primer apellido", 0)
            ocurrencias["primer apellido"] = indice + 1
            return (0, 128, 412 if indice == 0 else 307, 145, 7)
        if "segundo apellido" in clave or "apellido materno" in clave:
            indice = ocurrencias.get("segundo apellido", 0)
            ocurrencias["segundo apellido"] = indice + 1
            return (0, 298, 412 if indice == 0 else 307, 130, 7)
        if "nombre" in clave:
            indice = ocurrencias.get("nombre", 0)
            ocurrencias["nombre"] = indice + 1
            return (0, 458, 412 if indice == 0 else 307, 115, 7)
        if "adscripcion" in clave:
            indice = ocurrencias.get("adscripcion", 0)
            ocurrencias["adscripcion"] = indice + 1
            return (0, 96, 367 if indice == 0 else 248, 470, 7)
        if "cargo" in clave or "grado" in clave:
            indice = ocurrencias.get("cargo", 0)
            ocurrencias["cargo"] = indice + 1
            return (0, 100, 352 if indice == 0 else 232, 465, 7)
        if "fiscalia" in clave or "autoridad" in clave:
            return (0, 145, 263, 430, 7)

    if modulo == "policias":
        if "primer apellido" in clave:
            return (1, 101, 731, 130, 7)
        if "segundo apellido" in clave:
            return (1, 282, 731, 130, 7)
        if "nombre" in clave:
            return (1, 457, 731, 110, 7)
        if "grado" in clave or "cargo" in clave:
            return (1, 140, 607, 350, 7)
        if "unidad" in clave or "arribo" in clave:
            return (1, 210, 590, 300, 7)

    if modulo == "conocimiento_hecho":
        if "911" in clave:
            return (1, 121, 467, 60, 6)
        if "fecha" in clave and "conocimiento" in clave:
            return (1, 130, 408, 105, 7)
        if "fecha" in clave and "arribo" in clave:
            return (1, 424, 408, 105, 7)
        if "hora" in clave and "conocimiento" in clave:
            return (1, 131, 382, 55, 7)
        if "hora" in clave and "arribo" in clave:
            return (1, 424, 382, 55, 7)

    if modulo in {"acta_noticia", "inspeccion_lugar"}:
        ubicacion = (
            ("calle", 1, 132, 290),
            ("exterior", 1, 114, 273),
            ("interior", 1, 288, 273),
            ("postal", 1, 478, 273),
            ("colonia", 1, 132, 256),
            ("localidad", 1, 132, 256),
            ("municipio", 1, 142, 242),
            ("entidad federativa", 1, 142, 220),
            ("referencias", 1, 122, 204),
        )
        for palabra, pagina, x, y in ubicacion:
            if palabra in clave:
                return (pagina, x, y, 430, 7)

    if modulo == "acta_noticia":
        if "fecha" in clave and "arribo" in clave:
            return (1, 424, 408, 105, 7)
        if "hora" in clave and "arribo" in clave:
            return (1, 424, 382, 55, 7)

    if modulo == "inspeccion_lugar":
        if "latitud" in clave:
            return (1, 83, 171, 105, 6)
        if "longitud" in clave:
            return (1, 334, 171, 105, 6)

    if modulo == "narracion_primer_respondiente" and (
        "narracion" in clave or "narrativ" in clave or "describa" in clave or "relato" in clave
    ):
        return (3, 38, 688, 532, 8)

    if modulo == "anexo_a":
        if "rnd" in clave or "registro nacional de detenciones" in clave:
            return (4, 406, 748, 160, 6)
        if "fecha" in clave:
            return (4, 77, 699, 110, 7)
        if "hora" in clave:
            return (4, 280, 699, 55, 7)
        if "primer apellido" in clave:
            return (4, 104, 652, 115, 7)
        if "segundo apellido" in clave:
            return (4, 273, 652, 115, 7)
        if "nombre" in clave:
            return (4, 444, 652, 130, 7)

    return None


def _ancla_casilla(modulo, etiqueta, valor):
    clave = _normalizar(etiqueta)
    seleccionado = _normalizar(valor)
    if not seleccionado:
        return None

    if modulo == "puesta_disposicion":
        if "no se entregan anexos" in clave and seleccionado in {"x", "si", "true"}:
            return (0, 517, 496)
        for letra, posicion in {
            "a": (0, 190, 553),
            "b": (0, 190, 536),
            "c": (0, 190, 518),
            "d": (0, 190, 505),
            "e": (0, 516, 553),
            "f": (0, 516, 536),
            "g": (0, 516, 518),
        }.items():
            if f"anexo {letra}" in clave and ("entrega" in clave or "entregado" in clave):
                return posicion if seleccionado in {"si", "x", "true"} else None
        if "documentacion complementaria" in clave:
            if seleccionado == "si":
                return (0, 154, 476)
            if seleccionado == "no":
                return (0, 154, 441)
        opciones_documentacion = {
            "fotografias": (0, 350, 476),
            "audio": (0, 520, 476),
            "videos": (0, 350, 458),
            "certificados medicos": (0, 520, 458),
            "otra": (0, 350, 441),
        }
        if clave in opciones_documentacion:
            return opciones_documentacion[clave]

    if modulo == "policias":
        opciones_institucion = {
            "guardia nacional": (1, 40, 672),
            "policia federal ministerial": (1, 40, 657),
            "policia ministerial": (1, 230, 687),
            "policia mando unico": (1, 230, 672),
            "policia estatal": (1, 230, 657),
            "policia municipal": (1, 230, 642),
        }
        if clave in {"institucion", "institucion a la que pertenece"}:
            return opciones_institucion.get(seleccionado)

    if modulo == "conocimiento_hecho":
        opciones = {
            "denuncia": (1, 140, 495),
            "flagrancia": (1, 268, 495),
            "localizacion": (1, 364, 495),
            "mandamiento judicial": (1, 535, 495),
            "llamada de emergencia": (1, 154, 481),
            "descubrimiento": (1, 303, 481),
            "aportacion": (1, 405, 481),
        }
        if clave in {"como se entero", "como se entero del hecho"}:
            return opciones.get(seleccionado)

    return None


def _dibujar_referencia(lienzo, valor):
    if not valor:
        return
    segmentos = re.findall(r"[A-Za-z0-9]+", _formatear(valor))
    posiciones = [
        (326, 712, 20),
        (350, 712, 27),
        (380, 712, 22),
        (405, 712, 22),
        (430, 712, 17),
        (451, 712, 17),
        (473, 712, 42),
        (519, 712, 17),
        (542, 712, 17),
    ]
    if len(segmentos) == 5:
        indices = (0, 1, 2, 3, 6)
    elif len(segmentos) >= len(posiciones):
        indices = tuple(range(len(posiciones)))
    elif len(segmentos) > 1:
        indices = tuple(range(len(segmentos)))
    else:
        texto = segmentos[0] if segmentos else ""
        longitudes = (3, 4, 3, 4, 2, 2, 4, 2, 2)
        segmentos = []
        inicio = 0
        for longitud in longitudes:
            segmentos.append(texto[inicio : inicio + longitud])
            inicio += longitud
        indices = tuple(range(len(posiciones)))

    lienzo.setFont(FUENTE, 5)
    for indice, posicion in zip(indices, segmentos):
        x, y, ancho = posiciones[indice]
        linea = _texto_seguro(posicion)
        while lienzo.stringWidth(linea, FUENTE, 5) > ancho and len(linea) > 1:
            linea = linea[:-1]
        lienzo.drawString(x, y, linea)


def _crear_hoja_sobre(ancho, alto):
    buffer = BytesIO()
    lienzo = canvas.Canvas(buffer, pagesize=(ancho, alto), pageCompression=1)
    return buffer, lienzo


def _anexos_seleccionados(campos):
    anexos = {
        letra
        for modulo, letra in {
            "anexo_a": "a",
            "anexo_b": "b",
            "anexo_c": "c",
            "inspeccion_vehiculo": "c",
            "anexo_d": "d",
            "anexo_e": "e",
            "anexo_f": "f",
            "bitacora": "g",
            "seccion_5_complemento": "g",
        }.items()
        if campos.get(modulo)
    }

    for campo in campos.get("puesta_disposicion", []):
        etiqueta = _normalizar(campo.get("label"))
        valor = _normalizar(campo.get("value"))
        for letra in "abcdefg":
            if f"anexo {letra}" not in etiqueta and f"anexos {letra}" not in etiqueta:
                continue
            if "cantidad" in etiqueta or "armas" in etiqueta or "objetos" in etiqueta:
                if valor.isdigit() and int(valor) > 0:
                    anexos.add(letra)
            elif valor in {"si", "x", "true", "1"}:
                anexos.add(letra)
    return anexos


def generar_pdf_iph(iph, capturas=None, campos_por_modulo=None):
    """Devuelve la plantilla oficial con capturas persistidas y valores actuales."""
    if not PLANTILLA_IPH.is_file():
        raise FileNotFoundError(f"No se encontró la plantilla oficial del IPH: {PLANTILLA_IPH}")

    plantilla = PdfReader(str(PLANTILLA_IPH), strict=False)
    if len(plantilla.pages) != 15:
        raise ValueError("La plantilla oficial IPH2019 debe contener sus 15 páginas.")

    campos = _campos_por_modulo(capturas or {}, campos_por_modulo or {})
    buffers = []
    lienzos = []
    for pagina in plantilla.pages:
        ancho = float(pagina.mediabox.width)
        alto = float(pagina.mediabox.height)
        buffer, lienzo = _crear_hoja_sobre(ancho, alto)
        buffers.append(buffer)
        lienzos.append(lienzo)

    # Datos estructurales que no dependen de los módulos de captura.
    _dibujar_texto(lienzos[0], _formatear(getattr(iph, "folio_interno", "")), 356, 681, 195)
    expediente = _formatear(getattr(iph, "no_expediente", ""))
    for campo in campos.get("puesta_disposicion", []):
        if "expediente" in _normalizar(campo.get("label")):
            expediente = campo["value"]
            break
    _dibujar_texto(lienzos[0], expediente, 445, 591, 130)
    fecha = _formatear(getattr(iph, "fecha_puesta_disposicion", ""))
    hora = _formatear(getattr(iph, "hora_puesta_disposicion", ""))
    for campo in campos.get("puesta_disposicion", []):
        etiqueta = _normalizar(campo.get("label"))
        if "fecha" in etiqueta:
            fecha = campo["value"]
        elif "hora" in etiqueta:
            hora = campo["value"]
    if fecha:
        _dibujar_texto(lienzos[0], fecha, 77, 591, 110)
    if hora:
        _dibujar_texto(lienzos[0], hora, 244, 591, 48)
    referencia = _formatear(getattr(iph, "no_referencia", ""))
    for campo in campos.get("puesta_disposicion", []):
        if "referencia" in _normalizar(campo.get("label")):
            referencia = campo["value"]
            break
    _dibujar_referencia(lienzos[0], referencia)

    ocurrencias_por_modulo = {}
    overflow = []
    for modulo, campos_modulo in campos.items():
        ocurrencias = ocurrencias_por_modulo.setdefault(modulo, {})
        zonas = list(ZONAS_MODULO.get(modulo, []))
        zona_indice = 0
        pagina_actual = None
        x = y = ancho = limite_y = 0
        for campo in campos_modulo:
            casilla = _ancla_casilla(modulo, campo["label"], campo["value"])
            if casilla:
                pagina, x_casilla, y_casilla = casilla
                lienzos[pagina].setFont(FUENTE, 7)
                lienzos[pagina].drawString(x_casilla, y_casilla, "X")
                continue
            if modulo == "puesta_disposicion" and "referencia" in _normalizar(campo["label"]):
                continue
            if modulo == "puesta_disposicion" and "expediente" in _normalizar(campo["label"]):
                continue
            if modulo == "puesta_disposicion" and {
                "fecha",
                "hora",
            } & set(_normalizar(campo["label"]).split()):
                continue
            texto = f"{campo['label']}: {campo['value']}".strip(": ")
            ancla = _ancla_directa(modulo, campo["label"], ocurrencias)
            if ancla:
                pagina, x_ancla, y_ancla, ancho_ancla, fuente = ancla
                _dibujar_texto(lienzos[pagina], _valor_de(campo), x_ancla, y_ancla, ancho_ancla, fuente)
                continue

            if not zonas:
                overflow.append((modulo, texto))
                continue
            if pagina_actual is None or y < limite_y:
                if zona_indice >= len(zonas):
                    overflow.append((modulo, texto))
                    continue
                pagina_actual, x, y, ancho, limite_y = zonas[zona_indice]
                zona_indice += 1
            nuevo_y = _dibujar_texto(lienzos[pagina_actual], texto, x, y, ancho)
            y = nuevo_y - INTERLINEADO

    for lienzo in lienzos:
        lienzo.showPage()
        lienzo.save()

    writer = PdfWriter()
    paginas_incluidas = {0, 1, 2, 3}
    paginas_anexo = {letra: pagina for letra, pagina in zip("abcdefg", (4, 7, 8, 9, 11, 13, 14))}
    for letra in _anexos_seleccionados(campos):
        pagina_anexo = paginas_anexo[letra]
        paginas_incluidas.add(pagina_anexo)
        if letra in {"a", "d", "e"}:
            paginas_incluidas.add(pagina_anexo + 1)
        if letra == "a":
            paginas_incluidas.add(pagina_anexo + 2)

    for indice, (pagina, buffer) in enumerate(zip(plantilla.pages, buffers)):
        if indice not in paginas_incluidas:
            continue
        buffer.seek(0)
        sobre = PdfReader(buffer, strict=False).pages[0]
        pagina.merge_page(sobre)
        writer.add_page(pagina)

    if overflow:
        paginas_extra = []
        for modulo, texto in overflow:
            paginas_extra.extend(
                simpleSplit(
                    f"{modulo.replace('_', ' ').title()}: {texto}",
                    FUENTE,
                    TAMANO_FUENTE,
                    532,
                )
            )
        indice = 0
        while indice < len(paginas_extra):
            buffer, lienzo = _crear_hoja_sobre(
                float(plantilla.pages[14].mediabox.width),
                float(plantilla.pages[14].mediabox.height),
            )
            y = 708
            while indice < len(paginas_extra) and y >= 68:
                lienzo.setFont(FUENTE, TAMANO_FUENTE)
                lienzo.drawString(38, y, _texto_seguro(paginas_extra[indice]))
                y -= INTERLINEADO
                indice += 1
            lienzo.showPage()
            lienzo.save()
            buffer.seek(0)
            continuation = deepcopy(plantilla.pages[14])
            continuation.merge_page(PdfReader(buffer, strict=False).pages[0])
            writer.add_page(continuation)

    salida = BytesIO()
    writer.write(salida)
    salida.seek(0)
    return salida
