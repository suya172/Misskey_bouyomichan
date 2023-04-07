import websocket
import json
import re
import emoji
import requests
import config

host="misskey.io"
token=config.TOKEN

ws_url = f"wss://{host}/streaming?i={token}"

def on_open(ws):
    print("WebSocket connection opened")
    message = {
        "type": "connect",
        "body": {
            "channel": "localTimeline",
            "id": "foobar"
        }
    }
    ws.send(json.dumps(message))

def on_message(ws, message):
    json_message = json.loads(message)


    content = json_message['body']['body']['text']

    if content is None:
        return
    
    content=toPlain(content)

    username = json_message['body']['body']['user']['username']


    # Print the contents of the 'body' field
    print(f"\033[33m{username} : {content}\033[0m")
    open('out.txt','a').write(f"{username} : {content}\n")
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
    return res.status_code


if __name__ == "__main__":
    print(speak_bouyomi('あいうえお'))


websocket.enableTrace(True)
ws = websocket.WebSocketApp(ws_url,
                            on_open=on_open,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
ws.run_forever()
