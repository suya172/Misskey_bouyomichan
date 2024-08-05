import requests
import json
import pickle

def get_emojis_dict(host) -> dict:
    url = f'https://{host}/api/emojis'
    try:
        res = requests.get(url)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(e)
        return {}
    else:
        print('絵文字一覧を取得しました')
    
    data = res.json()
    EMOJI_DICT = {}
    for emoji in data['emojis']:
        for alias in emoji['aliases']:
            EMOJI_DICT.setdefault(alias, []).append(emoji['name'])

    filename = host.replace('.','') + '_emojidict.pkl'
    with open(filename, 'wb') as f:
        pickle.dump(EMOJI_DICT, f)

    return EMOJI_DICT

if __name__ == "__main__":
    d = get_emojis_dict('misskey.io')
    print(d['おはよう'])

