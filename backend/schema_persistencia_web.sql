/* Ejecutar una vez en la base IPH configurada antes de desplegar este backend.
   La tabla de capturas se crea con la migración sqlserver/001_create_iph_capturas_web.sql,
   que deriva iph_id del tipo real de dbo.IPH.ID_IPH y define la clave foránea. */

IF OBJECT_ID(N'dbo.iph_estado_web', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.iph_estado_web (
        iph_id INT NOT NULL CONSTRAINT PK_iph_estado_web PRIMARY KEY,
        estado NVARCHAR(20) NOT NULL CONSTRAINT DF_iph_estado_web_estado DEFAULT N'EN_TRAMITE',
        actualizado_en DATETIME2 NOT NULL CONSTRAINT DF_iph_estado_web_actualizado DEFAULT SYSUTCDATETIME(),
        CONSTRAINT CK_iph_estado_web_estado CHECK (estado IN (N'EN_TRAMITE', N'ACTIVA', N'TERMINADA', N'CANCELADA'))
    );
END;

IF OBJECT_ID(N'dbo.iph_adjuntos_web', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.iph_adjuntos_web (
        id NVARCHAR(100) NOT NULL CONSTRAINT PK_iph_adjuntos_web PRIMARY KEY,
        iph_id INT NOT NULL,
        anexo NVARCHAR(80) NOT NULL,
        nombre NVARCHAR(255) NOT NULL,
        mime_type NVARCHAR(100) NOT NULL,
        tamano BIGINT NOT NULL,
        contenido VARBINARY(MAX) NOT NULL,
        creado_en DATETIME2 NOT NULL CONSTRAINT DF_iph_adjuntos_web_creado DEFAULT SYSUTCDATETIME()
    );
    CREATE INDEX IX_iph_adjuntos_web_iph_id ON dbo.iph_adjuntos_web(iph_id);
END;
