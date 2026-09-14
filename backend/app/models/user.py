from app.extensions import db, bcrypt
from datetime import datetime


class Usuario(db.Model):
    """
    Tabla de usuarios para inicio de sesión.
    AJUSTA __tablename__ y columnas si en la base de datos ya existente
    esta tabla tiene otro nombre/estructura.
    """
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    usuario = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    cargo = db.Column(db.String(100))          # ej. "Policía Investigador"
    adscripcion = db.Column(db.String(150))    # ej. "Segunda Unidad General de Investigación en Victoria"
    rol = db.Column(db.String(50), default="investigador")  # investigador, supervisor, admin
    activo = db.Column(db.Boolean, default=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, raw_password):
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password):
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre_completo": self.nombre_completo,
            "correo": self.correo,
            "usuario": self.usuario,
            "cargo": self.cargo,
            "adscripcion": self.adscripcion,
            "rol": self.rol,
        }
