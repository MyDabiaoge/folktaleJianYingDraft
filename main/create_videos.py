import sys
from pprint import pprint

from LLM.jimeng_reverse import create_video_save_file
from common.constant import session_ids
from common.model import Story, Scenes
import threading
import queue
import time
from functools import wraps
from typing import Callable, Any
import requests

from common.utils import retry_on_exception, IMAGE_GEN_RETRY_CONFIG, scenes_serializer, thread_safe_print, \
    get_video_last_frame

# 对函数应用重试装饰器
retryable_fun = retry_on_exception(**IMAGE_GEN_RETRY_CONFIG)(create_video_save_file)


# 为每个session_id创建一个专用线程函数
def session_worker(session_id, scenes_queue, story_name, db_lock, failed_scenes_queue=None):
    """为特定session_id创建的工作线程"""
    thread_safe_print(f"线程启动，专用session_id: {session_id}")

    while True:
        try:
            # 从队列获取场景，设置超时避免无限等待
            scene = scenes_queue.get(timeout=1)
        except queue.Empty:
            thread_safe_print(f"线程{session_id}完成所有任务")
            break

        try:
            thread_safe_print(f"线程{session_id}处理场景 {scene.index}，提示词: {scene.v_prompt[:50]}...")
            image_path = scene.image_path1
            if scene.image_index == 2:
                image_path = scene.image_path2
            elif scene.image_index == 3:
                image_path = scene.image_path3
            elif scene.image_index == 4:
                image_path = scene.image_path4
            # 使用带重试的函数调用
            video_paths = retryable_fun(
                session_id, scene.index, story_name, scene.v_prompt, image_path
            )
            # 使用数据库锁确保数据库操作线程安全
            with db_lock:
                scene.video_path1 = video_paths[0] if len(video_paths) > 0 else None
                scene.save()

            thread_safe_print(f"--成功--线程{session_id}完成场景{scene.index}------- ")

        except Exception as e:
            thread_safe_print(f"线程{session_id}处理场景 {scene.index}时发生错误，已达到最大重试次数: {e}")
            # 将失败场景加入失败队列（如果提供了）
            if failed_scenes_queue is not None:
                failed_scenes_queue.put(scene)
                thread_safe_print(f"场景 {scene.index} 已加入失败队列")

        finally:
            scenes_queue.task_done()


def create_videos(story_id: int, is_rerun: bool = False):
    story = Story.get_by_id(story_id)
    if story.video_scenes_num < 1:
        print("视频场景数量为零，已退出程序！")
        sys.exit()

    scenes_list = (Scenes.select()
                   .where(Scenes.story_id == story_id)
                   .order_by(Scenes.index.asc())
                   .limit(story.video_scenes_num))
    if not is_rerun:
        scenes_list = scenes_list.where(Scenes.video_path1.is_null(True))

    print(f"开始处理故事: {story.name}，共有 {len(scenes_list)} 个场景")

    # 创建主任务队列和失败场景队列
    scenes_queue = queue.Queue()
    failed_scenes_queue = queue.Queue()  # 用于存储失败场景

    for scene in scenes_list:
        scenes_queue.put(scene)

    # 创建数据库操作锁
    db_lock = threading.Lock()

    # 为每个session_id创建并启动一个专用线程
    threads = []
    for session_id in session_ids:
        thread = threading.Thread(
            target=session_worker,
            args=(session_id, scenes_queue, story.name, db_lock, failed_scenes_queue),
            name=f"Worker_{session_id}"
        )
        thread.daemon = True
        threads.append(thread)
        thread.start()
        print(f"已启动线程 {thread.name} 使用 session_id: {session_id}")

    # 等待队列中所有任务完成
    scenes_queue.join()

    # 检查是否有失败场景
    failed_count = failed_scenes_queue.qsize()
    if failed_count > 0:
        print(f"警告: 有 {failed_count} 个场景处理失败")
        # 这里可以添加对失败场景的后续处理，比如重新尝试或记录到日志
        while not failed_scenes_queue.empty():
            failed_scene = failed_scenes_queue.get()
            print(f"失败场景: ID={failed_scene.id}, Index={failed_scene.index}")

    print("所有场景处理完成！")


if __name__ == '__main__':
    story_id = input("请输入故事Id：")
    str_one = input("默认只补全没有视频的scene,若要重头到尾重新执行请输入1:")
    is_rerun = False
    if str_one == "1":
        is_rerun = True
    create_videos(int(story_id), is_rerun)
