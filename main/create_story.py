import sys

from common.model import Story

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