from sqlalchemy import create_engine, text
import pyodbc

import config

proxies = config.get_proxies_dict()
tg_url = config.get_tg_url()

# con_st = config.get_connection_string(server='bpdb')
# engine = create_engine(con_st)
#
# with engine.connect() as conn:
#     # conn.execute(text('kill 11111'))
#     # conn.commit()
#     conn.execute('select top 7 * from lm1.dbo.drType')


con_st = config.get_connection_string(what_for='pyodbc')
cn = pyodbc.connect(con_st, autocommit=True)

with cn:
    with cn.cursor() as cursor:
        try:
            cursor.execute('kill 543')
            cursor.commit()
        except pyodbc.ProgrammingError as er:
            print(str(er))
    data = cursor.fetchall()
    print(data)