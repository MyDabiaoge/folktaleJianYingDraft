from pprint import pprint

import requests
import json

from common.utils import decode_base64, save_to_file

url = "https://openspeech.bytedance.com/api/v1/tts"
app_id = "3825016967"
token = "Ac3Fn4ibVvi2JoyWWj9YiVQoF7VnQNWD"


def create_voice(id: int, text):
    payload = json.dumps({
        "app": {
            "appid": app_id,
            "token": token,
            "cluster": "volcano_tts",
        },
        "user": {
            "uid": str(id),
        },
        "audio": {
            "voice_type": "zh_male_dongfanghaoran_moon_bigtts",
            "encoding": "mp3",
            "speed_ratio": 1.0,
        },
        "request": {
            "reqid": str(id),
            "text": text,
            "operation": "query",
        }
    })
    headers = {
        'Authorization': f'Bearer;{token}',
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code == 200:
        res = response.json()
        return {
            'duration': float(res['addition']['duration']),
            'base64': res['data']
        }
    else:
        raise Exception(f"API调用失败，状态码: {response.status_code}, 错误: {response.text}")

    # 转换为JSON对象


def create_voice_and_save_file(scenes_id: int, index: int, story_name: str, caption: str):
    voice_data = create_voice(scenes_id, caption)
    decoded_data = decode_base64(voice_data['base64'])
    save_to_file(rf"D:\Mine\folktale\{story_name}\audios\{index}.mp3", decoded_data)
    return {
        'voice_path': rf"D:\Mine\folktale\{story_name}\audios\{index}.mp3",
        'duration': voice_data['duration'] * 1000,
    }


if __name__ == '__main__':
    # pprint(create_voice("你好"))
    create_voice_and_save_file(2, 1, "书生", "你好")
