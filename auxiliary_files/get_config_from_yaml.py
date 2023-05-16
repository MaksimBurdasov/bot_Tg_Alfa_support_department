from spring_config import ClientConfigurationBuilder
from spring_config.client import SpringConfigClient


config = (
    ClientConfigurationBuilder()
    .app_name("ossktb-tgbot-python")  # config file
    .address("http://ossktbapprhel1/ossktb-rcsite-settings/")
    .profile("prelive")
    .build()
)

conf = SpringConfigClient(config).get_config()

# print(conf['tg']['allowed_chats'])

for title, info in conf['tg']['allowed_chats'].items():
    print(info['default_bd'], title, info['chat_id'])

