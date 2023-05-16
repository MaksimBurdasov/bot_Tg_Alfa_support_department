DECLARE @SPID int;
DECLARE @sql NVARCHAR(100);
SET @SPID = 75  -- указать номер процесса для остановки
SET @sql = 'KILL ' + CONVERT(varchar(10), @SPID);
EXEC (@sql)