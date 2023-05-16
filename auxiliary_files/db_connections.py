from spring_config import ClientConfigurationBuilder
from spring_config.client import SpringConfigClient

import sqlalchemy
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

config = (
    ClientConfigurationBuilder()
    .app_name("ossktb-tgbot-python")  # config file
    .address("http://ossktbapprhel1/ossktb-rcsite-settings/")
    .profile("prelive")
    .build()
)

conf = SpringConfigClient(config).get_config()


def get_connection_string(what_for='sqlalchemy', server='bpdb', db='master'):
    if what_for == 'sqlalchemy':
        connection_string = f'mssql+pyodbc://{server}/{db}?' + \
                            'trusted_connection=yes' + \
                            '&driver=ODBC+Driver+13+for+SQL+Server' + \
                            '&user=' + conf['db']['db_user'] + \
                            '&password=' + conf['db']['db_pass'] + \
                            '&encrypt=no'
    elif what_for == 'pyodbc':
        connection_string = 'DRIVER={SQL Server};' + \
                            f'Server={server};' + \
                            f'Database={db};' + \
                            'UID=' + conf['db']['db_user'] + ';' + \
                            'PWD=' + conf['db']['db_pass'] + ';' + \
                            'encrypt=no'
    return connection_string


def get_pyodbc_connection_string(host: str = 'bpdb', db: str = 'master') -> str:
    connection_string = 'DRIVER={SQL Server};' + \
        f'Server={host};' + \
        f'Database={db};' + \
        'UID=' + conf['db']['db_user'] + ';' + \
        'PWD=' + conf['db']['db_pass'] + ';' + \
        'encrypt=no'
    return connection_string


def get_connection_url(host: str = 'OSSKTBAPP1', db: str = 'master') -> URL:
    # URL template: dialect+driver://username:password@host:port/database
    # url_object example:  mssql  +pyodbc://rc_site_user:xUgDFVHd*qHfh10!@bpdb:1433/master?driver=ODBC+Driver+13+for+SQL+Server
    url_object = URL.create(
        drivername="mssql+pyodbc",
        username=conf['db']['db_user'],
        password=conf['db']['db_pass'],  # plain (unescaped) text
        host=host,
        port=1433,  # наш SQL-сервер обрабатывает запросы на этом порту
        database=db,
        query={"driver": "ODBC Driver 13 for SQL Server"}
    )
    return url_object