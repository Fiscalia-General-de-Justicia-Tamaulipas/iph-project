"""
Script para crear un usuario administrador inicial.
Uso (dentro del contenedor o entorno virtual):
    python seed_admin.py
"""
from app import create_app
from app.extensions import db
from app.models.user import Usuario

app = create_app()

with app.app_context():
    if Usuario.query.filter_by(usuario="admin").first():
        print("El usuario 'admin' ya existe.")
    else:
        admin = Usuario(
            nombre_completo="Administrador del Sistema",
            correo="admin@fiscalia.tamaulipas.gob.mx",
            usuario="admin",
            cargo="Administrador",
            adscripcion="Fiscalía General de Justicia de Tamaulipas",
            rol="admin",
        )
        admin.set_password("CambiaEstaPassword123!")
        db.session.add(admin)
        db.session.commit()
        print("Usuario 'admin' creado con contraseña temporal: CambiaEstaPassword123!")
