import requests
URL='https://feebly-settled-killifish.cloudpub.ru'

csrftoken = requests.get(URL+"/csrf").json()['csrf']
header = {'X-CSRFToken': csrftoken}
cookies = {'csrftoken': csrftoken}

content = {'action': 'add', 'text': 'забрать дочку из садика', 'category': 'meeting',
            'address': '', 'datetime': '2025-06-17 12:21', 'done': False, 'condition': 'time', 'user_id': '829328549'}
        

mes = requests.post(URL + '/records/add', data=content, headers=header, cookies=cookies).json()
print(mes['message'])