import json

from typing import Union

import requests as req

from sqlalchemy import create_engine
import pyodbc
import pandas as pd

import os

import config

proxies = config.get_proxies_dict()
tg_url = config.get_tg_url()  # заготовка URL-адреса для запроса к Telegram

# словарь доступных команд
# выводится списком по команде /help
available_commands = {
    "help": "получить список доступных команд",
    "rep_FILE": "справка по созданию выгрузки",
    "show_sql_dir": "список доступных sql-скриптов",
    "kill_NUMBER": "справка по завершению процесса",
    'rst_APP': "справка по рестарту приложения",
}


def get_updates(params=None):
    return req.get(f'{tg_url}getUpdates', params=params, proxies=proxies, verify=False)


def relay_func(command: str, update_info: dict) -> None:
    """
    Выбрать и запустить реакцию (функцию) на указанную команду.

    :param command: команда в виде строки (без слэш)
    :param update_info: апдейт, который содержал эту команду
    :return: None
    """

    if command[-10:] == "@AlfaRCbot":
        command = command[:-10]

    if command in ('start', 'help'):
        start_command(update_info)
    elif command[:4] == 'rep_':
        report_command(command, update_info)
    elif command == 'show_sql_dir':
        show_sql_dir_command(update_info)
    elif command[:5] == 'kill_':
        kill_command(command, update_info)
    elif command[:4] == 'rst_':
        restart_command(command, update_info)
    else:
        say_command_not_found(command, update_info)


def is_command_from_allowed_chat(update: dict) -> bool:
    """
    Проверить необходимость обработки полученного события.

    :param update: информация о событии в виде словаря
    :return: логическое значение, ответ на вопрос "Если ли смысл обрабатывать событие?"
    """

    print("Запущена функция is_command_from_allowed_chat()..")  # TODO: delete

    allowed_chats = config.get_allowed_tg_chat_ids()

    print(f"Получено значение allowed_chats: {allowed_chats}..")  # TODO: delete

    # Проверка: связан ли аптейт с отправкой сообщения
    if 'message' not in update:
        print("В апдейте не обнаружено поле 'message'. Завершение is_command_from_allowed_chat()..")  # TODO: delete
        return False

    # Проверка: есть ли ID чата в разрешённых
    if update['message']['chat']['id'] not in allowed_chats:
        print("ID чата нет в разрешённых. Завершение is_command_from_allowed_chat()..")  # TODO: delete
        return False

    # Проверка: есть ли в сообщении что-то кроме текста (команды, приложения ...)
    # Нас интересуют только команды, при наличии они будут содержаться в 'entities'
    if 'entities' not in update['message']:
        print("В апдейте не обнаружено поле 'entities'. Завершение is_command_from_allowed_chat()..")  # TODO: delete
        return False
    print("ID чата УСПЕШНО прошло проверку..")  # TODO: delete
    return True


def extract_chat_id(update: dict) -> int:
    """Получить ID чата, целое число."""
    return update['message']['chat']['id']


def get_text_from_file(filename: str) -> str:
    """Вернуть содержимое текстового файла."""
    with open(filename, encoding="utf8") as f:
        text = f.read()
    return text


def send_text_message(chat_id: int, text: Union[str, bytes]) -> None:
    """Отправить сообщение в Telegram методом POST."""
    print("Запустилась функция send_text_message()..")  # TODO: delete
    data = {
        "chat_id": chat_id,
        "text": text,
        "headers": {'Content-type': 'text/plain; charset=utf-8'}
    }
    print("Функция send_text_message() сейчас будет пробовать отправить сообщение..")  # TODO: delete
    res = req.post(tg_url + 'sendMessage', data=data, proxies=proxies, verify=False)   # TODO: удалить переменную res
    print("Результат попытки отправить: ", end='')  # TODO: delete
    print(res.text.replace("'", '"').replace(''))  # TODO: delete


def send_document_to_chat(chat_id: int, file_path: str, caption: str = '') -> None:
    """Отправить документ в Telegram методом POST."""
    body = {
        "chat_id": chat_id,
        "caption": caption
    }
    files = {'document': open(file_path, "rb")}
    req.post(tg_url + 'sendDocument', data=body, files=files, proxies=proxies, verify=False)


def start_command(update_info: dict) -> None:
    """Отправить в чат список доступных команд."""
    print("Запустилась функция start_command()..")  # TODO: delete
    chat_id = update_info['message']['chat']['id']
    beginnings = [
        "Ты по какому вопросу?", "Не будем тратить время. Что тебе нужно?",
        "Я, в отличие от джина, могу исполнить больше трёх желаний. C чего начнём?"
    ]
    text = beginnings[int(update_info['update_id']) % len(beginnings)] + '\n\n\tДОСТУПНЫЕ КОМАНДЫ:'
    for cmd, description in available_commands.items():
        text += f'\n/{cmd} - {description}'
    print("Функция start_command() сформировала приветсвенный текст..")  # TODO: delete
    send_text_message(chat_id, text)


def check_report_command(command: str) -> str:
    """Проверить правильность записи команды rep."""
    err_text = 'Проблема в записи команды: '
    err_text_end = ' Узнай подробнее, выполнив /rep_FILE'

    if len(command) == 4:
        err_text += "команда должна содержать название файла после 'rep_'."
        return err_text + err_text_end

    cmd_head, sql_file_title = command[:4], command[4:]
    sql_file_title = 'sql_queries/' + sql_file_title + '.sql'

    if not os.path.exists(sql_file_title):
        err_text += f"в папке sql_queries/ файл '{sql_file_title}' не найден."
        return err_text + err_text_end

    return "ok"


def get_db_response_as_dataframe(chat_id: int, sql_file_name: str) -> pd.DataFrame:
    """Получить ответ от БД в виде датафрейма."""
    query = get_text_from_file('sql_queries/' + sql_file_name)

    default_server = config.get_default_db_server(chat_id)
    if sql_file_name == 'marathon_apps.sql':
        default_server = 'OSSKTBAPP1'

    url_object = config.get_sqlalchemy_connection_url(host=default_server)

    engine = create_engine(url_object)

    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection)

    return df


def make_excel_from_dataframe(df: pd.DataFrame, recording_file_title: str) -> None:
    """Записать датафрейм в .xlsx-файл с названием recording_file_title (уже содержит расширение)."""
    with pd.ExcelWriter(recording_file_title, mode='wb', engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False, engine='xlsxwriter')
        sheet = writer.sheets['Sheet1']
        # Настройка ширины колонок по самой длинной строке в столбце
        for col_ind, col in enumerate(df):
            series = df[col]
            widest_element_length = series.astype(str).map(len).max()  # размер наибольшего элемента
            column_title_width = len(str(series.name))  # размер названия колонки
            max_len = max((widest_element_length, column_title_width)) + 1  # дополнительный пробел
            sheet.set_column(col_ind, col_ind, max_len)  # установить ширину столбца
        sheet.set_column(4, 4, 40)


def report_command(command: str, update_info: dict) -> None:
    """Отправить выгрузку из БД в чат .xlsx-файлом."""
    chat_id = extract_chat_id(update_info)
    if command == 'rep_FILE':
        text = get_text_from_file('text_files/report_command_instruction.txt')
        send_text_message(chat_id, text)
        return None

    check_func_conclusion = check_report_command(command)
    if check_func_conclusion == 'ok':
        sql_file_name = command[4:] + '.sql'
        df = get_db_response_as_dataframe(chat_id, sql_file_name)
        make_excel_from_dataframe(df, command + '.xlsx')
        send_document_to_chat(chat_id, command + '.xlsx', caption='Выгрузка готова: ')
    else:
        send_text_message(chat_id, check_func_conclusion)


def check_kill_command(command: str) -> str:
    """Проверить правильность записи команды kill."""
    err_text = 'Проблема в записи команды: '
    err_text_end = ' Узнай подробнее, выполнив /kill_NUMBER'

    if len(command) == 5:
        err_text += "команда должна содержать номер процесса после 'kill_'."
        return err_text + err_text_end

    proc_number = command[5:]

    if not proc_number.isdigit():
        err_text += f"номер процесса может содержать только цифры."
        return err_text + err_text_end

    return "ok"


def kill_command(command: str, update_info: dict) -> None:
    """Прервать процесс и отправить статус выполнения команды в чат."""
    chat_id = extract_chat_id(update_info)
    if command == 'kill_NUMBER':
        text = get_text_from_file('text_files/kill_command_instruction.txt')
        send_text_message(chat_id, text)
        return None

    check_func_conclusion = check_kill_command(command)
    if check_func_conclusion == 'ok':
        proc_number = command[5:]
        default_server = config.get_default_db_server(chat_id)
        conn_st = config.get_pyodbc_connection_string(host=default_server)
        conn = pyodbc.connect(conn_st, autocommit=True)

        with conn:
            with conn.cursor() as cursor:
                try:
                    cursor.execute('KILL ' + proc_number + ';')
                    cursor.commit()
                    send_text_message(chat_id, "Процесс " + proc_number + " храбро сражался. Но был убит.")
                except pyodbc.ProgrammingError as er:
                    send_text_message(chat_id, "C процессом " + proc_number + " возникла проблема: " + str(er))
    else:
        send_text_message(chat_id, check_func_conclusion)


def show_sql_dir_command(update_info: dict) -> None:
    """Отправить в чат список доступных боту sql-скриптов."""
    chat_id = extract_chat_id(update_info)
    answer = get_text_from_file('text_files/show_sql_dir_command_answer_beginning.txt') + \
             '\n\U0001F3F7 '.join([''] + os.listdir('sql_queries'))
    answer = answer.encode('utf-8')
    send_text_message(chat_id, answer)


def check_restart_command(command: str) -> str:
    """
    Проверить корректность команды /rst_<app_alias>.

    :param command: текст команды (без символа слеш)
    :return: строка "ok" - в случае успешной проверки, текст ошибки - в противном случае
    """

    err_text_st = 'Проблема в записи команды: '
    err_text_end = ' Узнай подробнее, выполнив /rst_APP'

    if len(command) == 4:
        err_text_st += "команда должна содержать элиас сервиса после 'rst_'."
        return err_text_st + err_text_end

    return "ok"


def is_service_updating_now(marathon_app_url: str) -> bool:
    """Проверить, обновляется ли сервис сейчас."""
    deployments = req.get(marathon_app_url).json()['app']['deployments']
    if not deployments:
        return False
    return True


def restart_command(command: str, update_info: dict) -> None:
    """
    Выполнить рестарт указанного приложения.

    :param command: команда rst_APP, где APP - это элиас приложения в таблице RC.dbo.MarathonApps (сервер OSSKTBAPP1)
    :param update_info: словарь с данными о событии (сообщении), в котором была указана команда
    :return: None
    """

    chat_id = extract_chat_id(update_info)

    if command == 'rst_APP':
        text = get_text_from_file('text_files/restart_command_instruction.txt')
        send_text_message(chat_id, text)
        return None

    check_func_conclusion = check_restart_command(command)
    if check_func_conclusion == 'ok':
        alias = command[4:].upper()
        text = f"\u2705 Сервис {alias} сгорел и возродился из пепла, как феникс. Перезагрузил успешно."

        app_data = config.get_app_address_data_from_db(alias)
        if app_data == ("NOT", "FOUND"):
            text = f'\u274C Не нашёл сервис с элиасом {alias} среди доступных для рестарта.'
            send_text_message(chat_id, text.encode('utf-8'))
            return None

        server_name, app_address_id = app_data[0], app_data[1]

        # marathon_app_url - http запрос к конкретному приложению на Marathon
        marathon_app_url = 'http://' + server_name + ':8080/v2' + '/apps' + app_address_id
        if is_service_updating_now(marathon_app_url):
            text = f'\u274C Сервис {alias} уже в процессе обновления. Не стал его тревожить.'

        try:
            restart_status = req.post(marathon_app_url + '/restart')
            if restart_status.status_code != 200:
                text = f'\u274C Я попытался перезапустить сервис {alias}. ' + \
                       f'Но при запросе к Marathon получил код {restart_status.status_code}.'
        except Exception as e:
            text = f'\u274C Я попытался перезапустить сервис {alias}. ' + \
                   'Но не вышло даже http-запрос выполнить. Возникла ошибка: ' + str(e)

        send_text_message(chat_id, text.encode('utf-8'))
    else:
        send_text_message(chat_id, check_func_conclusion)


def say_command_not_found(command: str, update_info: dict) -> None:
    """Отправить в чат сообщение о том, что такой команды нет среди доступных."""
    chat_id = extract_chat_id(update_info)
    text = f"\u274C команда /{command} не найдена".encode('utf-8')
    send_text_message(chat_id, text)
