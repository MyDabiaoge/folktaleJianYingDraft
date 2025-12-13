from string import Template

import requests
import json

from common.utils import decode_base64, save_to_file

# base_url = "http://1.95.136.171:5100"
base_url = "http://127.0.0.1:5100"
base_prompt = Template('''
- **主要内容**：$content
- **艺术风格**：古风写实插画，中国工笔与现代水彩融合风格，绢本细腻纹理质感，细节精致写实。古风写实插画，中国工笔与现代水彩融合风格，绢本细腻纹理质感，细节精致写实。柔和侧光，自然漫射光，轻柔明暗变化
''')


def base_image_request(session_id: str, prompt: str):
    payload = json.dumps({
        "model": "jimeng-4.0",
        "prompt": prompt,
        "ratio": "9:16",
        "resolution": "1k",
        "sample_strength": 1,
        "response_format": "b64_json"
    })

    headers = {
        "Authorization": f"Bearer {session_id}",
        "Content-Type": "application/json"
    }
    url = base_url + "/v1/images/generations"
    response = requests.request("POST", url, headers=headers, data=payload)

    # print(response.text)

    # 获取耗时（秒）
    elapsed_time = response.elapsed.total_seconds()
    print(f"请求耗时: {elapsed_time:.2f} 秒")
    # 转换为JSON对象
    result = response.json()
    # 直接获取所有URL
    # pprint(result)
    b64s = [item["b64_json"] for item in result["data"]]
    return b64s


def base_video_request(session_id: str, prompt: str, image_path: str):
    url = base_url + "/v1/videos/generations"

    # 准备请求头
    headers = {
        "Authorization": f"Bearer {session_id}"
    }
    # 准备表单数据
    files = [
        ('image_file_1', ('image1.jpg', open(image_path, 'rb'), 'image/jpeg')),
        # ('images', ('image2.png', open(image2_path, 'rb'), 'image/jpeg'))
    ]
    # 准备其他表单字段
    data = {
        "prompt": prompt,
        "model": "jimeng-video-3.0",
        "ratio": "16:9",
        "duration": "10",
        "response_format": "b64_json"
    }
    # 发送POST请求
    response = requests.post(
        url=url,
        headers=headers,
        data=data,
        files=files
    )
    # print(response.text)

    # 获取耗时（秒）
    elapsed_time = response.elapsed.total_seconds()
    print(f"请求耗时: {elapsed_time:.2f} 秒")
    # 转换为JSON对象
    result = response.json()
    # 直接获取所有URL
    # pprint(result)
    b64s = [item["b64_json"] for item in result["data"]]
    return b64s


def create_image_save_file(session_id: str, sql_index: int, story_name: str, prompt: str):
    final_prompt = base_prompt.substitute(content=prompt)
    b64s = base_image_request(session_id, final_prompt)
    file_list = []
    for i, b64 in enumerate(b64s):
        decoded_data = decode_base64(b64)
        file_name = rf"D:\Mine\folktale\{story_name}\images\{sql_index}_{i + 1}.jpeg"
        save_to_file(file_name, decoded_data)
        file_list.append(file_name)

    return file_list


def create_video_save_file(session_id: str, sql_index: int, story_name: str, prompt: str, image_path: str,
                           image_index: int = 1):
    b64s = base_video_request(session_id, prompt, image_path)
    file_list = []
    for i, b64 in enumerate(b64s):
        decoded_data = decode_base64(b64)
        file_name = rf"D:\Mine\folktale\{story_name}\videos\{sql_index}_{image_index}.mp4"
        save_to_file(file_name, decoded_data)
        file_list.append(file_name)

    return file_list
