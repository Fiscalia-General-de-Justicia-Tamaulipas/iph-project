# Auditoria Integral IPH

Fecha: 2026-11-23
Alcance: revision funcional segura del repositorio y de los contenedores existentes. No se modifico codigo ni configuracion.

## 1. Resumen ejecutivo

El proyecto tiene una arquitectura Docker operativa para backend Flask, frontend Vue/Nginx y un servicio independiente de voz. Los tres contenedores existentes estaban iniciados y reportaban estado healthy al momento de la revision.

Se pudo verificar el arranque, la pagina de inicio de sesion, el health de los servicios, el proxy API, la compilacion del frontend, la sintaxis Python y controles basicos de autenticacion.

No fue seguro ni posible realizar operaciones de autenticacion real, registro IPH, anexos, estado final, PDF ligado a base real o SQL Server, porque el sistema apunta a una base compartida y no existia una base local aislada identificada para pruebas de escritura. No se ejecutaron scripts SQL ni solicitudes de escritura.

## 2. Arquitectura encontrada

### Servicios

| Servicio | Tecnologia | Puerto/Expoicion | Comunicacion |
|---|---|---|---|
| frontend | Vue 3, Vite, Pinia, Vue Router, Nginx | `8080:80` | Proxy de `/api/` hacia `backend:5000` |
| backend | Flask, SQLAlchemy, JWT, Gunicorn | `5000:5000` | SQL Server compartido; voz en `http://voz:8000` |
| voz | Flask, Gunicorn, faster-whisper, ffmpeg | Solo red Docker | Recibe audio desde el backend |
| base de datos | SQL Server existente | Externa a Compose | Configurada por variables `.env` |

### Backend

- Factory Flask en `backend/app/__init__.py`.
- Blueprints:
  - autenticacion: `/api/auth/*`
  - IPH: `/api/iph/*`
  - voz: `/api/voz/*`
- El listado y la creacion usan SQL nativo/procedimientos almacenados existentes.
- Los modulos ORM complementarios usan SQLAlchemy.
- Las capturas web, estado web y adjuntos usan tablas `dbo` adicionales.

### Frontend

- Vue Router protege rutas no publicas mediante el token guardado en localStorage.
- Axios adjunta `Authorization: Bearer` a las solicitudes.
- Las pantallas de captura se encuentran en `frontend/src/views/modulos/`.
- Nginx usa `try_files` para Vue Router history y reenvia `/api/` al backend.

### Persistencia

- `dbo.IPH` es el registro legacy principal.
- Modelos ORM en `backend/app/models/iph.py` representan modulos legacy/adicionales.
- Tablas web requeridas:
  - `dbo.iph_capturas_web`
  - `dbo.iph_estado_web`
  - `dbo.iph_adjuntos_web`
- El modelo de adjuntos usa `VARBINARY(MAX)`.

## 3. Estado de Docker

`docker compose config` termino correctamente.

| Contenedor | Estado observado | Evidencia |
|---|---|---|
| `iph_backend` | Healthy, iniciado | Puerto `5000` |
| `iph_frontend` | Healthy, iniciado | Puerto `8080` |
| `iph_voz` | Healthy, iniciado | Modelo cargado; puerto interno `8000` |

El backend respondio `{"status":"ok"}` en `/api/health`. El frontend respondio HTML por `/`. El servicio de voz respondio `{"model_loaded":true,"status":"ok"}` en su endpoint `/health`.

El ruteo `/api/voz/health` desde Nginx no existe; el health directo es el endpoint interno del contenedor. No es un problema funcional de salud, pero la ruta externa no esta implementada.

## 4. Estado del frontend

Resultado observado:

- La pagina de login cargo correctamente en el navegador.
- El diseno responsive renderizo.
- Los campos vacios mostraron mensajes de validacion al intentar entrar.
- El boton de mostrar/ocultar contraseña esta disponible.
- El build de Vite termino correctamente.
- Existe una advertencia de Rollup por el tamaño del bundle, que supera 500 KB.

No pudieron verificarse panel, navegacion autenticada, modales, formularios IPH, botones de anexos ni PDF sin credenciales ni una base local aislada.

## 5. Estado del backend

Resultado observado:

- El health publico responde correctamente.
- Los campos obligatorios de login se validan con HTTP 400.
- Los endpoints protegidos rechazan solicitudes sin JWT con HTTP 401.
- El blueprint `/api/voz/transcribir` rechaza solicitudes sin JWT.
- La ruta de registro de usuarios responde HTTP 405: el alta se delega al sistema principal.
- El enum de rutas se obtuvo correctamente.

No se ejecuto autenticacion real ni CRUD de escritura.

## 6. Estado del servicio de voz

El health interno funciono y reporto modelo cargado.

Se verificaron respuestas controladas sin JWT e invalidas:

- Sin JWT: HTTP 401.
- Solicitud directa sin multipart: HTTP 400 con `audio_required`.
- Los limites 429/413/422/400 estan implementados en el codigo.

No se verificaron transcripcion real, concurrencia, consumo de memoria sostenido, 429 bajo carga ni limpieza bajo carga. No se uso audio sensible.

## 7. Resultados del registro IPH

| Comprobacion | Estado |
|---|---|
| Acceso al modulo | NO VERIFICADO |
| Creacion con datos ficticios | NO VERIFICADO |
| Validacion de campos | PARCIAL |
| Guardado y persistencia | NO VERIFICADO |
| Recuperacion | NO VERIFICADO |
| Edicion | NO VERIFICADO |
| Folios | NO VERIFICADO |
| Duplicados/perdidas | NO VERIFICADO |

La implementacion contiene rutas y validaciones, pero no se ejecuto contra una base aislada.

## 8. Resultados del modulo de anexos

No verificado funcionalmente. La implementacion permite subir, listar, descargar y eliminar archivos, valida extensiones basicas y limite de 50 MB. Las firmas de imagen JPG/JPEG/PNG/BMP se comprueban superficialmente.

No se verifico persistencia ni reinicio de contenedores por ausencia de base local aislada.

## 9. Resultados de generacion PDF

Existe la plantilla `backend/app/assets/iph-delitos.pdf`.

Prueba automatizada ejecutada dentro del contenedor backend:

- La prueba de vista previa sin captura no paso.
- Causa exacta: `StopIteration` al esperar una foreign key en `IPHCaptura.iph_id`.
- Evidencia: `next(iter(IPHCaptura.__table__.c.iph_id.foreign_keys))`.
- Impacto: el test detecta que el modelo no coincide con la relacion esperada por la migracion.

La prueba de pagina de Anexo A paso y valido pagina 7, texto de anexo y RND ficticio. ReportLab/pypdf emitieron advertencias de objetos incorrectos en la plantilla existente.

No se verificaron visualmente descarga, acentos, encabezados/pies, saltos ni integridad completa en una interfaz autenticada.

## 10. Resultados de SQL Server

No se conecto ni se verifico el esquema real. Se identificaron posibles inconsistencias:

- `Usuario` modela una tabla `usuarios`, mientras la autenticacion usa `cat_usuario`, `usuarios` y procedimientos almacenados.
- Los modulos ORM representan tablas propuestas que pueden no existir en el esquema institucional real.
- `IPHCaptura.iph_id` no tiene `ForeignKey` declarado en el modelo, aunque la migracion debe crearla.
- El registro principal usa columnas de forma legacy no validadas contra DDL real.
- No se verifico el tipo real de `dbo.IPH.ID_IPH`; la README advierte que debe ser `int`.

Escritura SQL prohibida por seguridad y sin base aislada. No se ejecuto ningun procedimiento de modificacion ni DDL.

## 11. Resultados de pruebas automatizadas

Se ejecutaron 17 comprobaciones manuales o automaticas principales:

| Tipo | Ejecuciones | Pasaron | Fallaron |
|---|---:|---:|---:|
| Docker/configuracion/red | 5 | 5 | 0 |
| Backend/API seguro | 5 | 5 | 0 |
| Voz/controlado | 3 | 3 | 0 |
| Frontend/build/navegador | 3 | 3 | 0 |
| Python/unittest/PDF | 3 | 1 | 2 |

El total resultante es **17 ejecutadas, 15 pasaron y 2 fallaron**.

Detalle de pruebas:

1. `docker compose config`: paso.
2. Estado de contenedores: paso.
3. Backend `/api/health`: paso.
4. Frontend `/`: paso.
5. Voz `/health` interno: paso.
6. Login sin datos: paso.
7. Endpoint IPH sin JWT: paso.
8. Voz sin JWT: paso.
9. Voz directa sin archivo: paso.
10. Voz directa con payload invalido: paso.
11. Build frontend: paso.
12. Sintaxis Python: paso.
13. Enumeracion de rutas Flask: paso.
14. Vista previa PDF sin captura: fallo.
15. Anexo PDF con plantilla original: paso.
16. Carga visual login: paso.
17. Validacion visual de campos vacios: paso.

Nota: el intento host de unittest fallo por falta de dependencias de Python en el host, no se considero una prueba fallida del proyecto. La prueba equivalente se ejecuto dentro del contenedor backend.

## 12. Hallazgos de seguridad

### CRITICO

No se identificaron fallos explotables confirmados sin credenciales ni una base aislada. Sin embargo, quedan riesgos de configuracion que deben corregirse antes de produccion:

- CORS permite `*` por defecto.
- Las claves por defecto `dev-secret` y `dev-jwt-secret` existen en el codigo si no son reemplazadas por variables.
- El login puede devolver `str(exc)` al cliente cuando falla la conexion SQL Server, mediante el campo `detalle`.
- No se confirmaron rate limits globales ni protecciones contra fuerza bruta.

### ALTO

- Los endpoints de anexos y modulos usan JWT, pero no se verifica un rol o privilegio por operacion.
- El endpoint de perfil vuelve a consultar tablas alternativas sin control de privilegio.
- El servicio de voz interno no exige JWT; solo su blueprint backend lo hace. Para ser robusto debe permanecer inaccesible fuera de la red Docker.
- Los archivos permitidos no validan firmas para PDF, DOC/DOCX, MP3/WAV y MP4/MPEG/MPG.
- Los mensajes de autenticacion pueden revelar si el usuario existe o si la contraseña es incorrecta a traves del procedimiento existente.

### MEDIO

- El endpoint `/api/auth/registro` publica el registro como 405.
- Los errores de login muestran mensajes distintos a usuarios invalidos y contraseñas incorrectas.
- `CORS_ORIGINS` puede ser una lista separada por comas, pero la practica predeterminada es permisiva.
- El frontend guarda JWT y datos de usuario en localStorage.
- Nginx usa un timeout largo de lectura y el backend tambien permite hasta 90 segundos de voz.

### BAJO

- Bundle frontend mayor a 500 KB.
- Se muestran advertencias de PDF al leer objetos de plantilla.
- Mensajes de consola de dependencias Requests dentro del contenedor.

## 13. Errores detectados

| ID | Error exacto | Archivo | Linea aproximada |
|---|---|---|---|
| ERR-01 | `StopIteration` en la prueba PDF al leer FK de `IPHCaptura.iph_id` | `backend/tests/test_pdf_preview_route.py` | 18 |
| ERR-02 | `RequestsDependencyWarning: urllib3/chardet mismatch` | Dependencia del contenedor backend | No aplica |
| ERR-03 | Advertencias `Ignoring wrong pointing object` al leer plantilla PDF | Motor pypdf | No aplica |
| ERR-04 | `/api/voz/health` publico devuelve 404 en Nginx | `frontend/nginx.conf` | `/api/` |

## 14. Archivos involucrados

- `backend/app/__init__.py`
- `backend/app/config.py`
- `backend/app/blueprints/auth/routes.py`
- `backend/app/blueprints/iph/routes.py`
- `backend/app/blueprints/voz/routes.py`
- `backend/app/models/iph.py`
- `backend/app/models/user.py`
- `backend/app/services/pdf_generator.py`
- `backend/voice_server.py`
- `backend/Dockerfile.voice`
- `backend/tests/test_pdf_preview_route.py`
- `frontend/nginx.conf`
- `frontend/src/router/index.js`
- `frontend/src/store/api.js`
- `frontend/src/store/auth.js`
- `frontend/src/views/LoginView.vue`
- `docker-compose.yml`
- `backend/app/assets/iph-delitos.pdf`

## 15. Tabla de hallazgos

| ID | Problema | Archivo | Prioridad | Impacto | Solucion recomendada |
|---|---|---|---|---|---|
| IPH-001 | Claves JWT por defecto conocidas | `backend/app/config.py` | CRITICO | Suplantacion de sesion si no se sobrescriben | Exigir secretos por entorno, validar configuracion al arrancar |
| IPH-002 | CORS permisivo por defecto | `backend/app/config.py` | CRITICO | Lectura o uso cruzado desde origen no autorizado | Configurar allowlist explicita |
| IPH-003 | Respuesta de login expone detalle tecnico de SQL | `backend/app/blueprints/auth/routes.py` | ALTO | Divulgacion de infraestructura | Mantener el detalle solo en logs |
| IPH-004 | No hay autorizacion por rol confirmada | Blueprints IPH/voz/anexos | ALTO | Usuarios podrian operar fuera de privilegio | Añadir politicas por rol y municipio/unidad |
| IPH-005 | Validacion incompleta de firmas de archivo | `backend/app/blueprints/iph/routes.py` | ALTO | Subida de archivos con contenido falso | Validar magic bytes y listas por pantalla |
| IPH-006 | Modelo de captura sin FK declarada | `backend/app/models/iph.py` | MEDIO | Riesgo de inconsistencia ORM/migracion | Añadir `ForeignKey("dbo.iph.ID_IPH")` si coincide el tipo real |
| IPH-007 | Esquema SQL Server no validado | `backend/app/models/*.py` | ALTO | CRUD puede fallar o apuntar a tablas incorrectas | Obtener DDL y ajustar modelos/mapeos |
| IPH-008 | Tablas web dependientes no creadas confirmadas | Migracion SQL Server | ALTO | Capturas, estado y adjuntos no persisten | Crear/aplicar migracion solo en base autorizada |
| IPH-009 | Credenciales compartidas no probadas | `.env`, configuracion Docker | ALTO | No se puede validar el flujo real | Crear base aislada y credenciales ficticias |
| IPH-010 | Bundle frontend superior a 500 KB | `frontend/src` | BAJO | Carga inicial mas lenta | Code splitting y lazy loading |
| IPH-011 | Advertencias de objetos PDF | Plantilla PDF/pypdf | MEDIO | Posible integridad visual imperfecta | Reparar/verificar la plantilla PDF y generar muestra visual |
| IPH-012 | `/api/voz/health` no expuesto | `frontend/nginx.conf` | MEDIO | Monitoreo externo incompleto | Añadir ruta health controlada o usar un healthcheck interno |

## 16. Solucion tecnica recomendada

1. Darle a IPH-001 e IPH-002 prioridad inmediata.
2. Obtener DDL real y crear una base local aislada antes de cualquier prueba de escritura.
3. Validar el esquema principal y los procedimientos almacenados.
4. Corregir el contrato ORM/migracion de `iph_capturas_web`.
5. Restringir autorizacion por rol, municipio y unidad.
6. Corregir validacion de adjuntos y no exponer detalles tecnicos.
7. Ejecutar nuevamente todas las pruebas funcionales con datos ficticios.
8. Revisar visualmente los PDFs y reparar la plantilla si persisten objetos invalidos.

## 17. Riesgos de cada solucion

- Cambiar permisos JWT puede bloquear usuarios sin un mapeo completo de roles.
- Cambiar CORS puede romper clientes moviles u orígenes legitimos no identificados.
- Ajustar tipos de clave puede requerir migracion o correccion del DDL real.
- Añadir validacion estricta de archivos puede rechazar formatos actualmente aceptados.
- Reparar la plantilla puede alterar la distribución oficial y requiere aprobación institucional.
- Crear tablas en SQL Server debe hacerse solo con autorización y contra una base aislada.

## 18. Pruebas que no pudieron realizarse

- Login real y JWT emitido por un usuario institucional.
- Creacion y persistencia ficticia del registro IPH.
- Duplicados y folios contra SQL Server.
- Edicion, borrado y recuperación de modulos.
- Subida, descarga y eliminación real de anexos.
- Persistencia tras reiniciar contenedores.
- Flujo completo de voz con audio real.
- 429 bajo carga y medida de memoria.
- Limpieza de temporales bajo carga.
- PDF autenticado, descarga visual y integridad de todas las paginas.
- Escritura de estado final y bloqueo de estados anteriores.
- Verificacion DDL de todas las tablas y procedimientos.
- Pruebas de navegacion autenticada y consola JavaScript.
- Prueba de expiracion JWT.
- Prueba de CORS desde origenes no autorizados.

## 19. Dependencias pendientes

- Base SQL Server local aislada o contenedor SQL Server autorizado.
- Credenciales ficticias para autenticacion.
- DDL o diccionario de datos real.
- Script/migracion autorizada para tablas web.
- Usuario y rol de prueba.
- Audios ficticios de corta duracion.
- Archivos ficticios para cada formato permitido.
- Plantilla oficial aprobada y datos PDF ficticios.
- Confirmacion de origenes CORS permitidos.
- Politica institucional de roles y permisos.

## 20. Plan de trabajo

### Fase 1: Seguridad y configuracion

- Problemas: IPH-001, IPH-002, IPH-003.
- Archivos: `backend/app/config.py`, `backend/app/blueprints/auth/routes.py`.
- Cambios: secretos obligatorios, CORS allowlist, eliminar detalles SQL de respuestas.
- Dependencias: lista de dominios y secretos de despliegue.
- Riesgos: bloqueo de origenes o usuarios mal configurados.
- Pruebas: inicio sin secretos debe fallar; CORS permitido/denegado; login no expone detalles.

### Fase 2: Preparacion segura de datos

- Problemas: IPH-007, IPH-008, IPH-009.
- Archivos: modelos, migraciones y scripts SQL autorizados.
- Cambios: comparar DDL, ajustar tipos/columnas, crear tablas solo en base aislada.
- Dependencias: DDL real y base local.
- Riesgos: incompatibilidad de tipos o claves foraneas.
- Pruebas: inspeccion de esquema, integracion ORM y migracion idempotente.

### Fase 3: Modelo ORM y captura

- Problemas: IPH-006.
- Archivos: `backend/app/models/iph.py`, migracion SQL Server.
- Cambios: declarar o retirar la relacion segun el esquema real.
- Dependencias: resultado de Fase 2.
- Riesgos: migracion que no sea compatible con el tipo real de `ID_IPH`.
- Pruebas: reconstruir base, guardar/listar captura, ejecutar unittest PDF.

### Fase 4: Permisos y anexos

- Problemas: IPH-004, IPH-005.
- Archivos: blueprints IPH/voz y frontend autorizado.
- Cambios: roles, municipio/unidad, firmas de archivo, validacion por anexo.
- Dependencias: politica institucional.
- Riesgos: rechazar formatos legitimos o bloquear operaciones validas.
- Pruebas: usuario autorizado/no autorizado, tipos falsos, limites y persistencia.

### Fase 5: Voz y operacion

- Problemas: IPH-012 y cobertura incompleta.
- Archivos: Docker Compose, Nginx y voz si se autoriza.
- Cambios: monitoreo externo seguro, prueba de carga y limites.
- Dependencias: audios ficticios y hardware representativo.
- Riesgos: bloqueo por transcripciones lentas o bajo memoria.
- Pruebas: formatos validos, 60 segundos, 10 MB, 429, health y memoria.

### Fase 6: PDF y UX

- Problemas: IPH-010, IPH-011.
- Archivos: plantilla, generador PDF y frontend.
- Cambios: reparar/verificar PDF, lazy loading y revision visual.
- Dependencias: plantilla oficial aprobada.
- Riesgos: cambio visual no homologado.
- Pruebas: PDF abre, tiene paginas esperadas, texto, acentos y anexos.

### Fase 7: Regresion integral

- Problemas de todas las fases.
- Archivos: todos los modificados.
- Cambios: ejecutar integracion completa sin datos reales.
- Dependencias: base aislada y usuario ficticio.
- Riesgos: duplicados o efectos secundarios en datos si no se mantiene el aislamiento.
- Pruebas: login, CRUD IPH, anexos, estado, PDF, voz, persistencia y reinicio.

## Estado funcional

| Funcionalidad | Estado | Evidencia | Observaciones |
|---|---|---|---|
| Docker Compose | FUNCIONA | Configuracion valida y tres contenedores iniciados/healthy | No se reconstruyeron imagenes durante esta auditoria |
| Frontend carga | FUNCIONA | HTTP 200 y navegador renderizo login | No se verifico toda la UX autenticada |
| Build frontend | FUNCIONA | Vite termino exitosamente | Advertencia de tamaño de bundle |
| Backend health | FUNCIONA | `{"status":"ok"}` | |
| JWT obligatorio | FUNCIONA | Endpoints protegidos devolvieron 401 sin token | Expiracion no verificada |
| Login de credenciales reales | NO VERIFICADO | Requiere base compartida/usuario ficticio | No se usaron credenciales reales |
| Registro IPH | NO VERIFICADO | Sin base aislada | No se hicieron escrituras |
| Modulos IPH | NO VERIFICADO | Sin base aislada | Implementacion parcialmente encontrada |
| Capturas web | NO VERIFICADO | Sin esquema migrado disponible | Ruta implementada |
| Anexos | NO VERIFICADO | Sin base aislada | No se hizo escritura |
| Voz health | FUNCIONA | `model_loaded:true` | |
| Voz transcripcion | NO VERIFICADO | Sin audio y sin credenciales | Se verifico salud y manejo invalidos |
| PDF Anexo A | FUNCIONA | Prueba automatizada paso | Solo Anexo A; plantilla emitio advertencias |
| PDF vista previa | FALLA | Prueba fallo por FK ausente en modelo | Puede requerir ajuste de migracion/modelo |
| SQL Server | NO VERIFICADO | Base compartida externa | Sin escritura ni lectura de schema |
