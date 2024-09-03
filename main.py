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
from window import Window
from utils import reactions, listner
import asyncio
import tkinter as tk


websocket.enableTrace(True)


class App:

    is_talk: bool
    HOST: str
    TOKEN: str
    CHANNEL: str
    BOUYOMICHAN_PATH: str
    DEVICE_INDEX: int
    current_note_id: str
    EMOJI_DICT: dict
    ws: websocket.WebSocketApp
    ws_url: str
    window: Window


    def __init__(self):
        self.is_talk = False
        self.HOST = ""
        self.TOKEN = ""
        self.CHANNEL = ""
        self.BOUYOMICHAN_PATH = ""
        self.DEVICE_INDEX = 0
        self.current_note_id = 'test'
        self.EMOJI_DICT = {}
        self.ws = None
        self.ws_url = ""
        self.window = None

    def initialize(self):
        self.window = Window(self.click_start, self.click_stop)
        return self.window
    
    async def websocket_run_forever(self):
        while True:
            try:
                self.ws.run_forever()
            except websocket.WebSocketException as e:
                print(f"WebSocket error: {e}")
                self.window.log(f"WebSocket error: {e}")
                await asyncio.sleep(5)  # 再接続前に少し待機
            except Exception as e:
                print(f"Unexpected error: {e}")
                self.window.log(f"Unexpected error: {e}")
                break

    async def run(self, is_talk: bool, HOST: str, TOKEN: str, CHANNEL: str, BOUYOMICHAN_PATH: str, DEVICE_INDEX: int):
        print('run')
        self.is_talk = is_talk
        self.HOST = HOST
        self.TOKEN = TOKEN
        self.CHANNEL = CHANNEL
        self.BOUYOMICHAN_PATH = BOUYOMICHAN_PATH
        self.DEVICE_INDEX = DEVICE_INDEX
        
        await asyncio.create_subprocess_exec(self.BOUYOMICHAN_PATH)
        self.EMOJI_DICT = reactions.get_emojis_dict(HOST)

        if self.is_talk:
            await listner.realtime_textise(self.on_spoken, self.DEVICE_INDEX)
        
        self.ws_url = f"wss://{HOST}/streaming?i={TOKEN}"
        self.ws = websocket.WebSocketApp(self.ws_url,
                                    on_open=self.on_open,
                                    on_message=self.on_message,
                                    on_error=self.on_error,
                                    on_close=self.on_close)
        
        await self.websocket_run_forever()

    def stop(self):
        self.ws.close()

    def click_start(self, is_talk: bool, HOST: str, TOKEN: str, CHANNEL: str, BOUYOMICHAN_PATH: str, DEVICE_INDEX: int):
        print("click_start")
        if self.window:
            self.window.log("読み上げを開始します")
        asyncio.create_task(self.run(is_talk=is_talk, HOST=HOST, TOKEN=TOKEN, CHANNEL=CHANNEL, BOUYOMICHAN_PATH=BOUYOMICHAN_PATH, DEVICE_INDEX=DEVICE_INDEX))
        return True
    
    def click_stop(self):
        if self.window:
            self.window.log("読み上げを終了します")
        if self.ws:
            self.ws.close()

    def on_open(self,ws):
        message = {
            "type": "connect",
            "body": {
                "channel": self.CHANNEL,
                "id": "foobar"
            }
        }
        ws.send(json.dumps(message))
        print("タイムラインに接続しました")
        if self.window:
            self.window.log("タイムラインに接続しました")


    def on_message(self,ws, message):
        json_message = json.loads(message)

        content = json_message['body']['body']['text']

        if content is None:
            return

        name = json_message['body']['body']['user']['name']

        self.current_note_id = json_message['body']['body']['id']
        content = self.toPlain(content)

        print(f"\033[33m{name} : {content}\033[0m")
        self.window.log(f"{name} : {content}")
        self.speak_bouyomi(text=content)


    def on_error(ws, error):
        print("Error occurred: ", error)


    def on_close(ws):
        print("接続を閉じました")


    def exchangeEmoji(self,name):
        if name in self.EMOJI_DICT:
            return self.EMOJI_DICT[name][0]
        else:
            return name[1:-1]


    def toPlain(self,content):
        if 'play/' in content:
            return 'プレイの投稿'

        content = re.sub(
            "(https?:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+)|(\[.+\]\(https?:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+\))", "「URL省略」", content)
        content = re.sub(
            "\$\[\s*[a-zA-Z0-9]+(\.[a-zA-Z0-9]+(=(([a-zA-Z]+)|(-?[0-9]+)))?)?\s*", "", content)
        content = re.sub("\]", "", content)
        content = re.sub(":.+:", lambda match: '「' +
                        self.exchangeEmoji(match.group())+'」', content)
        content = re.sub("```.*```", "「コード」", content)
        content = re.sub("@\S+", "「メンション」", content)
        content = re.sub("#\S+", "「ハッシュタグ」", content)
        content = re.sub("<\/?[a-zA-Z]+>", "", content)
        content = re.sub("[*>]", "", content)
        content = emoji.demojize(content, delimiters=('「', '」'), language='ja')

        return content


    def speak_bouyomi(self, text='秘密のメッセージ', voice=0, volume=-1, speed=-1, tone=-1):
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


    def on_spoken(self, alias):
        if alias in self.EMOJI_DICT:
            self.create_reaction(random.choice(self.EMOJI_DICT[alias]))
        else:
            print('\033[92m該当する絵文字が見つかりませんでした\033[0m')
            self.window.log('該当する絵文字が見つかりませんでした')


    def create_reaction(self, emoji_name):
        if self.current_note_id == '':
            print('\033[92mリアクションを作成するノートがありません\033[0m')
            self.window.log('リアクションを作成するノートがありません')
            return

        url = f'https://{self.HOST}/api/notes/reactions/create'

        headers = {
            'Authorization': f'Bearer {self.TOKEN}',
            'Content-Type': 'application/json'
        }

        payload = {
            "noteId": self.current_note_id,
            "reaction": emoji_name
        }

        res = requests.post(url, headers=headers, data=json.dumps(payload))

        if res.status_code == 204:
            print(f"\033[92mリアクションが正常に作成されました : {emoji_name}\033[0m")
            self.window.log(f"リアクションが正常に作成されました : {emoji_name}")
        else:
            print(f"\033[92mエラーが発生しました。ステータスコード: {res.status_code}\033[0m")
            self.window.log(f"エラーが発生しました。ステータスコード: {res.status_code}")
            print(f"\033[92mレスポンス: {res.text}\033[0m")
            self.window.log(f"レスポンス: {res.text}")

        async def run_tk(self, root, interval=0.05):
            try:
                while True:
                    root.update()
                    await asyncio.sleep(interval)
            except tk.TclError as e:
                if "application has been destroyed" not in str(e):
                    raise
        



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
        "-B", "--bouyomichanpath", type=str, default="C:\BouyomiChan_0_1_11_0_Beta21\BouyomiChan.exe")
    parser.add_argument("--talk", action="store_true")
    parser.add_argument("-D", "--device-index", type=int, default=0)
    return parser.parse_args()


async def main():
    app = App()
    window = app.initialize()
    
    root = window.window.master  # TkEasyGUIのWindowオブジェクトからTkinterのrootウィンドウを取得

     # メインループを開始する前に、イベントループを取得し、アプリケーションにセット
    loop = asyncio.get_event_loop()
    app.loop = loop

    # Tkinterのイベントループとasyncioのイベントループを並行して実行
    await asyncio.gather(
        app.run_tk(root),
        # 他の非同期タスクがあればここに追加
    )

if __name__ == "__main__":
    asyncio.run(main())
