# mesos un: ufradm
# mesos pw: RFUmda#1

import pandas as pd

import requests as rt
import sqlalchemy

import config

from sqlalchemy.engine import URL
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

proxies = config.get_proxies_dict()

url = 'http://usrv-mesosm1:8080/v2' + '/apps' + '/ufr-rctariff-services/middle/settings'


def is_service_updating_now(app_address_id: str) -> bool:
    """
    Проверить, обновляется ли сервис сейчас.

    :param app_address_id: ID приложения вида '/ufr-rctariff-services/middle/settings'
    :return: логическое значение, ответ на вопрос "Перезагружается ли сервис сейчас?"
    """

    marathon_app_url = 'http://usrv-mesosm1:8080/v2' + '/apps' + app_address_id
    deployments = rt.get(marathon_app_url).json()['app']['deployments']

    if not deployments:
        return False
    return True


# resp = rt.get(url).json()
# print(is_service_updating_now(resp['app']['deployments']))
# print(*resp.items(), sep='\n')
# print(resp['deployments'])

# for app in resp['apps']:
#     if 'settings' in app['id']:
#         example_app = app

# example_app = resp['apps'].pop()
# # print(*example_app.items(), sep='\n')
# # print(example_app)
#
# deployments = rt.get(url + 'deployments').json()
# print(deployments)
#
# version = example_app['version']
# print(version)
#
# Рестарт
restart_responce = rt.post(
    # /v2/apps/{app_id}/restart
    url + '/apps' + '/ufr-rctariff-services/middle/settings/restart',
    # data={
    #     'app_id': '/ufr-rctariff-services/middle/settings'
    # },
    # proxies=proxies,
    # verify=False
)

print(restart_responce.status_code)
print(restart_responce.json())


# --  Способ подключения 1: через connection_string  --
# conn_st = config.get_connection_string(what_for='sqlalchemy', server='OSSKTBAPP1', db='RC')
# mssql+pyodbc://OSSKTBAPP1/RC?trusted_connection=yes&driver=ODBC+Driver+13+for+SQL+Server&user=rc_site_user&password=xUgDFVHd*qHfh10!&encrypt=no
# print(conn_st)

# with create_engine(conn_st).connect() as connection:
#     query = "SELECT sAddressID FROM RC.dbo.MarathonApps WHERE sAlias = 'TARS';"
#     df = pd.read_sql_query(query, connection)


# --  Способ подключения 2: через URL-объект  --
# url_object = URL.create(
#     drivername="mssql+pyodbc",
#     username="rc_site_user",
#     password="xUgDFVHd*qHfh10!",  # plain (unescaped) text
#     host="OSSKTBAPP1",
#     port=1433,  # наш SQL-сервер обрабатывает запросы на этом порту
#     database="RC",
#     query={
#         "driver": "ODBC Driver 13 for SQL Server",
#         # "TrustServerCertificate": "yes",
#         # "authentication": "ActiveDirectoryIntegrated",
#     },
# )


def get_app_address_id_from_db(alias: str) -> str:
    """
    Получить значение sAddressID по элиасу из БД.

    :param alias: код сервиса (элиас) - слово из заглавных латинских букв
    :return: адрес сервиса
    """

    engine = create_engine(
        config.get_sqlalchemy_connection_url(host='OSSKTBAPP1', db='RC'),
        echo=False
    )

    metadata = sqlalchemy.MetaData()
    metadata.reflect(bind=engine)

    apps_table = metadata.tables['MarathonApps']

    sql_select_query = select(apps_table).where(apps_table.c.sAlias == "TARS")

    apps_ids = []
    with Session(engine) as session:
        for row in session.execute(sql_select_query):
            apps_ids.append(row.sAddressID)

    if not apps_ids:
        return "NOT FOUND"
    return apps_ids[0]


app_address_id = get_app_address_id_from_db('TARS')
# print(app_address_id)

resp = rt.get(url).json()
print(is_service_updating_now(app_address_id))
