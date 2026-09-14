import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = 60 * 60 * 8  # 8 horas

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Conexión a SQL Server remoto (base de datos ya existente) ---
    DB_DRIVER = os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server")
    DB_SERVER = os.getenv("DB_SERVER", "localhost")
    DB_PORT = os.getenv("DB_PORT", "1433")
    DB_NAME = os.getenv("DB_NAME", "IPH_DB")
    DB_USER = os.getenv("DB_USER", "sa")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_TIMEOUT = os.getenv("DB_TIMEOUT", "15")
    DB_ENCRYPT = os.getenv("DB_ENCRYPT", "yes")
    DB_TRUST_SERVER_CERTIFICATE = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")

    # Si se define SQLALCHEMY_DATABASE_URI en el .env, se respeta tal cual.
    # De lo contrario, se arma automáticamente con los datos anteriores.
    _explicit_uri = os.getenv("SQLALCHEMY_DATABASE_URI")

    if _explicit_uri:
        SQLALCHEMY_DATABASE_URI = _explicit_uri
    else:
        _odbc_str = (
            f"DRIVER={{{DB_DRIVER}}};"
            f"SERVER={DB_SERVER},{DB_PORT};"
            f"DATABASE={DB_NAME};"
            f"UID={DB_USER};"
            f"PWD={DB_PASSWORD};"
            f"Connect Timeout={DB_TIMEOUT};"
            f"Encrypt={DB_ENCRYPT};"
            f"TrustServerCertificate={DB_TRUST_SERVER_CERTIFICATE};"
        )
        SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=" + quote_plus(_odbc_str)

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    PDF_OUTPUT_DIR = os.getenv("PDF_OUTPUT_DIR", os.path.join(os.path.dirname(__file__), "generated_pdfs"))

    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
}
