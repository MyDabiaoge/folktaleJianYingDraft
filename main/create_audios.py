from concurrent.futures import ThreadPoolExecutor, as_completed

from LLM.doubao_tts import create_voice_and_save_file
from common.model import Scenes, Story


def process_scene(scene, story_name):
    """处理单个场景的完整函数"""
    try:
        # 生成音频文件
        voice_data = create_voice_and_save_file(scene.id, scene.index, story_name, scene.caption)

        print(f"成功处理场景 {scene.index}: {voice_data["voice_path"]}")

        # 更新数据库
        scene.audio_path = voice_data["voice_path"]
        scene.duration = voice_data["duration"]
        scene.save()
        return True
    except Exception as exc:
        print(f"处理场景 {scene.index} 时发生错误: {exc}")
        return False


def create_audios(story_id: int, is_rerun: bool = False):
    story = Story.get_by_id(story_id)
    scenes_list = Scenes.select().where(Scenes.story_id == story_id).order_by(Scenes.index.asc())
    if not is_rerun:
        scenes_list = scenes_list.where(Scenes.audio_path.is_null(True))
    # 使用线程池并行处理，最大并发数为10
    with ThreadPoolExecutor(max_workers=10) as executor:
        # 提交所有任务
        futures = [executor.submit(process_scene, scene, story.name) for scene in scenes_list]

        # 等待所有任务完成
        results = []
        for future in as_completed(futures):
            results.append(future.result())

        print(f"处理完成：成功 {sum(results)} 个，失败 {len(results) - sum(results)} 个")


if __name__ == '__main__':
    story_id = input("请输入故事Id：")
    str_one = input("若要重头到尾重新执行请输入1，默认只补全没有配音的scene")
    is_rerun = False
    if str_one == "1":
        is_rerun = True
    create_audios(int(story_id), is_rerun)
