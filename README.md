# IPH - Informe Policial Homologado (Sistema Web)

Aplicación web para captura, por módulos, del **Informe Policial
Homologado (IPH2019)** y su **exportación a PDF**, con inicio de sesión.

## Stack

- **Backend:** Python + Flask, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Migrate
- **Base de datos:** SQL Server (ya existente, en otro servidor) vía `pyodbc` / `mssql+pyodbc`
- **Frontend:** Vue 3 (Composition API) + Vite + Tailwind CSS + Pinia + Vue Router
- **Generación de PDF:** ReportLab (ver nota abajo)
- **Contenedores:** Docker + docker-compose

## Estructura del proyecto

```
iph-project/
├── docker-compose.yml
├── .env.example                 # copia a .env y ajusta tus credenciales de SQL Server
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── wsgi.py                  # punto de entrada (gunicorn)
│   ├── seed_admin.py            # crea un usuario admin inicial
│   └── app/
│       ├── __init__.py          # app factory
│       ├── config.py            # arma la cadena de conexión a SQL Server
│       ├── extensions.py        # db, jwt, cors, bcrypt, migrate
│       ├── models/
│       │   ├── user.py          # tabla de usuarios (login)
│       │   └── iph.py           # IPH + los 14 módulos del panel
│       ├── blueprints/
│       │   ├── auth/routes.py   # /api/auth/login, /registro, /perfil
│       │   └── iph/routes.py    # /api/iph/... (CRUD + exportar-pdf)
│       └── services/
│           └── pdf_generator.py # arma el PDF a partir de los datos capturados
└── frontend/
    ├── Dockerfile
    ├── nginx.conf
    ├── vite.config.js
    ├── tailwind.config.js
    └── src/
        ├── main.js / App.vue
        ├── router/index.js      # rutas + guardia de autenticación
        ├── store/
        │   ├── api.js            # axios con interceptor de JWT
        │   └── auth.js           # store Pinia de sesión
        └── views/
            ├── LoginView.vue
            ├── PanelView.vue          # listado de folios IPH
            ├── FormularioIPHView.vue  # panel de módulos (igual al mockup)
            └── modulos/
                ├── ConocimientoHechoForm.vue  # ejemplo: módulo de UN registro
                └── DenuncianteForm.vue        # ejemplo: módulo de LISTA repetible
```

## Módulos del formulario (según el panel proporcionado)

| Módulo | Tipo | Modelo backend |
|---|---|---|
| Conocimiento de Hecho | único | `ConocimientoHecho` |
| Acta de Noticia | único | `ActaNoticia` |
| Acciones Realizadas | lista | `AccionRealizada` |
| Denunciante | lista | `Denunciante` |
| Ofendido | lista | `Ofendido` |
| Víctima | lista | `Victima` |
| Policías | lista | `PolicíaActuante` |
| Imputado | lista | `Imputado` |
| Testigo | lista | `Testigo` |
| Inspección de Lugar | único | `InspeccionLugar` |
| Inspección de Persona | lista | `InspeccionPersona` |
| Inspección de Vehículos | lista | `InspeccionVehiculo` |
| Narración del Primer Respondiente | único | `NarracionPrimerRespondiente` |
| Actuaciones | lista | `Actuacion` |

Los módulos se guardan en el servidor. Las pantallas que aún no tienen una
tabla legacy confirmada usan `iph_capturas_web`, que conserva el JSON completo
de cada pantalla; los archivos se guardan en `iph_adjuntos_web` como
`VARBINARY(MAX)`. `iph_estado_web` conserva el estado del flujo web sin cambiar
los códigos de estado de la aplicación legacy. El navegador migra al servidor
los borradores y adjuntos que ya existían localmente cuando se vuelven a abrir.
Las imágenes aceptadas son JPG, JPEG, BMP y PNG; la pantalla de puesta a
disposición también admite PDF, DOC/DOCX, MP3/WAV y MP4/MPEG/MPG. El límite por
archivo es 50 MB.

Antes de desplegar esta versión, ejecuta una vez
[`backend/schema_persistencia_web.sql`](backend/schema_persistencia_web.sql)
en la base SQL Server configurada para crear las tablas de estado y adjuntos.
Para `iph_capturas_web`, ejecuta siempre la migración SQL Server indicada
abajo; esta usa el tipo real de `dbo.IPH.ID_IPH` y crea la clave foránea
correcta sin modificar la tabla legacy.

Ejecuta la migración idempotente
[`backend/migrations/sqlserver/001_create_iph_capturas_web.sql`](backend/migrations/sqlserver/001_create_iph_capturas_web.sql)
en la base indicada por `DB_NAME` (o `DATABASE` en
`SQLALCHEMY_DATABASE_URI`) del backend que sirve la aplicación. Por ejemplo:

```bash
sqlcmd -S <servidor>,<puerto> -d <DB_NAME> -U <usuario> \
  -i backend/migrations/sqlserver/001_create_iph_capturas_web.sql
```

Verifica en esa misma conexión antes de probar el guardado:

```sql
SELECT DB_NAME() AS base_actual,
       OBJECT_ID(N'dbo.iph_capturas_web', N'U') AS tabla_capturas;
```

`tabla_capturas` debe tener un valor no nulo. El modelo usa explícitamente
`dbo.iph_capturas_web`; si la tabla está en otra base o esquema, corrige la
conexión o aplica la migración a la base configurada, no cambies el modelo para
ocultar esa diferencia.

La ruta legacy existente busca el registro por `IPH.ID_IPH`; por ello el modelo
ORM conserva el atributo Python `id` pero lo mapea a la columna SQL `ID_IPH`.
La migración lee el tipo real de esa columna desde `sys.columns` y crea
`iph_capturas_web.iph_id` con ese mismo tipo antes de añadir la clave foránea.
Para confirmar el tipo usado por el ORM (`Integer`), la única comprobación
adicional necesaria es:

```sql
SELECT TYPE_NAME(system_type_id) AS tipo, max_length, precision, scale
FROM sys.columns
WHERE object_id = OBJECT_ID(N'dbo.IPH', N'U')
  AND name = N'ID_IPH';
```

El resultado debe ser `int`; si difiere, ajusta `db.Integer` en el modelo al
tipo SQL correspondiente. La migración se detiene si no encuentra
`dbo.IPH.ID_IPH` o si su tipo no es compatible.

Para verificar el caso reportado, abre
`http://localhost:8080/iph/1069/puesta_disposicion`, guarda la captura y
confirma que la respuesta `PUT /api/iph/1069/capturas/puesta_disposicion`
sea `200`. Después pulsa **VISTA PREVIA PDF**; debe abrirse otra pestaña con el
PDF actualizado de esa pantalla. Si la tabla sigue ausente, la aplicación
registra el nombre de la base y la tabla esperada en el log y muestra un
mensaje genérico en español, sin exponer trazas al usuario.

La prueba de ruta sin base de datos de integración se puede ejecutar desde
`backend/` con las dependencias del proyecto:

```bash
SQLALCHEMY_DATABASE_URI=sqlite:// PYTHONPATH=. python -m unittest tests.test_pdf_preview_route -v
```

La prueba autentica una petición `POST /api/iph/2110/previsualizar-pdf` sin
capturas y verifica estado `200`, encabezado PDF y lectura válida del documento.

## Conexión a SQL Server (base de datos existente)

Todo se configura en `.env` (copia `.env.example`):

```
DB_DRIVER=ODBC Driver 17 for SQL Server
DB_SERVER=IP_O_HOST_DEL_SERVIDOR
DB_PORT=1433
DB_NAME=NOMBRE_DE_TU_BASE
DB_USER=usuario
DB_PASSWORD=contraseña
```

`app/config.py` arma automáticamente la cadena de conexión
`mssql+pyodbc://...` a partir de esas variables. El Dockerfile del
backend ya instala el **driver ODBC 17 de Microsoft** necesario para que
`pyodbc` pueda conectarse.

**Importante:** las tablas de captura/adjuntos/estado nuevas se pueden crear
con el script anterior. Los modelos legacy en `app/models/` (`Usuario`, `IPH`,
`ConocimientoHecho`, etc.) todavía requieren validación contra el DDL real de
la base institucional para confirmar que nombres, columnas y tipos coinciden.
Antes de activar esos módulos en producción:

1. Comparte el diccionario de datos / DDL de las tablas reales.
2. Ajusta `__tablename__` y las columnas en `app/models/iph.py` y
   `app/models/user.py` para que mapeen 1 a 1 con tu esquema.
3. Si las tablas ya existen y no quieres que Flask-Migrate intente
   crearlas, usa `db.Model` con `__table_args__ = {"extend_existing": True}`
   o genera las migraciones con `flask db migrate` y revísalas antes de
   aplicarlas (`flask db upgrade`).

## Generación del PDF

`app/services/pdf_generator.py` usa como fondo `app/assets/iph-delitos.pdf`,
la plantilla oficial IPH2019, y superpone los datos persistidos y los cambios
que aún están en el formulario activo. Las cuatro páginas principales siempre
se conservan; cada anexo se agrega desde las páginas originales de la plantilla
cuando se marca para entrega o tiene datos capturados. Los valores que no
corresponden a un campo posicional conocido se imprimen en el área de escritura
de su sección.

El visor se actualiza durante la captura. El botón existente descarga la
versión parcial mientras el IPH no esté confirmado como terminado. Después de
confirmar, el mismo botón descarga el PDF final; el servidor rechaza
exportaciones finales anteriores a esa confirmación.

El botón **VISTA PREVIA PDF** está en la barra de referencia fija de cada
pantalla. Abre el PDF generado con los datos guardados y los campos actuales
de esa pantalla. Si falla, el motivo se muestra junto al botón y también se
registra el detalle técnico en el log del servidor.

### Verificación manual del flujo PDF

1. En un IPH activo, cambia un campo y verifica que el visor PDF muestre el
   nuevo valor; las áreas sin captura deben permanecer vacías y el diseño debe
   conservar las páginas de la plantilla adjunta.
2. Antes de finalizar, usa el botón PDF existente. Debe descargar la vista
   previa parcial. Una solicitud autenticada a `GET /api/iph/<id>/exportar-pdf`
   debe responder `409`.
3. Confirma **FINALIZAR IPH** y acepta la confirmación; vuelve a usar el
   mismo botón. Debe descargar el PDF final con la captura más reciente.
   Comprueba también fecha, hora de 24 horas, croquis y anexos seleccionados;
   el Anexo D debe conservar su advertencia de cadena de custodia.

## Cómo levantar el proyecto

```bash
cp .env.example .env
# edita .env con los datos reales de tu SQL Server

docker compose up --build
```

- Frontend: http://localhost:8080
- Backend / API: http://localhost:5000/api
- Health check: http://localhost:5000/api/health

### Crear usuario administrador inicial

```bash
docker compose exec backend python seed_admin.py
```

Esto crea el usuario `admin` con contraseña temporal
`CambiaEstaPassword123!` (cámbiala de inmediato).

### Migraciones (Flask-Migrate)

```bash
docker compose exec backend flask db init      # solo la primera vez
docker compose exec backend flask db migrate -m "estructura inicial"
docker compose exec backend flask db upgrade
```

## Próximos pasos sugeridos

1. Confirmarme el esquema real de la base de datos SQL Server para
   ajustar los modelos exactamente.
2. Incorporar la plantilla oficial del IPH para ajustar la salida PDF a
   su distribución exacta.
3. Completar los 12 módulos de formulario restantes siguiendo el patrón
   de los dos ejemplos ya incluidos.
4. Definir roles/permisos (ej. investigador vs. supervisor) si el
   sistema lo requiere — la tabla `Usuario` ya tiene un campo `rol`
   listo para eso.
