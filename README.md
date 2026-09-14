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

Ya están implementados en el backend (modelos + endpoints genéricos) y en
el frontend solo se hicieron **dos módulos de ejemplo completos**
(`ConocimientoHechoForm.vue` y `DenuncianteForm.vue`) para que sirvan de
plantilla: uno para módulos de un solo registro, otro para listas
repetibles. Los demás módulos se agregan copiando ese patrón y
registrándolos en `componentesPorModulo` dentro de `FormularioIPHView.vue`.

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

**Importante:** los modelos en `app/models/` (`Usuario`, `IPH`,
`ConocimientoHecho`, etc.) están definidos con nombres de tabla en
español que probablemente **no coincidan exactamente** con el esquema
real ya existente en tu SQL Server. Antes de usarlos en producción:

1. Comparte el diccionario de datos / DDL de las tablas reales.
2. Ajusta `__tablename__` y las columnas en `app/models/iph.py` y
   `app/models/user.py` para que mapeen 1 a 1 con tu esquema.
3. Si las tablas ya existen y no quieres que Flask-Migrate intente
   crearlas, usa `db.Model` con `__table_args__ = {"extend_existing": True}`
   o genera las migraciones con `flask db migrate` y revísalas antes de
   aplicarlas (`flask db upgrade`).

## Generación del PDF

`app/services/pdf_generator.py` genera actualmente un PDF **nuevo**
(con ReportLab) que reproduce el orden y las secciones del formato
oficial IPH2019, a partir de los datos capturados.

Si en vez de eso necesitas **rellenar exactamente la plantilla oficial**
(`IPH-DELITOS.pdf`) que compartiste — por ejemplo, si resulta tener
campos de formulario reales (AcroForm) —, se puede cambiar el enfoque a
usar `pypdf` para llenar esos campos directamente sobre la plantilla.
Dime si el PDF que usarán en producción tiene campos rellenables o es
una plantilla plana/escaneada, y ajusto ese servicio.

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
2. Decidir si el PDF final debe ser el formato oficial rellenado
   (AcroForm) o el generado (ReportLab) — o una combinación.
3. Completar los 12 módulos de formulario restantes siguiendo el patrón
   de los dos ejemplos ya incluidos.
4. Definir roles/permisos (ej. investigador vs. supervisor) si el
   sistema lo requiere — la tabla `Usuario` ya tiene un campo `rol`
   listo para eso.
