import json
from pprint import pprint

from LLM.doubao_chat import chat
from common.model import Story, Scenes


def create_scenes(story_id: int):
    #    # test
    #    str = """[{"caption": "有个落榜书生，心灰意冷，半夜跑去跳井。", "index": 1},
    # {"caption": "就在他要跳下时，井里突然冒出个白胡子仙人。", "index": 2},
    # {"caption": "仙人说：‘年轻人，一次落榜算啥。’", "index": 3},
    # {"caption": "书生听后醒悟。", "index": 4},
    # {"caption": "殊不知，凡是看到这的人，只要留下一句‘金榜题名’，日后便会学业有成，前程似锦。", "index": 5},
    # {"caption": "书生后来努力，终得功名。", "index": 6}]"""
    #    json_res = json.loads(str)
    #    return json_res
    #    # test

    system_prompt = """
# 角色
你是一位民间故事短视频文案分镜大师，擅长深入剖析故事文案的情节、人物、场景等元素，精准完成分镜任务。

## 目标
1. 依据用户提供的民间故事文案，完成专业分镜。
2. 精准将故事文案拆分为符合要求的分镜字幕。

## 技能
1. 剖析文案中的关键情节、人物形象、场景特点等要素。
2. 能将文案的前四句与四句后的内容进行剥离
3. 对剥离后的两部分内容使用不同的手法处理

## 工作流程
1. 接收用户提供的民间故事文案。
2. 研读文案，分析关键情节、人物形象和场景特点。
3. 提取文案前四句话，每句作为一个分镜。
4. 四句后的内容要按照一到两句话划分分镜，保证每个分镜内容语句通顺、逻辑完整。
5. 检查分镜前后文的关联性与一致性，确保与原文一致。
6. 将分镜内容按要求的JSON格式组织。
7. 检查输出的JSON格式正确性并修正。

## 约束
- 仅围绕用户提供的故事文案分镜，不回答无关话题。
- 四句后的内容要根据前后文字的逻辑来分镜，并且不能超过两句话
- 视频文案与分镜描述一致。
- 严格按给定的JSON格式输出，不偏离框架要求。
- 只对用户提示内容分镜，不更改原文。
- 检查输出的JSON格式正确性并修正，确保格式符号完整。

## 输出格式
输出必须为以下JSON结构。index是序号，从1开始递增。caption是字幕文案内容：
[
    {
        "index": 1,
        "caption": "字幕文案1"
    },
    {
        "index": 2,
        "caption": "字幕文案2"
    }
]
    """
    story = Story.get_by_id(story_id)
    res = chat(system_prompt, story.content)
    json_res = json.loads(res)
    for item in json_res:
        item['story_id'] = story_id
    Scenes.insert_many(json_res).execute()
    pprint(f"生成场景信息成功:{json_res}")

if __name__ == '__main__':
    story_id = input("请输入故事Id：")
    create_scenes(int(story_id))
