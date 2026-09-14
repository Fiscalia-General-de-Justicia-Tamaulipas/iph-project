from flask import Flask
from app.config import config_by_name
from app.extensions import db, migrate, jwt, cors, bcrypt
import os


def create_app(config_name=None):
    config_name = config_name or os.getenv("FLASK_ENV", "production")
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    # Registrar blueprints
    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.iph.routes import iph_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(iph_bp, url_prefix="/api/iph")

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app
