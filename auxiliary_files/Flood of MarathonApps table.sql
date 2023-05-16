-- ���������� ���������� � ������� � ������� RC.dbo.MarathonApps
BEGIN TRAN
	INSERT INTO	RC.dbo.MarathonApps (
		sAlias,      -- �������� �����������: NOT NULL � UNIQUE()
		sAppName,    -- �������� ����������� NOT NULL
		sAddressID,  -- �������� ����������� NOT NULL
		sHost        -- �������� ����������� NOT NULL
	)
	VALUES (
		'RCDS',
		'ufr-rcdeal-settings',
		'/ufr-rcdeal/middle/settings',
		'ufrmesosm1'
	)
ROLLBACK


-- ������ ���������
BEGIN TRAN
	UPDATE RC.dbo.MarathonApps
	SET sAppName = 'ufr-rcincomeusrv-tadeal-service'
	WHERE ID = 1 
ROLLBACK


-- �������� ����� ������� bEnable
-- 0 ������ ���������� ��� ��������, 1 - ����� ������������
BEGIN TRAN
	ALTER TABLE RC.dbo.MarathonApps ADD bEnable BIT NOT NULL DEFAULT 1;
ROLLBACK


BEGIN TRAN
	-- �������� ����� ������� 
	ALTER TABLE RC.dbo.MarathonApps ADD sHost NVARCHAR(50);

	-- ��������� ������� sHost ����������
	UPDATE RC.dbo.MarathonApps SET sHost = 'usrv-mesosm1' WHERE 1=1;

	-- �������� ����������� NOT NULL �� ������� sHost
	ALTER TABLE RC.dbo.MarathonApps ALTER COLUMN sHost NVARCHAR(50) NOT NULL;
ROLLBACK


-- ���������� ���������� �������
SELECT * FROM RC.dbo.MarathonApps;


-- ������ ��������� ����������� (������������ ��������):
--ALTER TABLE table_name
--ADD CONSTRAINT constraint_name 
--UNIQUE(column1, column2,...);
-- ����� �� �����: https://www.sqlservertutorial.net/sql-server-basics/sql-server-unique-constraint/


-- ������ ������ �� �������� �� ���������� NVARCHAR(50) ����?
-- ������: https://translated.turbopages.org/proxy_u/en-ru.ru.570cd10d-63ca547a-0c33ae4a-74722d776562/https/stackoverflow.com/questions/626899/how-do-you-change-the-datatype-of-a-column-in-sql-server


---- �������� ��� ������ � �������
--ALTER TABLE RC.dbo.MarathonApps 
--ALTER COLUMN sAlias NVARCHAR(50) NOT NULL;


---- ������� �������� � ������� �����������
--ALTER TABLE RC.dbo.MarathonApps ADD CONSTRAINT unique_alias UNIQUE(sAlias);

