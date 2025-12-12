import base64
import os
import threading
import time
import cv2
from functools import wraps
from typing import Callable, Any

import requests


def decode_base64(base64_str):
    return base64.b64decode(base64_str)


def save_to_file(filename, data):
    # 提取目录路径
    directory = os.path.dirname(filename)

    # 如果目录不存在，则创建它（包括所有必要的父目录）
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    # 写入文件
    with open(filename, 'wb') as file:
        file.write(data)


# 自定义 JSON 序列化器
def scenes_serializer(scenes):
    json_data = {
        'id': scenes.id,
        'caption': scenes.caption,
        # 'prompt': scenes.prompt,
        # 'story_id': scenes.story_id,
        # 'audio_path': scenes.audio_path,
        # 'image_path1': scenes.image_path1,
        # 'image_path2': scenes.image_path2,
        # 'image_path3': scenes.image_path3,
        # 'image_path4': scenes.image_path4,
        # 'image_index': scenes.image_index,
        # 'index': scenes.index,
        # 'created_time': scenes.created_time,
        # 'update_time': scenes.update_time,
    }
    return json_data


# 自定义 JSON 序列化器
def role_serializer(role):
    json_data = {
        'name': role.name,
        'traits': role.traits,
    }
    return json_data


def retry_on_exception(max_retries: int = 3, delay: float = 1.0,
                       backoff_factor: float = 2.0,
                       exceptions: tuple = (Exception,),
                       retry_on_status_codes: list = None):
    """
    增强的重试装饰器
    Args:
        max_retries: 最大重试次数
        delay: 初始重试延迟（秒）
        backoff_factor: 延迟倍数因子（指数退避）
        exceptions: 需要重试的异常类型
        retry_on_status_codes: 需要重试的HTTP状态码列表
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            func_name = func.__name__

            for attempt in range(max_retries + 1):  # +1 包括第一次尝试
                try:
                    if attempt > 0:
                        print(f"函数 {func_name} 参数 {args}\n第 {attempt} 次重试，延迟 {current_delay:.2f} 秒...")
                        time.sleep(current_delay)
                        current_delay *= backoff_factor  # 指数退避

                    return func(*args, **kwargs)

                except requests.RequestException as e:
                    # 处理网络请求异常
                    last_exception = e
                    status_code = getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None

                    if retry_on_status_codes and status_code in retry_on_status_codes:
                        print(f"遇到可重试的HTTP状态码 {status_code}，进行重试")
                    else:
                        print(f"网络请求异常: {str(e)}")

                    if attempt == max_retries:
                        print(f"达到最大重试次数 ({max_retries})，放弃重试")
                        raise

                except exceptions as e:
                    last_exception = e
                    print(f"函数 {func_name} 参数 {args}\n第 {attempt + 1} 次调用失败: {str(e)}")

                    if attempt == max_retries:
                        print(f"函数 {func_name} 达到最大重试次数 ({max_retries})，放弃重试")
                        raise

            raise last_exception  # 理论上不会执行到这里，但为了安全

        return wrapper

    return decorator


# 重试装饰器配置 - 针对图像生成API
IMAGE_GEN_RETRY_CONFIG = {
    'max_retries': 3,  # 最多重试3次
    'delay': 2.0,  # 初始延迟2秒
    'backoff_factor': 1.5,  # 每次重试延迟增加1.5倍
    'exceptions': (Exception,),  # 捕获所有异常
    # 'retry_on_status_codes': [429, 500, 502, 503, 504]  # 重试这些HTTP状态码
}

# 创建一个全局锁对象
print_lock = threading.Lock()


# 定义线程安全的打印函数
def thread_safe_print(*args, **kwargs):
    with print_lock:
        print(*args, **kwargs)


def get_video_last_frame(video_path: str, image_path: str):
    # video_path = r"D:\Mine\folktale\两兄弟葬父\videos\1_1.mp4"
    # 打开视频文件
    cap = cv2.VideoCapture(video_path)

    # 读取视频文件中的所有帧
    frames = []
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    # 检查是否有帧可用
    if len(frames) > 0:
        # 提取最后一帧并将其保存为图像
        last_frame = frames[-1]
        # cvi_res = cv2.imwrite(r'D:\Mine\folktale\两兄弟葬父\videos\last.jpg', last_frame)
        cv2.imencode(".jpg", last_frame)[1].tofile(image_path)
        print("last picture over")
        return image_path
    else:
        print("错误：无法提取任何帧")
        return None

    # 释放视频文件句柄
    cap.release()


if __name__ == '__main__':


    # import sys
    #
    # lines = sys.stdin.readlines()
    # print(lines)

    get_video_last_frame(r"D:\Mine\folktale\两兄弟葬父\videos\1_1.mp4",r"D:\Mine\folktale\两兄弟葬父\videos\last.jpeg")
