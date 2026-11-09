/*
  Crea únicamente la tabla auxiliar de capturas en la base configurada.
  iph_id conserva el valor de dbo.IPH.ID_IPH como referencia lógica;
  no se crea una llave foránea hacia la tabla original.
*/
SET XACT_ABORT ON;

IF ISNULL(DB_NAME(), N'') <> N'PGJ_NSJP'
    THROW 51000, N'Base de datos incorrecta. Este script solo puede ejecutarse en PGJ_NSJP.', 1;

BEGIN TRY
    BEGIN TRANSACTION;

    IF OBJECT_ID(N'dbo.iph_capturas_web', N'U') IS NULL
    BEGIN
        CREATE TABLE dbo.iph_capturas_web (
            id INT IDENTITY(1,1) NOT NULL
                CONSTRAINT PK_iph_capturas_web PRIMARY KEY,
            iph_id INT NOT NULL,
            pantalla NVARCHAR(80) NOT NULL,
            datos_json NVARCHAR(MAX) NOT NULL,
            actualizado_en DATETIME2 NOT NULL
                CONSTRAINT DF_iph_capturas_web_actualizado
                DEFAULT SYSUTCDATETIME(),
            CONSTRAINT uq_iph_captura_pantalla
                UNIQUE (iph_id, pantalla)
        );
    END;

    IF OBJECT_ID(N'dbo.iph_capturas_web', N'U') IS NOT NULL
       AND NOT EXISTS (
            SELECT 1
            FROM sys.indexes
            WHERE name = N'IX_iph_capturas_web_iph_id'
              AND object_id = OBJECT_ID(N'dbo.iph_capturas_web', N'U')
       )
        CREATE INDEX IX_iph_capturas_web_iph_id
            ON dbo.iph_capturas_web (iph_id);

    COMMIT TRANSACTION;
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0
        ROLLBACK TRANSACTION;

    THROW;
END CATCH;
