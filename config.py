from spring_config import ClientConfigurationBuilder
from spring_config.client import SpringConfigClient

import sqlalchemy
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

config = (
    ClientConfigurationBuilder()
    .app_name("ossktb-tgbot-python")  # config file
    .address("http://ossktbapprhel1/ossktb-rcsite-settings/")
    .profile("production")
    .build()
)

conf = SpringConfigClient(config).get_config()  # данные из .yaml-файла


def get_tg_url():
    """Сформировать ссылку подключения к Telegram."""
    return conf['tg']['bot_requests_url'] + conf['tg']['token'] + "/"


def get_proxies_dict() -> dict:
    """
    Получить словарь с указаными URL прокси-серверов из настроек.

    Эта функция вспомогательная, результат её работы используется в качестве параметра proxies
    в другой функции. А именно в requests.post()
    :return: словарь вида {'http': <прокси>, 'https': <прокси>}
    """

    url = f"http://{conf['proxy']['un']}:{conf['proxy']['pw']}@{conf['proxy']['ip']}:{conf['proxy']['port']}"
    return {'http': url, 'https': url}


def get_db_user():
    """Получить логин технического пользователя из настроек."""
    return conf['db']['db_user']


def get_db_pass():
    """Получить пароль технического пользователя из настроек."""
    return conf['db']['db_pass']


def get_pyodbc_connection_string(host: str = 'bpdb', db: str = 'master') -> str:
    """Сформировать строку подключения к БД."""
    connection_string = 'DRIVER={SQL Server};' + \
        f'Server={host};' + \
        f'Database={db};' + \
        'UID=' + conf['db']['db_user'] + ';' + \
        'PWD=' + conf['db']['db_pass'] + ';' + \
        'encrypt=no'
    return connection_string


def get_sqlalchemy_connection_url(host: str = 'OSSKTBAPP1', db: str = 'master') -> sqlalchemy.engine.URL:
    """
    Сформировать URL объект.

    URL объект - это экземпляр класса sqlalchemy.engine.URL.
    Он нужен для подключения к серверам с базами данных при помощи модуля sqlalchemy.
    :param host: название сервера ('OSSKTBAPP1' по умолчанию)
    :param db: название базы данных ('master' по умолчанию)
    :return: URL объект, который будет позже использован для создания объекта Engine
    """

    # sqlalchemy.engine.URL template: dialect+driver://username:password@host:port/database?<params>
    url_object = sqlalchemy.engine.URL.create(
        drivername="mssql+pyodbc",
        username=conf['db']['db_user'],
        password=conf['db']['db_pass'],  # plain (unescaped) text
        host=host,
        port=1433,  # наш SQL-сервер обрабатывает запросы на этом порту
        database=db,
        query={"driver": "ODBC Driver 13 for SQL Server"}
    )
    return url_object


def get_app_address_data_from_db(alias: str) -> tuple[str, str]:
    """
    Получить значение sAddressID по элиасу из БД.

    :param alias: код сервиса (элиас) - слово из заглавных латинских букв
    :return: адрес сервиса
    """

    engine = create_engine(
        get_sqlalchemy_connection_url(host='OSSKTBAPP1', db='RC'),
        echo=False
    )

    metadata = sqlalchemy.MetaData()
    metadata.reflect(bind=engine)

    apps_table = metadata.tables['MarathonApps']

    sql_select_query = select(apps_table).where(
        (apps_table.c.sAlias == alias) & (apps_table.c.bEnable == 1)
    )

    apps_ids = []
    with Session(engine) as session:
        for row in session.execute(sql_select_query):
            apps_ids.append((row.sHost, row.sAddressID))

    if not apps_ids:
        return "NOT", "FOUND"
    return apps_ids[0]


def get_allowed_tg_chat_ids() -> list[int]:
    """Получить список ID разрешённых чатов."""
    return conf['tg']['allowed_chats_ids']


def get_default_db_server(chat_id: int) -> str:
    """Получить название сервера, который в настройках указан дефолтным для данного чата."""
    all_chats = conf['tg']['allowed_chats']
    for _, chat_info in all_chats.items():
        if chat_info['chat_id'] == chat_id:
            return chat_info['default_server']
    else:
        return 'DEFAULT_SERVER_NOT_FOUND'
