import pyaudio

def get_mic_list():
    ''' マイクチャンネルのindexをリストで取得する '''

    # 最大入力チャンネル数が0でない項目をマイクチャンネルとしてリストに追加
    pa = pyaudio.PyAudio()
    mic_list = []
    for i in range(pa.get_device_count()):
        num_of_input_ch = pa.get_device_info_by_index(i)['maxInputChannels']

        if num_of_input_ch != 0:
            mic_list.append(str(pa.get_device_info_by_index(i)['index'])+' '+pa.get_device_info_by_index(i)['name'])

    return mic_list
