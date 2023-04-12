import websocket
import json
import re
import emoji
import requests
import config
import subprocess
import time
'''
import time
from pydub import AudioSegment
from pydub.playback import play
'''

subprocess.Popen("/mnt/c/BouyomiChan_0_1_11_0_Beta21/BouyomiChan.exe")

token=config.TOKEN
while(True):
    host=input("misskey.io:1,voskey.icalo.net:2,その他:3\n番号を入力:")
    if host == "1":
        host="misskey.io"
        token=config.TOKEN
        break
    if host == "2":
        host="voskey.icalo.net"
        token=config.VTOKEN
        break
    if host == "3":
        host=input("ホスト名を入力:")
        token=input("トークンを入力:")
        break
while(True):
    channel=int(input("globalTimeline:1,homeTimeline:2,hybirdTimeline:3,localTimeline:4,main:5\n番号を入力:"))
    if channel > 0 & channel < 6:
        break
channel=channel-1
channels=["globalTimeline","homeTimeline","hybirdTimeline","localTimeline","main"]

ws_url = f"wss://{host}/streaming?i={token}"

def on_open(ws):
    print("WebSocket connection opened")
    message = {
        "type": "connect",
        "body": {
            "channel": channels[channel],
            "id": "foobar"
        }
    }
    ws.send(json.dumps(message))

def on_message(ws, message):
    json_message = json.loads(message)


    content = json_message['body']['body']['text']

    if content is None:
        return
    
    name = json_message['body']['body']['user']['name']

    open('out.txt','a').write(f"{name} : {content}\n")
    content=toPlain(content)

    # Print the contents of the 'body' field
    print(f"\033[33m{name} : {content}\033[0m")
    speak_bouyomi(text=content)

def on_error(ws, error):
    print("Error occurred: ", error)

def on_close(ws):
    print("WebSocket connection closed")


def toPlain(content):
    content = re.sub("(https?:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+)|(\[.+\]\(https?:\/\/[\w\/:%#\$&\?\(\)~\.=\+\-]+\))","「URL省略」",content)
    content = re.sub("\$\[\s*[a-zA-Z0-9]+(\.[a-zA-Z0-9]+(=(([a-zA-Z]+)|(-?[0-9]+)))?)?\s*","",content)
    content = re.sub("\]","",content)
    content = re.sub(":.+:","「絵文字」",content)
    content = re.sub("```.*```","「コード」",content)
    content = re.sub("@\S+","「メンション」",content)
    content = re.sub("#\S+","「ハッシュタグ」",content)
    content = re.sub("<\/?[a-zA-Z]+>","",content)
    content = re.sub("[*>]","",content)
    content = emoji.replace_emoji(content,"「絵文字」")

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
'''
def speak_voicevox(text='秘密のメッセージ',speaker=8):
    # 音声合成クエリの作成
    res1 = requests.post('http://127.0.0.1:50021/audio_query',params = {'text': text, 'speaker': speaker})
    # 音声合成データの作成
    res2 = requests.post('http://127.0.0.1:50021/synthesis',params = {'speaker': speaker},data=json.dumps(res1.json()))

    with open('go.wav', mode='wb') as f:
        f.write(res2.content)
    # 音声ファイルの読み込み
    audio_file = AudioSegment.from_file("go.wav", format="wav")

    # 再生
    play(audio_file)
'''

if __name__ == "__main__":
    print(speak_bouyomi('テストテスト'))


websocket.enableTrace(True)
ws = websocket.WebSocketApp(ws_url,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.run_forever()
