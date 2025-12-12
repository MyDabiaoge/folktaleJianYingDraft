import sys
from pprint import PrettyPrinter, pprint

from common.model import Story, Role, Scenes, database
from main.create_audios import create_audios
from main.create_images import create_images
from main.create_jy_traft import create_jy_traft
from main.create_prompt import create_image_prompt
from main.create_role import create_role
from main.create_scenes import create_scenes
from main.create_v_prompt import create_v_prompt
from main.create_videos import create_videos

if __name__ == '__main__':
    story_name = input("请输入故事名称：")
    exists_user = Story.select().where(Story.name == story_name).exists()
    if exists_user:
        print("故事名已存在！")
        sys.exit()

    print("请输入故事内容：")
    story_content = ''
    while True:
        try:
            story_content += input()
        except:
            break
    # with database.atomic() as transaction:
    story_id = Story.create(name=story_name, content=story_content)
    print(f"新增故事id:{story_id}")

    # 生成角色信息
    role_list = create_role(story_id)
    # 生成分镜
    scenes = create_scenes(story_id)
    # 生成绘画提示词
    scenes_had_prompt = create_image_prompt(story_id)
    # 生成图片
    create_images(story_id)
    # 生成视频提示词
    create_v_prompt(story_id)
    # 生成音频
    create_audios(story_id)
    # 生成视频
    create_videos(story_id)
    # 生成草稿
    create_jy_traft(story_id)
