import TkEasyGUI as eg
import pyaudio
from utils import get_input_channels
import datetime

pa = pyaudio.PyAudio()


class Window:
    host_list = ["misskey.io", "nijimiss.moe", "sushi.ski", "trpger.us", "oekakiskey", "mi.nakn.jp", "misskey.art", "voskey.icalo.net"]
    mic_list = get_input_channels.get_mic_list()
    channel_list = ["globalTimeline", "homeTimeline","hybirdTimeline", "localTimeline", "main"]
    window: eg.Window # type: ignore

    # レイアウトの定義
    layout = [
        [
            eg.Column(
                [            
                    [eg.Text('ホスト名'), eg.Combo(host_list,key='-host-'),],
                    [eg.Text('APIトークン'), eg.InputText(key='-token-',password_char='*',size=(30, 1))],
                    [eg.Text('チャンネル')],
                    [eg.Listbox(
                        channel_list,
                        default_value='homeTimeline',
                        key='-channel-',
                        select_mode=eg.LISTBOX_SELECT_MODE_SINGLE,
                        size=(20, 5),
                    )],
                    [eg.Text('棒読みちゃんのパス')],
                    [eg.Input('',key='-bouyomichanpath-'),eg.FileBrowse(
                        file_types=(("実行ファイル", "*.exe"),),
                        title='棒読みちゃんの実行ファイルを選択',
                        key='-bouyomichanpath_browse-',
                    )],
                ]
            ),
            eg.VSeparator(),
            eg.Column(
                [
                    [eg.Checkbox('マイクでリアクション', key='-is_talk-')],
                    [eg.Text('マイクチャンネル')],
                    [eg.Listbox(
                        mic_list,
                        default_value=mic_list[0],
                        key='-mic_channel-',
                        select_mode=eg.LISTBOX_SELECT_MODE_SINGLE,
                        size=(30, 10)
                )],
                ]
            )
        ],
        [eg.Button('読み上げを開始', key='-run-'), eg.Button('終了', key='-stop-')],
        [eg.HSeparator(background_color='#96C78C')],
        [eg.Listbox(
            key='-log-',
            select_mode=eg.LISTBOX_SELECT_MODE_EXTENDED,
            size=(80, 10)
        )],
    ]

    log_list = []
    def __init__(self, click_start, click_stop):
        self.window = eg.Window('棒読みすきー', self.layout)
        self.window['-bouyomichanpath-'].set_disabled(disabled=True)
        self.window['-bouyomichanpath_browse-'].set_disabled(disabled=True)
        self.window['-mic_channel-'].set_disabled(disabled=True)
        self.window['-stop-'].set_disabled(disabled=True)
        for event, values in self.window.event_iter():
            if event == '-run-':
                self.window['-run-'].set_disabled(disabled=True)
                click_start()
                self.window['-stop-'].set_disabled(disabled=False)
            elif event == eg.WIN_CLOSED:
                eg.popup('Goodbye!')
                break
            elif event == '-stop-':
                self.window['-stop-'].set_disabled(disabled=True)
                click_stop()
                self.window['-run-'].set_disabled(disabled=False)
            elif event == '-is_talk-':
                if values['-is_talk-']:
                    self.window['-bouyomichanpath-'].set_disabled(disabled=False)
                    self.window['-bouyomichanpath_browse-'].set_disabled(disabled=False)
                    self.window['-mic_channel-'].set_disabled(disabled=False)
                else:
                    self.window['-bouyomichanpath-'].set_disabled(disabled=True)
                    self.window['-bouyomichanpath_browse-'].set_disabled(disabled=True)
                    self.window['-mic_channel-'].set_disabled(disabled=True)


    def log(self,msg: str):
        now = datetime.datetime.now()
        msg = f'{now.strftime("%Y-%m-%d %H:%M:%S")} {msg}'
        self.log_list.append(msg)
        self.window['-log-'].update(values=self.log_list)

    def get(self, key: str):
        return self.window[key].get()
