/*
  Crea únicamente las tablas auxiliares de estado y adjuntos.
  La tabla de capturas se crea en migrations/sqlserver/001_create_iph_capturas_web.sql.
  En las tres tablas, iph_id es una referencia lógica a dbo.IPH.ID_IPH;
  no se agregan llaves foráneas ni se modifican objetos originales.
*/

IF ISNULL(DB_NAME(), N'') <> N'PGJ_NSJP'
    THROW 51000, N'Base de datos incorrecta. Este script solo puede ejecutarse en PGJ_NSJP.', 1;

SET XACT_ABORT ON;

BEGIN TRY
    BEGIN TRANSACTION;

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
    END;

    IF OBJECT_ID(N'dbo.iph_adjuntos_web', N'U') IS NOT NULL
       AND NOT EXISTS (
            SELECT 1
            FROM sys.indexes
            WHERE name = N'IX_iph_adjuntos_web_iph_id'
              AND object_id = OBJECT_ID(N'dbo.iph_adjuntos_web', N'U')
       )
        CREATE INDEX IX_iph_adjuntos_web_iph_id
            ON dbo.iph_adjuntos_web (iph_id);

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
