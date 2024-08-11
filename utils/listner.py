import speech_recognition as sr
import wave
import time
from datetime import datetime
from pykakasi import kakasi

import pyaudio

FORMAT = pyaudio.paInt16
SAMPLE_RATE = 44100        # サンプリングレート
CHANNELS = 1            # モノラルかバイラルか
CALL_BACK_FREQUENCY = 3      # コールバック呼び出しの周期[sec]


def look_for_audio_input():
    """
    デバイスうえでのオーディオ系の機器情報を表示する
    """
    pa = pyaudio.PyAudio()

    for i in range(pa.get_device_count()):
        print(pa.get_device_info_by_index(i))
        print()

    pa.terminate()


def callback(in_data, frame_count, time_info, status):
    """
    コールバック関数の定義
    """

    global sprec, kks_converter, on_spoken

    try:
        audiodata = sr.AudioData(in_data, SAMPLE_RATE, 2)
        sprec_text = sprec.recognize_google(audiodata, language='ja-JP')

        sprec_hiragana = kks_converter.do(sprec_text)

        print(sprec_hiragana)
        on_spoken(sprec_hiragana)

    except sr.UnknownValueError:
        pass

    except sr.RequestError as e:
        pass

    finally:
        return (None, pyaudio.paContinue)


def realtime_textise(d, device_index):
    """
    リアルタイムで音声を文字起こしする
    """

    global sprec, kks_converter, on_spoken, audio, stream

    on_spoken = d

    # speech recogniserインスタンスを生成
    sprec = sr.Recognizer()

    # kakasiインスタンスを生成
    kks = kakasi()
    kks.setMode('J', 'H')
    kks_converter = kks.getConverter()

    # Audioインスタンスを生成
    audio = pyaudio.PyAudio()

    # ストリームオブジェクトを作成
    stream = audio.open(format=FORMAT,
                        rate=SAMPLE_RATE,
                        channels=CHANNELS,
                        input_device_index=device_index,
                        input=True,
                        # CALL_BACK_FREQUENCY 秒周期でコールバック
                        frames_per_buffer=SAMPLE_RATE*CALL_BACK_FREQUENCY,
                        stream_callback=callback)

    stream.start_stream()


def end_realtime_textise():

    global audio, stream

    stream.stop_stream()
    stream.close()
    audio.terminate()


if __name__ == '__main__':
    exit()
