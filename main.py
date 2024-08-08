# pip install websocket-client
import websocket
import json
import re
import emoji
import requests
import subprocess
import time
import argparse
import random
from utils import reactions, listner


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("-H", "--host", type=str, default="misskey.io")
    parser.add_argument("-T", "--token", type=str, required=True)
    channels = ["globalTimeline", "homeTimeline",
                "hybirdTimeline", "localTimeline", "main"]
    parser.add_argument("-C", "--channel", type=str,
                        choices=channels, default="localTimeline")
    parser.add_argument(
        "-B", "--bouyomichan-path", type=str, default="C:\BouyomiChan_0_1_11_0_Beta21\BouyomiChan.exe")
    parser.add_argument("--talk", action="store_true")
    parser.add_argument("-D", "--device-index", type=int, default=0)
    return parser.parse_args()


is_debug = get_args().debug
is_talk = get_args().talk
HOST = get_args().host
TOKEN = get_args().token
CHANNEL = get_args().channel
BOUYOMICHAN_PATH = get_args().B
DEVICE_INDEX = get_args().device_index

EMOJI_DICT = reactions.get_emojis_dict(HOST)

subprocess.Popen(BOUYOMICHAN_PATH)
ws_url = f"wss://{HOST}/streaming?i={TOKEN}"

current_note_id = ''


def on_open(ws):
    message = {
        "type": "connect",
        "body": {
            "channel": CHANNEL,
            "id": "foobar"
        }
    }
    ws.send(json.dumps(message))
    print("タイムラインに接続しました")


def on_message(ws, message):
    json_message = json.loads(message)

    content = json_message['body']['body']['text']

    if content is None:
        return

    name = json_message['body']['body']['user']['name']

    current_note_id = json_message['body']['body']['id']
    content = toPlain(content)

    print(f"\033[33m{name} : {content}\033[0m")
    speak_bouyomi(text=content)


def on_error(ws, error):
    print("Error occurred: ", error)


def on_close(ws):
    print("接続を閉じました")


def exchangeEmoji(name):
    if name in EMOJI_DICT:
        return EMOJI_DICT[name][0]
    else:
        return name[1:-1]


def toPlain(content):
    if 'play/' in content:
        return 'プレイの投稿'

    content = re.sub(
        "(https?:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+)|(\[.+\]\(https?:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+\))", "「URL省略」", content)
    content = re.sub(
        "\$\[\s*[a-zA-Z0-9]+(\.[a-zA-Z0-9]+(=(([a-zA-Z]+)|(-?[0-9]+)))?)?\s*", "", content)
    content = re.sub("\]", "", content)
    content = re.sub(":.+:", lambda match: '「' +
                     exchangeEmoji(match.group())+'」', content)
    content = re.sub("```.*```", "「コード」", content)
    content = re.sub("@\S+", "「メンション」", content)
    content = re.sub("#\S+", "「ハッシュタグ」", content)
    content = re.sub("<\/?[a-zA-Z]+>", "", content)
    content = re.sub("[*>]", "", content)
    content = emoji.demojize(content, delimiters=('「', '」'), language='ja')

    return content


def speak_bouyomi(text='秘密のメッセージ', voice=0, volume=-1, speed=-1, tone=-1):
    res = requests.get(
        'http://localhost:50080/Talk',
        params={
            'text': text,
            'voice': voice,
            'volume': volume,
            'speed': speed,
            'tone': tone})
    time.sleep(1)
    return res.status_code


def on_spoken(alias):
    if alias in EMOJI_DICT:
        create_reaction(random.choice(EMOJI_DICT[alias]))
    else:
        print('\033[92m該当する絵文字が見つかりませんでした\033[0m')


def create_reaction(emoji_name):
    if current_note_id == '':
        print('\033[92mリアクションを作成するノートがありません\033[0m')
        return

    url = f'https://{HOST}/api/notes/reactions/create'

    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }

    payload = {
        "noteId": current_note_id,
        "reaction": emoji_name
    }

    res = requests.post(url, headers=headers, data=json.dumps(payload))

    if res.status_code == 204:
        print(f"\033[92mリアクションが正常に作成されました : {emoji_name}\033[0m")
    else:
        print(f"\033[92mエラーが発生しました。ステータスコード: {res.status_code}\033[0m")
        print(f"\033[92mレスポンス: {res.text}\033[0m")


if __name__ == "__main__":
    print(speak_bouyomi('テストテスト'))

if is_talk:
    # listner.look_for_audio_input()
    listner.realtime_textise(on_spoken, DEVICE_INDEX)

websocket.enableTrace(True)
ws = websocket.WebSocketApp(ws_url,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.run_forever()

if is_talk:
    listner.end_realtime_textise()
