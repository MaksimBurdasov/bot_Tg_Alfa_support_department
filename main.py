from time import sleep
import web_touch as wbt


def get_updates_list() -> list:
    """
    Получить и отметить прочитанными новые события.

    После обработки события пометятся как прочитанные.
    Повторно получить их методом getUpdates от Telegram будет невозможно.
    :return: список словарей с информацией о событиях
    """

    # обращение к сервису
    # в худшем случае будет произведено 5 попыток
    for _ in range(5):
        resp = wbt.get_updates()
        if resp.status_code == 200:
            break
        sleep(1)
    else:
        # если выполнилось 5 запросов к Telegram без результата
        return []

    resp = resp.json()
    result_list = resp['result']  # список событий (updates)

    if resp['ok']:  # статус resp['ok'] равен True, если Telegram дал валидную информацию
        if result_list:
            last_upd_id = result_list[-1]['update_id']  # id последнего события + 1
            wbt.get_updates(params={'offset': last_upd_id + 1})  # пометить события как обработанные
            return result_list
    return []


def extract_commands(update_data: dict) -> list:
    """
    Получить список команд из одного сообщения.

    :param update_data: словарь с информацией о сообщении
    :return: список команд, найденных в тексте сообщения, в виде строк
    """

    commands = []
    for entity in update_data['message']['entities']:
        if entity['type'] == 'bot_command':
            commands.append(update_data['message']['text'][entity['offset'] + 1:entity['offset'] + entity['length']])
    return commands


def execute_commands(updates_list: list) -> None:
    """
    Отправить на исполнение найденные команды.

    Если в полученном сообщении содержаться команды (одна и более),
    то в цикле они будут переданы в функцию relay_func().
    При возникновении ошибки, её текст будет отправлен в чат.
    :param updates_list: список событий
    """

    for upd in updates_list:
        print(str(upd).replace("'", '"'))  # TODO: delete
        if wbt.is_command_from_allowed_chat(upd):
            for cmd in extract_commands(upd):
                print(cmd)  # TODO: delete
                try:
                    wbt.relay_func(cmd, upd)
                except Exception as er:
                    chat_id = wbt.extract_chat_id(upd)
                    text = f"Команду {cmd} не выполнил.\nВозникла ошибка: " + str(er)
                    wbt.send_text_message(chat_id, text)


if __name__ == "__main__":
    upd_list = get_updates_list()
    if upd_list:
        execute_commands(upd_list)
