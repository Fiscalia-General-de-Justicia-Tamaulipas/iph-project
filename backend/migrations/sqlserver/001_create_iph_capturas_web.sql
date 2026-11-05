/*
  Run in the configured PGJ_NSJP database. The capture key uses the exact
  SQL Server type of dbo.IPH.ID_IPH so its foreign key remains compatible.
*/
SET XACT_ABORT ON;

DECLARE @iph_object_id INT = OBJECT_ID(N'dbo.IPH', N'U');
IF @iph_object_id IS NULL
    THROW 50001, 'No existe dbo.IPH en la base de datos actual.', 1;

DECLARE @pk_type SYSNAME;
DECLARE @pk_max_length SMALLINT;
DECLARE @pk_precision TINYINT;
DECLARE @pk_scale TINYINT;
DECLARE @pk_sql_type NVARCHAR(128);
DECLARE @pk_column_id INT;

SELECT
    @pk_column_id = c.column_id,
    @pk_type = TYPE_NAME(c.system_type_id),
    @pk_max_length = c.max_length,
    @pk_precision = c.precision,
    @pk_scale = c.scale
FROM sys.columns AS c
WHERE c.object_id = @iph_object_id
  AND c.name = N'ID_IPH';

IF @pk_type IS NULL
    THROW 50002, 'No existe dbo.IPH.ID_IPH; revise el esquema real de la tabla IPH.', 1;

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes AS i
    INNER JOIN sys.index_columns AS ic
        ON ic.object_id = i.object_id
       AND ic.index_id = i.index_id
    WHERE i.object_id = @iph_object_id
      AND i.is_primary_key = 1
      AND ic.column_id = @pk_column_id
      AND ic.key_ordinal = 1
      AND (
          SELECT COUNT(*)
          FROM sys.index_columns AS pk_columns
          WHERE pk_columns.object_id = i.object_id
            AND pk_columns.index_id = i.index_id
            AND pk_columns.key_ordinal > 0
      ) = 1
)
    THROW 50004, 'dbo.IPH.ID_IPH no es la clave primaria de dbo.IPH.', 1;

SET @pk_sql_type =
    CASE
        WHEN @pk_type IN (N'varchar', N'char', N'varbinary', N'binary')
            THEN @pk_type + N'(' + CASE WHEN @pk_max_length = -1 THEN N'max' ELSE CONVERT(NVARCHAR(10), @pk_max_length) END + N')'
        WHEN @pk_type IN (N'nvarchar', N'nchar')
            THEN @pk_type + N'(' + CASE WHEN @pk_max_length = -1 THEN N'max' ELSE CONVERT(NVARCHAR(10), @pk_max_length / 2) END + N')'
        WHEN @pk_type IN (N'decimal', N'numeric')
            THEN @pk_type + N'(' + CONVERT(NVARCHAR(10), @pk_precision) + N',' + CONVERT(NVARCHAR(10), @pk_scale) + N')'
        WHEN @pk_type IN (N'time', N'datetime2', N'datetimeoffset')
            THEN @pk_type + N'(' + CONVERT(NVARCHAR(10), @pk_scale) + N')'
        WHEN @pk_type IN (N'tinyint', N'smallint', N'int', N'bigint', N'uniqueidentifier')
            THEN @pk_type
        ELSE NULL
    END;

IF @pk_sql_type IS NULL
    THROW 50003, 'El tipo de dbo.IPH.ID_IPH no es compatible con esta migración.', 1;

IF OBJECT_ID(N'dbo.iph_capturas_web', N'U') IS NULL
BEGIN
    DECLARE @create_sql NVARCHAR(MAX) =
        N'CREATE TABLE dbo.iph_capturas_web (
            id INT IDENTITY(1,1) NOT NULL
                CONSTRAINT PK_iph_capturas_web PRIMARY KEY,
            iph_id ' + @pk_sql_type + N' NOT NULL,
            pantalla NVARCHAR(80) NOT NULL,
            datos_json NVARCHAR(MAX) NOT NULL,
            actualizado_en DATETIME2 NOT NULL
                CONSTRAINT DF_iph_capturas_web_actualizado DEFAULT SYSUTCDATETIME(),
            CONSTRAINT uq_iph_captura_pantalla UNIQUE (iph_id, pantalla),
            CONSTRAINT FK_iph_capturas_web_iph FOREIGN KEY (iph_id)
                REFERENCES dbo.IPH (ID_IPH)
        );';
    EXEC sys.sp_executesql @create_sql;
END
ELSE IF NOT EXISTS (
    SELECT 1
    FROM sys.foreign_keys
    WHERE parent_object_id = OBJECT_ID(N'dbo.iph_capturas_web', N'U')
      AND name = N'FK_iph_capturas_web_iph'
)
BEGIN
    ALTER TABLE dbo.iph_capturas_web
        ADD CONSTRAINT FK_iph_capturas_web_iph
        FOREIGN KEY (iph_id) REFERENCES dbo.IPH (ID_IPH);
END;

IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = N'IX_iph_capturas_web_iph_id'
      AND object_id = OBJECT_ID(N'dbo.iph_capturas_web', N'U')
)
    CREATE INDEX IX_iph_capturas_web_iph_id
        ON dbo.iph_capturas_web (iph_id);
