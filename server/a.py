import os

id_list = [id.split('.')[0] for id in os.listdir('chat_data')]
print(id_list)
