import json

user_file = 'data/users.json'

default_restriction = {
    'punks': [-0.05, 0.05],
    'azuki': [-0.5, 0.5],
    'bayc': [-0.05, 0.05],
    'mayc': [-0.3, 0.3],
    'milady': [-2.0, 2.0]
}


def read_profile_json():
    with open(user_file, encoding='utf-8') as f:
        d = json.load(f)
    return d


def save_profile_json(data=None, new=False):
    if data is None and new is True:
        data = {}
    if data is None and new is False:
        raise Exception('Incorrect save_json!')
    with open(user_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def if_profile_exists(user_id: int | str):
    d = read_profile_json()
    if str(user_id) in d.keys():
        return True
    return False


def create_profile(user_id: int | str):
    try:
        profile = {
            'last': {},
            'notifications': True,
            'trades_limit': 3,
            'collections': [[col.split('/')[-1], True, default_restriction[col.split('/')[-1]]] for col in
                            [i.strip() for i in open('urls.txt').readlines()]]
        }
    except KeyError:
        raise Exception('Проверьте корректность заполнения default_restriction или urls.txt!')
    data = read_profile_json()
    data[str(user_id)] = profile
    save_profile_json(data)
    return profile


def get_profile(user_id: int | str):
    data = read_profile_json()
    return data[str(user_id)]
