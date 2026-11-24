# Diagnóstico exclusivo del PDF del sistema IPH

Fecha: 2026-11-23

## Alcance

Se realizó una revisión aislada de la plantilla, coordenadas, datos Vue, rutas Flask, capturas SQL Server y salida PDF.

No se modificó código, SQL, Docker, volúmenes ni el módulo de voz.

No se consultó ni modificó ningún IPH real distinto del registro ficticio `2183`, identificado con `PRUEBA_CODEX_20261123`.

## 1. Resumen ejecutivo

La plantilla oficial contiene **15 páginas** y el generador conserva sus páginas principales.

El PDF se genera en memoria y se devuelve al navegador. Actualmente no existe una ruta que escriba el documento final en `backend/app/generated_pdfs` ni que lo recupere después desde disco. Por ello, la vista previa, la descarga y la persistencia no forman todavía un flujo único y estable.

La muestra ficticia generada produjo un PDF válido de cuatro páginas. Las páginas principales se conservaron, pero la página 1 presenta errores confirmados visualmente:

- Los campos `Responsable / Nombre(s)` y `Receptor / Nombre(s)` no llegaron a sus coordenadas configuradas.
- Estos dos campos aparecieron al final de la página como texto genérico.
- Una etiqueta y su valor quedaron fuera de los campos oficiales.
- Las zonas de depuración confirmaron que los marcos se calculan y encajan parcialmente.
- La fuente Helvetica, en el campo largo de nombres, puede ser demasiado pequeña o no ajustarse visualmente al espacio real.
- El PDF final conserva 15 páginas solo como plantilla disponible, pero el generador normalmente devuelve solo las páginas seleccionadas.

## 2. Evidencia disponible

### Plantilla original

La plantilla original fue renderizada a PNG completo:

- [Página 1](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-01.png)
- [Página 2](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-02.png)
- [Página 3](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-03.png)
- [Página 4](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-04.png)
- [Página 5](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-05.png)
- [Página 6](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-06.png)
- [Página 7](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-07.png)
- [Página 8](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-08.png)
- [Página 9](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-09.png)
- [Página 10](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-10.png)
- [Página 11](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-11.png)
- [Página 12](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-12.png)
- [Página 13](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-13.png)
- [Página 14](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-14.png)
- [Página 15](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/original/original-15.png)

### PDF generado

- [Página 1 generada con datos ficticios](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/generada/generated-1.png)
- [Página 2 generada](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/generada/generated-2.png)
- [Página 3 generada](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/generada/generated-3.png)
- [Página 4 generada](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/generada/generated-4.png)
- [Página 1 con marcos de depuración](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/generada/debug-page-1.png)

## 3. Métodos de revisión

Se realizó:

- Lectura con pypdf de las 15 páginas.
- Renderizado de la plantilla completa a 100 DPI.
- Inspección visual directa de las 15 imágenes originales.
- Generación con datos ficticios.
- Renderizado de la página generada.
- Generación con marcos rojos mediante `generar_pdf_iph_debug`.
- Lectura de la información persistente asociada a IPH 2183.

Dimensiones originales:

- Todas las páginas usan 612 x 792 puntos.
- Rotación PDF: 0.
- Página original cuenta: 15.

## 4. Flujo actual

### Vue

[FormularioIPHView.vue](/root/iph-project/frontend/src/views/FormularioIPHView.vue) obtiene cada campo activo con `leerCamposActuales`.

Cada campo se convierte a:

```json
{"label": "Etiqueta del campo", "value": "Valor"}
```

El flujo reúne todos los módulos en `camposPorModulo`.

Rutas usadas por el frontend:

- Vista previa en iframe: `POST /api/iph/<id>/previsualizar-pdf`
- Vista previa de pantalla: `POST /api/iph/<id>/capturas/<pantalla>/previsualizar-pdf`
- Descarga parcial/final: `POST /api/iph/<id>/exportar-pdf`
- Descarga final GET: `GET /api/iph/<id>/exportar-pdf`

Problema: Vue transforma campos HTML a etiquetas humanas y no utiliza claves estables para PDF. Esto obliga al backend a reconocer texto libre mediante normalización y coincidencias aproximadas.

### Capturas SQL Server

[capturas.js](/root/iph-project/frontend/src/store/capturas.js) guarda la captura mediante `PUT /api/iph/<id>/capturas/<pantalla>`.

[iph/routes.py](/root/iph-project/backend/app/blueprints/iph/routes.py) persiste el JSON en `dbo.iph_capturas_web.datos_json`.

El generador [pdf_generator.py](/root/iph-project/backend/app/services/pdf_generator.py) vuelve a convertir ese JSON y los campos actuales en una lista:

```json
{"label": "...", "value": "..."}
```

El registro no tenía capturas persistidas al verificarse. Por tanto, la muestra visual se construyó con campos enviados directamente por el frontend, no con un flujo recuperado de SQL Server.

### Generación

El generador:

1. Lee la plantilla.
2. Lee datos estructurales de `dbo.IPH`.
3. Lee capturas web.
4. Combina capturas con campos actuales.
5. Imprime una hoja transparente por página.
6. Une las hojas con la plantilla.
7. Devuelve un `BytesIO`.

No usa `PDF_OUTPUT_DIR`.

### Vista previa frente a descarga

La vista previa y la descarga usan el mismo `generar_pdf_iph`.

Sin embargo:

- Vista previa agrega los campos actuales.
- Descarga POST agrega los campos actuales solo si el IPH está terminado.
- Vista previa usa `_capturas_pdf` para recuperar datos persistidos.
- Descarga GET usa `_capturas_pdf` y no recibe campos actuales.

No se pudo comprobar visualmente una descarga persistida después de guardado, porque no existe una captura persistida para 2183.

## 5. Persistencia real

### Estado confirmado

- `PDF_OUTPUT_DIR` apunta a `/app/app/generated_pdfs`.
- El volumen Docker monta `pdf_output:/app/app/generated_pdfs`.
- El directorio está vacío.
- `_crear_respuesta_pdf` llama a `send_file(BytesIO(...))`.
- No se guarda ningún PDF en disco.
- No existe una ruta de recuperación de documentos generados.

Conclusión:

> El PDF generado actualmente es temporal. No se conserva como archivo final ni existe un identificador de documento para consultarlo posteriormente.

Antes de cualquier corrección se debe decidir si el PDF final:

- se guarda en el volumen `pdf_output`;
- se guarda en SQL Server;
- se guarda fuera de Compose;
- o solo se consulta por generación reproducible.

## 6. Diagnóstico visual de las 15 páginas originales

| Página | Apartado visible | Estado visual original |
|---:|---|---|
| 1 | Puesta a disposición | Completa |
| 2 | Primer respondiente y conocimiento del hecho | Completa |
| 3 | Lugar de intervención e inspección | Completa |
| 4 | Narrativa y continuación | Completa |
| 5 | Anexo A: detención | Completa |
| 6 | Derechos y inspección de detención | Completa |
| 7 | Lugar de detención y primer respondiente | Completa |
| 8 | Anexo B: uso de fuerza | Completa |
| 9 | Anexo C: inspección de vehículo | Completa |
| 10 | Anexo D: armas y objetos | Completa |
| 11 | Anexo D: registro de objetos | Completa |
| 12 | Anexo E: entrevistas | Completa |
| 13 | Anexo E: datos del lugar | Completa |
| 14 | Anexo F: entrega-recepción | Completa |
| 15 | Anexo G: continuación narrativa | Completa |

No se detectaron páginas incompletas ni textos faltantes en la plantilla original.

## 7. Errores confirmados

| ID | Página | Campo afectado | Evidencia visual | Causa técnica | Archivo a modificar | Solución propuesta | Comprobación |
|---|---:|---|---|---|---|---|---|
| PDF-001 | 1 | Responsable / Nombre(s) | Aparece al pie de la página junto al texto `Responsable / Nombre(s):` | El backend busca `nombres`, pero Vue envía `Nombre(s)`, por lo que no coincide en `_ancla_directa` | `pdf_generator.py`, `pdf_layout.py`, `FormularioIPHView.vue` | Usar una clave estable y un mapa exacto del campo; quitar coincidencia aproximada | Captura real con PRUEBA_CAMPO_03 dentro del campo y marco rojo fuera |
| PDF-002 | 1 | Receptor / Nombre(s) | Aparece al pie de la página junto al texto `Receptor / Nombre(s):` | El mismo problema de etiqueta `Nombre(s)` frente a clave `nombres` | `pdf_generator.py`, `pdf_layout.py`, `FormularioIPHView.vue` | Añadir el alias exacto `nombre(s)` al mapa receptor | Texto visible únicamente dentro del campo oficial |
| PDF-003 | 1 | Responsable segundo apellido | Enmarcado visualmente en la posición principal | Se imprimió correctamente; falta verificar acentos/textos largos | `pdf_layout.py` | Requiere solo prueba de longitud y fuente mínima | Texto largo ajustado sin corte |
| PDF-004 | 1 | Receptor segundo apellido | Aparece como texto plano `CODEX` en la línea | Coincidencia y coordenada parecen correctas, pero sin prueba exhaustiva | `pdf_layout.py` | Validar ancho y alineación | Captura visual sin solapamiento |
| PDF-005 | 1 | Folio asignado | El folio ocupa el recuadro superior pero la muestra muestra el texto sobre varias líneas pequeñas | `_dibujar_campo_configurado` reduce y trunca, pero no hay inspección visual aprobada | `pdf_layout.py`, `pdf_generator.py` | Separar folio en casillas o confirmar un recuadro único | Comparar con página 1 original |
| PDF-006 | 1 | Fecha | Aparece dentro de casillas separadas | La conversión elimina separadores y puede confundir formato | `pdf_generator.py` | Validar fecha ISO y emitir `DDMMAAAA` únicamente | Generar 23/11/2026 y comparar casillas |
| PDF-007 | 1 | Hora | Aparece en 4 casillas | La conversión elimina separadores | `pdf_generator.py` | Validar 24 horas y rechazar formatos inválidos | Generar 14:35 y comparar cada casilla |
| PDF-008 | 1 | Expediente | Se extiende por casillas de 20 posiciones | Puede cortarse o perder caracteres especiales | `pdf_generator.py` | Definir expediente alfanumérico y límite real | Texto largo PRUEBA_CODEX dentro de casillas |
| PDF-009 | 1 | Persona responsable y receptor | Los marcos rojos cubren campos pero los textos largos no están dentro | Faltan claves estables y anchos/fontes por campo | `pdf_layout.py`, `pdf_generator.py` | Registrar ancho, fuente, alineación y multilinea por campo | PDF depuración + comparación 1:1 |
| PDF-010 | 1-15 | Campos sin ancla | El fallback puede imprimir `etiqueta: valor` en áreas genéricas | La aplicación usa texto normalizado y zonas heurísticas | `pdf_generator.py` | Convertir todas las etiquetas a claves conocidas y eliminar fallback no aprobado | Ningún texto de fallback en prueba completa |
| PDF-011 | 1-15 | Texto largo | Los campos desconocidos pueden ir a overflow en página adicional | Solo se limita al ancho, no existe edición de varias líneas en todos los campos | `pdf_generator.py` | Implementar ajuste y salto controlado por campo | Largo no cortado ni encimado |
| PDF-012 | 1-15 | Acentos | La muestra conserva caracteres compatibles con CP1252 | El texto pasa por `_texto_seguro`, con reemplazo para otros caracteres | `pdf_generator.py` | Usar fuente Unicode o validar conjunto de caracteres | Prueba Ñ, acentos y caracteres especiales |
| PDF-013 | 1-15 | Páginas anexas | El generador añade anexos condicionalmente | `_anexos_seleccionados` depende de etiquetas humanas | `pdf_generator.py`, `PuestaDisposicionForm.vue` | Usar claves A-G estables y respuesta booleana | Cada anexo aparece solo cuando fue entregado |
| PDF-014 | 1-15 | PDF persistente | No existe archivo generado después de la solicitud | `_crear_respuesta_pdf` usa `send_file(BytesIO)` y no guarda | `iph/routes.py`, configuración PDF | Crear registro persistente y ruta de descarga | Archivar, listar y descargar el mismo PDF |
| PDF-015 | 1-15 | Preview/download | Son blobs distintos aunque comparten el mismo generador | Diferencias en `camposPorModulo` y capturas persistidas | `FormularioIPHView.vue`, `iph/routes.py` | Construir un único payload de generación y comparar checksum PDF | Preview y descarga iguales |

## 8. Tabla de correspondencias confirmada

Los siguientes anclajes están definidos en código, pero no aprobados visualmente:

| Campo Vue | Clave backend | Página | Coordenadas PDF | Estado |
|---|---|---:|---|---|
| Folio | `folio_interno` | 1 | x=356, y=681, ancho=195 | Visual parcialmente correcto |
| Número de referencia | `no_referencia` | 1 | 9 posiciones en la banda superior | Sin prueba visual completa |
| No. expediente | `no_expediente` | 1 | x=445, y=591, 20 casillas | Correcto en forma |
| Fecha | `fecha_puesta_disposicion` | 1 | x=77, y=591, 8 casillas | Correcto en forma |
| Hora | `hora_puesta_disposicion` | 1 | x=244, y=591, 4 casillas | Correcto en forma |
| Responsable / Primer apellido | `responsable.primer_apellido` | 1 | x=128, y=412, ancho=145 | Visual correcto |
| Responsable / Segundo apellido | `responsable.segundo_apellido` | 1 | x=298, y=412, ancho=130 | Visual correcto |
| Responsable / Nombre(s) | `responsable.nombres` | 1 | x=458, y=412, ancho=115 | **Incorrecto** |
| Responsable / Adscripción | `responsable.adscripcion` | 1 | x=96, y=367, ancho=470 | Visual correcto |
| Responsable / Cargo | `responsable.cargo` | 1 | x=100, y=352, ancho=465 | Visual correcto |
| Receptor / Primer apellido | `receptor.primer_apellido` | 1 | x=128, y=307, ancho=145 | Visual correcto |
| Receptor / Segundo apellido | `receptor.segundo_apellido` | 1 | x=298, y=307, ancho=130 | Visual correcto |
| Receptor / Nombre(s) | `receptor.nombres` | 1 | x=458, y=307, ancho=115 | **Incorrecto** |
| Receptor / Institución | `receptor.institucion` | 1 | x=145, y=263, ancho=430 | Visual correcto |
| Receptor / Adscripción | `receptor.adscripcion` | 1 | x=96, y=248, ancho=470 | Visual correcto |
| Receptor / Cargo | `receptor.cargo` | 1 | x=100, y=232, ancho=465 | Visual correcto |
| Receptor / Firma | `receptor.firma` | 1 | x=100, y=217, ancho=465 | Sin prueba |
| Receptor / Sello | `receptor.sello` | 1 | x=100, y=202, ancho=465 | Sin prueba |

## 9. Análisis de la plantilla

Archivo:

[iph-delitos.pdf](/root/iph-project/backend/app/assets/iph-delitos.pdf)

Observaciones:

- Las 15 páginas están completas.
- Todas son 612 x 792 puntos.
- pypdf emitió objetos apuntadores incorrectos en las páginas/objetos 8, 10, 12 y 94.
- Los objetos incorrectos no impidieron generar el PDF.
- No se conoce si corresponden a referencias internas dañadas o a compatibilidad con el lector.

Recomendación:

- Abrir la plantilla con software institucional.
- Exportarla nuevamente desde el documento fuente si está disponible.
- Comparar la salida reparada con las 15 páginas originales.
- Mantener copias y checksum antes de reemplazarla.

## 10. StopIteration

La prueba existente falla por:

```text
StopIteration
IPHCaptura.iph_id.foreign_keys
```

La causa real es doble:

- El test espera una FK.
- El modelo no declara la FK.

No se encontró que esto impida la generación PDF real, pero sí representa una inconsistencia de integridad y debe corregirse o eliminarse el supuesto de FK según el esquema aprobado.

No se modificó el modelo ni la tabla.

## 11. Evidencia visual del problema principal

En [la página generada](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/generada/generated-1.png) aparecen dos textos al final de la página:

- `Responsable / Nombre(s): Texto largo con acentos Ñ ...`
- `Receptor / Nombre(s): PRUEBA AUTORIDAD`

Esto demuestra que las claves `nombres` no coincidieron con las etiquetas Vue `Nombre(s)`.

En [la página con marcos](/root/iph-project/DIAGNOSTICO_PDF_EVIDENCIA/generada/debug-page-1.png) se observan marcos rojos en los campos primer apellido, segundo apellido, adscripción y receptor. Los campos nombre no tienen marcos en sus posiciones oficiales, ya que fueron enviados al fallback.

## 12. Plan de corrección

### Fase 1: contrato estable

Archivos:

- `frontend/src/views/FormularioIPHView.vue`
- formularios Vue de los módulos
- `backend/app/blueprints/iph/routes.py`
- `backend/app/services/pdf_generator.py`

Cambios propuestos:

- Reemplazar etiquetas humanas como mecanismo de identificación por claves.
- Enviar `campoId`, `moduloId`, `valor`.
- Mantener etiquetas solo para presentación.
- Validar fechas, horas, booleans y anexos por tipo.

Prueba:

- Enviar el valor `PRUEBA_CAMPO_03`.
- Confirmar que cae exclusivamente en el campo correspondiente.

### Fase 2: mapa visual completo

Archivos:

- `backend/app/services/pdf_layout.py`
- `backend/app/services/pdf_generator.py`

Cambios propuestos:

- Declarar cada campo con página, x, y, ancho, fuente y alineación.
- Agregar alturas máximas y ajuste de texto.
- Agregar una prueba de marcos por página.
- Eliminar coincidencias por cadenas humanas donde sea posible.
- Revisar todas las coordenadas existentes contra las imágenes originales.

Pruebas:

- Una página por sección con datos ficticios.
- Texto corto.
- Texto largo.
- Acentos.
- Fechas.
- Horas.
- Casillas.
- Campos vacíos.

### Fase 3: anexos y páginas

Archivos:

- `PuestaDisposicionForm.vue`
- `AnexosPantalla.vue`
- `pdf_generator.py`

Cambios:

- Usar respuestas A-G por clave.
- Seleccionar páginas por clave estable.
- Validar cantidad de anexos D.
- Verificar derechos de Anexo E.
- Validar continuidad de narrativa G.

Prueba:

- Activar uno por uno los anexos A-G.
- Confirmar páginas esperadas y ninguna página adicional incorrecta.

### Fase 4: persistencia

Archivos:

- `iph/routes.py`
- `pdf_generator.py`
- configuración Docker
- modelo relacionado si se decide SQL Server

Cambios:

- Crear un PDF persistente con identificador.
- Asociarlo al IPH.
- Guardarlo en volumen o tabla según decisión arquitectónica.
- Exponer descarga por ID.
- Recuperar y devolver el mismo documento.
- Definir si preview guarda borrador o solo genera.

Pruebas:

- Generar.
- Consultar.
- Descargar.
- Reiniciar backend.
- Descargar nuevamente.
- Comparar checksum.

### Fase 5: regresión visual

Archivos afectados por Fase 1-4.

Pruebas:

- Comparar todas las páginas originales.
- Comparar vista previa y descarga.
- Confirmar que no hay solapamientos.
- Confirmar texto completo.
- Confirmar firma y sellos.
- Confirmar anexos y folio.
- Generar PDF final y abrirlo en visor local.

## 13. Riesgos

- Una corrección manual sin revisión institucional puede desplazar todos los campos.
- Reemplazar la plantilla dañada puede alterar el formato oficial.
- Persistir PDF en SQL Server puede duplicar almacenamiento o consumir memoria.
- Persistir PDF en disco requiere definir retención y respaldo.
- El fallback de texto puede ocultar campos sin ancla.
- El uso de claves nuevas requiere actualizar Vue y Flask de manera coordinada.

## 14. Pruebas pendientes

- Inspección visual real de todas las páginas generadas con datos completos.
- Recuperación de capturas desde SQL Server.
- Verificación de persistencia después de reinicio.
- Vista previa y descarga con los mismos datos.
- Anexos A-G.
- Textos largos y multilínea.
- Caracteres Unicode fuera de CP1252.
- PDF final terminado.
- Reparación o sustitución de la plantilla.

## 15. Conclusión

El problema PDF no se reduce a una sola coordenada. Hay tres causas principales:

1. Las etiquetas Vue no forman claves PDF estables.
2. Algunas coincidencias aproximadas no encuentran los anclajes reales.
3. Los PDFs no se persisten y no existe una ruta de recuperación final.

Antes de modificar el proyecto, se requiere:

- Autorización expresa.
- Decisión de persistencia.
- Una aprobación visual institucional de todas las coordenadas.
- Corrección coordinada de Vue y Flask.
- Pruebas visuales de las 15 páginas.
