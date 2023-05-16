import requests as req
import web_touch as wbt
from json import dumps, loads

import config


resp = loads(wbt.get_updates().text)
updates_list = resp['result']

for upd in updates_list:
    # print(loads(dumps(upd)), end='\n\n')

    if 'message' in upd:
        chat_id = upd['message']['chat']['id']

        commands = []
        for entity in upd['message']['entities']:
            if entity['type'] == 'bot_command':
                commands.append(upd['message']['text'][entity['offset'] + 1:entity['offset'] + entity['length']])

        print(f'chat_id: {chat_id}\ncommands: {", ".join(commands)}', end='\n\n')
