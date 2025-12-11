from pprint import pprint
import json

from common.model import Story, Role, Scenes
from common.utils import scenes_serializer, role_serializer
from volcenginesdkarkruntime import Ark

api_key = '53a070fe-f684-4d6b-92fb-b373ff3a8847'
client = Ark(api_key='53a070fe-f684-4d6b-92fb-b373ff3a8847')


# def chat(system_prompt: str, user_prompt: str):
#     url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
#
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {api_key}"
#     }
#
#     data = {
#         "model": 'doubao-1-5-pro-32k-250115',
#         "messages": [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_prompt},
#         ],
#         "temperature": 0.7,
#         "max_tokens": 16384
#     }
#
#     response = requests.post(url, headers=headers, json=data)
#
#     if response.status_code == 200:
#         return response.json()['choices'][0]['message']['content']
#     else:
#         raise Exception(f"API调用失败，状态码: {response.status_code}, 错误: {response.text}")

def chat(system_prompt: str, user_prompt: str, model: str = "doubao-1-5-pro-32k-250115",max_completion_tokens:int = None):
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.7,
        thinking={
            "type": "disabled",  # 不使用深度思考能力
            # "type": "enabled", # 使用深度思考能力
            # "type": "auto", # 模型自行判断是否使用深度思考能力
        },
        max_completion_tokens=max_completion_tokens
    )
    res = completion.choices[0].message.content
    pprint(f"chat接口返回{res}")
    return res










# if __name__ == '__main__':
# res = chat("你是聊天助手","你好呀")

# story_content = input("请输入故事内容")
# res = create_role(story_content)
# pprint(res)

# story_content = input("请输入故事内容：")
# res = create_scenes(story_content)
# pprint(res)

#    role_str = """[{'name': '落榜书生', 'traits': '年龄约20岁，五官端正、眼神忧郁，体态瘦弱，肤色泛黄，发型黑色束发，服饰破旧长衫。'},
# {'name': '白胡子仙人', 'traits': '年龄约80岁，五官慈祥、白眉白须，体态清瘦，肤色红润，发型白发苍苍，服饰白色道袍。'}]"""
#    scenes_str = """[{'caption': '有个落榜书生，心灰意冷，半夜跑去跳井。', 'index': 1},
#     {'caption': '就在他要跳下时，井里突然冒出个白胡子仙人。', 'index': 2},
#     {'caption': '仙人说：‘年轻人，一次落榜算啥。’', 'index': 3},
#     {'caption': '书生听后醒悟。', 'index': 4},
#     {'caption': '殊不知，凡是看到这的人，只要留下一句‘金榜题名’，日后便会学业有成，前程似锦。', 'index': 5},
#     {'caption': '书生后来努力，终得功名。', 'index': 6}]"""
#    res = create_image_prompt(role_str, scenes_str)
#    pprint(res)
