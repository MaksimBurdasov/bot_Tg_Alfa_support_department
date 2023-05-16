-- Добавление информации о сервисе в таблицу RC.dbo.MarathonApps
BEGIN TRAN
	INSERT INTO	RC.dbo.MarathonApps (
		sAlias,      -- наложены ограничения: NOT NULL и UNIQUE()
		sAppName,    -- наложено ограничение NOT NULL
		sAddressID,  -- наложено ограничение NOT NULL
		sHost        -- наложено ограничение NOT NULL
	)
	VALUES (
		'RCDS',
		'ufr-rcdeal-settings',
		'/ufr-rcdeal/middle/settings',
		'ufrmesosm1'
	)
ROLLBACK


-- Внести изменения
BEGIN TRAN
	UPDATE RC.dbo.MarathonApps
	SET sAppName = 'ufr-rcincomeusrv-tadeal-service'
	WHERE ID = 1 
ROLLBACK


-- Добавить новую колонку bEnable
-- 0 значит недоступно для рестарта, 1 - можно рестартовать
BEGIN TRAN
	ALTER TABLE RC.dbo.MarathonApps ADD bEnable BIT NOT NULL DEFAULT 1;
ROLLBACK


BEGIN TRAN
	-- Добавить новую колонку 
	ALTER TABLE RC.dbo.MarathonApps ADD sHost NVARCHAR(50);

	-- Заполнить колонку sHost значениями
	UPDATE RC.dbo.MarathonApps SET sHost = 'usrv-mesosm1' WHERE 1=1;

	-- Наложить ограничение NOT NULL на колонку sHost
	ALTER TABLE RC.dbo.MarathonApps ALTER COLUMN sHost NVARCHAR(50) NOT NULL;
ROLLBACK


-- Посмотреть содержимое таблицы
SELECT * FROM RC.dbo.MarathonApps;


-- Скрипт наложения ограничения (уникальность значений):
--ALTER TABLE table_name
--ADD CONSTRAINT constraint_name 
--UNIQUE(column1, column2,...);
-- Взято из стать: https://www.sqlservertutorial.net/sql-server-basics/sql-server-unique-constraint/


-- Почему скрипт не работает со значениями NVARCHAR(50) типа?
-- Статья: https://translated.turbopages.org/proxy_u/en-ru.ru.570cd10d-63ca547a-0c33ae4a-74722d776562/https/stackoverflow.com/questions/626899/how-do-you-change-the-datatype-of-a-column-in-sql-server


---- Изменить тип данных в колонке
--ALTER TABLE RC.dbo.MarathonApps 
--ALTER COLUMN sAlias NVARCHAR(50) NOT NULL;


---- Сделать значения в колонке уникальными
--ALTER TABLE RC.dbo.MarathonApps ADD CONSTRAINT unique_alias UNIQUE(sAlias);

