# Diagnóstico integral y funcional del sistema IPH

Fecha: 2026-11-23

## Alcance y restricciones

Se realizó una auditoría con los contenedores existentes, el navegador compartido autenticado y consultas de lectura al SQL Server configurado.

No se modificó código, configuración, Docker, SQL, estructura de tablas ni el servicio de voz.

Se creó expresamente el registro ficticio solicitado:

- Folio: `28/41/005/00182/2026`
- ID: `2183`
- Prefijo utilizado: `PRUEBA_CODEX_20261123`
- Estado inicial observado: `EN_TRAMITE`

No se solicitaron ni mostraron contraseñas, cookies ni tokens.

## 1. Estado general

El sistema está operativo para la sesión institucional probada:

- Docker Compose está configurado.
- Backend, frontend y voz están iniciados y saludables.
- El usuario autenticado pudo entrar y cargar el panel.
- El panel leyó 244 registros para el municipio y unidad asociados.
- Se pudo crear el IPH ficticio 2183.
- Las tablas web existen en la base real configurada.
- El navegador pudo abrir el formulario IPH 2183.
- El generador produjo un PDF ficticio válido de cuatro páginas.
- No fue posible completar todas las pruebas de edición y anexos por inestabilidad de las sesiones de automatización del navegador.

## 2. Estado de Docker

| Contenedor | Estado | Evidencia |
|---|---|---|
| `iph_backend` | Healthy | Puerto 5000, `/api/health` respondió `{"status":"ok"}` |
| `iph_frontend` | Healthy | Puerto 8080, HTML y interfaz cargados |
| `iph_voz` | Healthy | `/health` interno respondió modelo cargado |

`docker compose config` terminó sin errores.

El backend usa:

- Servidor SQL: `192.168.123.48:1433`
- Base: `PGJ_NSJP`
- Servicio de voz: `http://voz:8000`

La base mostrada es compartida. Solo se hicieron lecturas y la creación del registro ficticio que el usuario autorizó. No se ejecutaron DDL ni instrucciones de modificación sobre tablas originales.

## 3. Estado del frontend

Verificado:

- La pantalla de login carga.
- La validación de campos vacíos funciona.
- La sesión autenticada persiste.
- El panel carga 244 registros.
- El buscador, ordenamiento y paginación están presentes.
- El botón Nuevo IPH creó el folio 2183.
- El workspace muestra las secciones y formularios.
- La vista previa tiene un componente iframe.
- El formulario de anexos se abre como modal.
- Los campos probados aceptaron texto, fechas y horas.
- El dictado de voz aparece al enfocar campos.

Problemas observados:

- La automatización del navegador perdió varias veces la página por Page crashed.
- El asistente de anexos se volvió a abrir automáticamente al recargar por el uso de `sessionStorage`.
- El cierre produjo una confirmación de cambios sin guardar.
- No se pudo completar visualmente toda la navegación durante esta sesión.

## 4. Estado del backend

Rutas principales registradas:

- `/api/auth/login`
- `/api/auth/registro`
- `/api/auth/perfil`
- `/api/iph/`
- `/api/iph/<iph_id>`
- `/api/iph/<iph_id>/<modulo>`
- `/api/iph/<iph_id>/<modulo>/lista`
- `/api/iph/<iph_id>/capturas/<pantalla>`
- `/api/iph/<iph_id>/adjuntos`
- `/api/iph/<iph_id>/estado`
- `/api/iph/<iph_id>/previsualizar-pdf`
- `/api/iph/<iph_id>/exportar-pdf`
- `/api/voz/transcribir`

Comprobado:

- Endpoints protegidos rechazan solicitudes sin JWT.
- Login sin datos devuelve 400.
- `/api/health` devuelve 200.
- El folio 2183 pudo crearse desde la interfaz.

## 5. Estado de SQL Server

Lectura real del esquema para las tablas consultadas:

| Tabla | Columnas relevantes |
|---|---|
| `dbo.IPH` | `ID_IPH INTEGER`, `IPH VARCHAR(24)`, `ID_MUNICIPIO_IPH SMALLINT`, `ID_ESTADO_IPH SMALLINT`, `FECHA_REGISTRO DATETIME`, `ACTIVO_IPH BIT` |
| `dbo.iph_capturas_web` | `id INTEGER`, `iph_id INTEGER`, `pantalla NVARCHAR(80)`, `datos_json NVARCHAR`, `actualizado_en DATETIME2` |
| `dbo.iph_estado_web` | `iph_id INTEGER`, `estado NVARCHAR(20)`, `actualizado_en DATETIME2` |
| `dbo.iph_adjuntos_web` | `id NVARCHAR(100)`, `iph_id INTEGER`, `anexo NVARCHAR(80)`, `nombre NVARCHAR(255)`, `mime_type NVARCHAR(100)`, `tamano BIGINT`, `contenido VARBINARY`, `creado_en DATETIME2` |

Resultado:

- `dbo.IPH.ID_IPH` es realmente entero.
- Las tres tablas web existen.
- El estado inicial de 2183 es `EN_TRAMITE`.
- No existen capturas ni adjuntos asociados a 2183 al momento de verificarlo.

## 6. Resultados de autenticación

Estado: FUNCIONA para la sesión probada.

Evidencia:

- Se abrió el panel con el usuario `POLICIA`.
- El usuario mostró su adscripción y puesto.
- El panel pudo consultar los registros.
- El workspace pudo abrir el registro creado.

No se recopiló ni expuso el token.

## 7. Resultados de captura y edición IPH

Estado: PARCIAL.

Se verificó:

- Creación del IPH 2183.
- Folio asignado correctamente por el sistema.
- Apertura del workspace.
- Edición de fecha, hora, expediente y datos personales ficticios.
- Vista previa automática intentada.

No se pudo confirmar:

- Guardado persistente completo mediante automatización.
- Recuperación posterior de todos los campos.
- Edición secuencial de todos los módulos.
- Finalización del IPH.

Se dejaron en el navegador valores temporales con prefijos ficticios. La base web no tenía captura persistida cuando se consultó el modelo.

## 8. Resultados de anexos

Estado: PARCIAL.

Verificado:

- El asistente de anexos A-G se mostró.
- Existe una opción Sí/No para cada anexo.
- Existe la opción Ningún anexo.
- Los botones de navegación y cierre aparecen.
- La interfaz mostró 7 respuestas registradas temporalmente como No.
- La interfaz mostró una confirmación de cierre por cambios pendientes.

No se confirmó persistencia:

- No existían adjuntos asociados a 2183.
- No existía una captura persistida en `iph_capturas_web`.

No se subieron archivos de prueba porque el navegador perdió estabilidad durante el flujo.

## 9. Estado del servicio de voz

Estado: VERIFICADO SOLO EN SALUD.

- `/health` interno respondió modelo cargado.
- No se modificó el módulo de voz.
- No se probó transcripción real para evitar depender de audio no disponible.

## 10. Persistencia

Estado: NO COMPLETADO.

Resultado real:

- Las tablas existen.
- IPH 2183 tiene estado `EN_TRAMITE`.
- No hay captura web ni adjunto persistido asociado.

No se reiniciaron contenedores ni se probó persistencia después de reinicio.

## 11. Diagnóstico completo del PDF

### Evidencias generadas

Se generó `/tmp/PRUEBA_CODEX_20261123.pdf` desde `generar_pdf_iph` con datos ficticios.

Resultado técnico:

- Archivo PDF válido.
- Versión PDF 1.3.
- Cuatro páginas principales.
- Texto extraído en la página 1.
- Se encontraron los marcadores ficticios:
  - `PRUEBA_CAMPO_01`
  - `PRUEBA_CAMPO_02`
  - `PRUEBA_CAMPO_03`
  - `SEGUNDA UNIDAD PRUEBA_CODEX_20261123`
  - `RECEPTOR_PRUEBA`
  - `PRUEBA AUTORIDAD`
  - `FISCALÍA PRUEBA_CODEX_20261123`

La plantilla PDF original contiene advertencias conocidas al leerla con pypdf:

- `Ignoring wrong pointing object 8 0`
- `Ignoring wrong pointing object 10 0`
- `Ignoring wrong pointing object 12 0`
- `Ignoring wrong pointing object 94 0`

Estas advertencias no impidieron generar un documento válido, pero requieren reparación o validación visual de la plantilla.

### Causa técnica probable de posiciones incorrectas

El generador usa:

- Coordenadas manuales calibrables.
- Coincidencia por texto normalizado de etiquetas.
- Zonas genéricas para campos sin coincidencia exacta.
- Fallback a áreas de escritura.
- Casillas individuales para fecha, hora y expediente.
- Un único conjunto de coordenadas para la primera página.

Los campos mal colocados pueden provenir de cualquiera de estos factores:

1. Una etiqueta de Vue no coincide exactamente con la etiqueta esperada por `_normalizar`.
2. El fallback imprime etiquetas completas en áreas genéricas en lugar de usar su ancla configurada.
3. Las coordenadas fueron ajustadas manualmente sin inspección visual automatizada de todas las páginas.
4. El tamaño real de los renglones no coincide con los anchos configurados.
5. El texto largo se trunca o se reduce pero no se verifica visualmente por campo.
6. La plantilla tiene objetos PDF mal referenciados.

### Inspección de coordinadas

Todas las coordenadas siguientes corresponden a puntos PDF en origen inferior izquierdo, de acuerdo con `backend/app/services/pdf_layout.py`.

| Campo de Vue | Campo del backend | Página PDF | Coordenadas |
|---|---|---:|---|
| Folio | `folio_interno` | 1 | x=356, y=681, ancho=195 |
| No. expediente | `no_expediente` | 1 | x=445, y=591, paso=6.5, 20 casillas |
| Fecha puesta a disposición | `fecha_puesta_disposicion` | 1 | x=77, y=591, paso=12, 8 casillas |
| Hora puesta a disposición | `hora_puesta_disposicion` | 1 | x=244, y=591, paso=12, 4 casillas |
| Responsable: primer apellido | `responsable.primer_apellido` | 1 | x=128, y=412, ancho=145 |
| Responsable: segundo apellido | `responsable.segundo_apellido` | 1 | x=298, y=412, ancho=130 |
| Responsable: nombres | `responsable.nombres` | 1 | x=458, y=412, ancho=115 |
| Responsable: adscripción | `responsable.adscripcion` | 1 | x=96, y=367, ancho=470 |
| Responsable: cargo/grado | `responsable.cargo` | 1 | x=100, y=352, ancho=465 |
| Receptor: primer apellido | `receptor.primer_apellido` | 1 | x=128, y=307, ancho=145 |
| Receptor: segundo apellido | `receptor.segundo_apellido` | 1 | x=298, y=307, ancho=130 |
| Receptor: nombres | `receptor.nombres` | 1 | x=458, y=307, ancho=115 |
| Receptor: institución | `receptor.institucion` | 1 | x=145, y=263, ancho=430 |
| Receptor: adscripción | `receptor.adscripcion` | 1 | x=96, y=248, ancho=470 |
| Receptor: cargo | `receptor.cargo` | 1 | x=100, y=232, ancho=465 |
| Receptor: firma | `receptor.firma` | 1 | x=100, y=217, ancho=465 |
| Receptor: sello | `receptor.sello` | 1 | x=100, y=202, ancho=465 |

Coordenadas adicionales usadas por el generador:

| Campo | Página | Coordenadas |
|---|---:|---|
| Primer apellido policía | 2 | x=101, y=731 |
| Segundo apellido policía | 2 | x=282, y=731 |
| Nombre policía | 2 | x=457, y=731 |
| 911 conocimiento | 2 | x=121, y=467 |
| Fecha conocimiento | 2 | x=130, y=408 |
| Hora conocimiento | 2 | x=131, y=382 |
| Fecha arribo | 2 | x=424, y=408 |
| Hora arribo | 2 | x=424, y=382 |
| Narrativa primer respondiente | 4 | x=38, y=688 |
| RND Anexo A | 5 | x=406, y=748 |
| Fecha Anexo A | 5 | x=77, y=699 |
| Hora Anexo A | 5 | x=280, y=699 |

La correspondencia anterior no fue extraída de una inspección visual completa de todas las páginas; proviene de `pdf_layout.py` y `_ancla_directa` en `pdf_generator.py`.

### Prueba real del StopIteration

La prueba `test_preview_without_capture_returns_valid_pdf` falló con:

`StopIteration`

Causa exacta: la línea 18 intenta obtener una clave foránea de `IPHCaptura.iph_id`; el modelo no tiene una clave foránea declarada.

Clasificación:

- Es un error real del test en la hipótesis de relación.
- También es una inconsistencia real del modelo ORM.
- No impide necesariamente la ruta real, porque la tabla SQL existente sí utiliza `iph_id INTEGER` y el código puede consultarla por filtros.
- Puede impedir que el modelo represente correctamente integridad referencial.

Archivos involucrados:

- `backend/tests/test_pdf_preview_route.py:18`
- `backend/app/models/iph.py:460`
- `backend/app/blueprints/iph/routes.py:991`
- `backend/app/blueprints/iph/routes.py:1192`

## 12. Evidencias visuales

No fue posible abrir el PDF temporal como archivo desde el navegador debido a la restricción de carpetas confiables del navegador.

Sí se verificó:

- Extracción válida de texto.
- Página 1 con datos ficticios.
- Un documento total de cuatro páginas.
- Generación de PDF sin excepción.

Se recomienda una inspección visual posterior mediante capturas de las 15 páginas originales y una conversión controlada a imágenes. No se realizó esa conversión completa en esta auditoría.

## 13. Errores encontrados

| Hallazgo | Archivo | Función/línea aproximada | Clasificación |
|---|---|---|---|
| Modelo web sin FK declarada | `backend/app/models/iph.py` | `IPHCaptura`, línea 452-464 | MEDIO |
| Test PDF falla por asumir FK no declarada | `backend/tests/test_pdf_preview_route.py` | línea 18 | MEDIO |
| Fallback y coincidencias manuales de etiquetas | `backend/app/services/pdf_generator.py` | `_ancla_directa`, línea 177 | ALTO |
| Coordinadas manuales sin mapa visual aprobado | `backend/app/services/pdf_layout.py` | `PUESTA_DISPOSICION`, línea 3 | ALTO |
| Plantilla con objetos apuntadores inválidos | `backend/app/assets/iph-delitos.pdf` | pypdf, lectura PDF | MEDIO |
| Formulario abre asistente de anexos automáticamente | `frontend/src/views/modulos/PuestaDisposicionForm.vue` | `abrirAutomaticamenteUnaVez` | MEDIO |
| Navegador perdió varias páginas durante automatización | Navegador/Playwright integrado | No aplica | MEDIO |
| Validación de firmas incompleta para tipos no-image | `backend/app/blueprints/iph/routes.py` | `subir_adjunto`, línea 1056 | ALTO |
| CORS y secretos con valores por defecto | `backend/app/config.py` | `Config`, líneas 1-52 | CRÍTICO |
| Detalle técnico SQL puede devolverse al cliente | `backend/app/blueprints/auth/routes.py` | `login`, línea 144 | ALTO |

## 14. Archivos y funciones involucrados

- `backend/app/services/pdf_layout.py`: coordenadas calibrables.
- `backend/app/services/pdf_generator.py`: generación, anclas y fallback.
- `backend/app/blueprints/iph/routes.py`: capturas, adjuntos y rutas PDF.
- `backend/app/models/iph.py`: modelos de IPH y tablas web.
- `backend/tests/test_pdf_preview_route.py`: prueba PDF.
- `frontend/src/views/FormularioIPHView.vue`: lectura de campos y vista previa.
- `frontend/src/views/modulos/PuestaDisposicionForm.vue`: captura y anexos.
- `frontend/src/views/modulos/AnexosPantalla.vue`: asistente de anexos.
- `frontend/src/store/capturas.js`: almacenamiento de capturas.
- `frontend/src/store/attachments.js`: anexos.
- `backend/app/assets/iph-delitos.pdf`: plantilla oficial.

## 15. Riesgos de posibles correcciones

- Añadir una FK al modelo puede requerir una migración real.
- Cambiar coordenadas sin una plantilla aprobada puede desplazar todos los campos.
- Reparar la plantilla puede alterar páginas oficiales.
- Cambiar el procesamiento de anexos puede rechazar archivos legítimos.
- Reducir CORS puede bloquear orígenes legítimos no identificados.
- Exigir secretos puede impedir el arranque si no se configura producción.

## 16. Pruebas pendientes

- Completar el guardado persistente de la captura de 2183.
- Recargar el formulario y verificar todos los campos.
- Subir, listar, descargar y eliminar archivos ficticios.
- Completar anexos Sí/No y persistencia.
- Navegar por todos los módulos.
- Probar editar y volver a guardar.
- Probar finalización y exportación PDF final.
- Convertir las 15 páginas originales a imágenes.
- Comparar visualmente las coordenadas calibradas.
- Probar textos largos, fecha, hora, acentos y casillas.
- Comparar vista previa y descarga.
- Ejecutar transcripción real con audio ficticio.
- Probar 429, memoria y limpieza temporal.
- Probar persistencia después de reiniciar contenedores.
- Verificar todos los roles y permisos.

## 17. Plan de corrección por etapas

### Fase 1: seguridad

- Exigir secretos JWT desde entorno.
- Configurar CORS con allowlist.
- Dejar detalles SQL únicamente en logs.
- Confirmar roles y privilegios.

### Fase 2: esquema y persistencia

- Revisar DDL real completo.
- Confirmar relaciones entre IPH y las tablas web.
- Definir si `IPHCaptura.iph_id` tendrá FK o solo integridad aplicada por ruta.
- Ejecutar pruebas sobre una copia/base aislada.

### Fase 3: PDF

- Convertir todas las páginas de la plantilla a imágenes.
- Construir una tabla visual aprobada Campo Vue/Backend/Página/Coordenadas.
- Añadir una configuración declarativa por campo y anexo.
- Añadir marcos de depuración opcionales.
- Reducir fuentes, ajustar ancho y controlar desbordamiento sin recortar.
- Reparar o sustituir la plantilla si las advertencias indican daño.

### Fase 4: flujo funcional

- Reparar la reapertura automática del modal solo si crea confusión.
- Completar persistencia y recarga de módulos.
- Completar anexos y adjuntos.
- Ejecutar pruebas de voz y PDF end-to-end.

### Fase 5: regresión

- Ejecutar pruebas unitarias dentro del contenedor.
- Ejecutar pruebas de integración con datos ficticios.
- Verificar descarga y vista previa.
- Verificar persistencia después de reinicio.
- Confirmar que no se modifica el sistema legacy.

## 18. Resultado resumido

| Área | Estado |
|---|---|
| Docker | FUNCIONA |
| Frontend login/panel | FUNCIONA |
| Navegación autenticada | PARCIAL |
| Creación IPH | FUNCIONA |
| Captura persistente | NO COMPLETADA |
| Anexos | PARCIAL |
| Voz | NO COMPLETADA |
| SQL Server lectura | FUNCIONA |
| Tablas web | FUNCIONAN/EXISTEN |
| Generación PDF | PARCIAL |
| Inspección visual PDF | NO COMPLETADA |
| Prueba automatizada PDF | FALLA |

El hallazgo principal del PDF no es que el documento no se genere: el PDF se genera y contiene texto. El riesgo principal es que las coordenadas manuales pueden no corresponder exactamente con los espacios oficiales y que faltan una inspección visual completa y una correspondencia aprobada para todos los campos.
