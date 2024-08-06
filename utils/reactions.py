import requests
import json
import pickle


def get_emojis_dict(host, load_chunk=False) -> dict:
    print('\033[92m絵文字一覧を取得します\033[0m')
    path = './picklejar/' + host.replace('.', '') + '_emojidict.pkl'
    if load_chunk:
        with open(path, 'rb') as f:
            EMOJI_DICT = pickle.load(f)
    else:
        url = f'https://{host}/api/emojis'
        try:
            res = requests.get(url)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(e)
            return {}
        else:
            print('\033[92m絵文字一覧を取得しました\033[0m')

        data = res.json()
        EMOJI_DICT = {}
        for emoji in data['emojis']:
            name = ':' + emoji['name'] + ':'
            for alias in emoji['aliases']:
                EMOJI_DICT.setdefault(alias, []).append(name)
                EMOJI_DICT.setdefault(name, []).append(alias)

        with open(path, 'wb') as f:
            pickle.dump(EMOJI_DICT, f)

    return EMOJI_DICT


if __name__ == "__main__":
    d = get_emojis_dict('misskey.io')
    print(d['おはよう'])
