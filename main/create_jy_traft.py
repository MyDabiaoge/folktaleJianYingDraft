import math

from common.caption_tools import process_single_subtitle
from common.model import Story, Scenes
import os
import pyJianYingDraft as draft
from pyJianYingDraft import IntroType, TransitionType, trange, tim, OutroType, ClipSettings, KeyframeProperty, Timerange


def create_jy_traft(story_id: int):
    story = Story.get_by_id(story_id)
    scenes_list = Scenes.select().where(Scenes.story_id == story_id).order_by(Scenes.index.asc())
    # 设置草稿文件夹
    draft_path = r"D:\Program Files\JianyingPro Drafts"
    base_material_path = r"D:\Mine\folktale\base"
    assert os.path.exists(draft_path), f"未找到剪映草稿文件夹{os.path.abspath(draft_path)}"
    assert os.path.exists(base_material_path), f"未找到基础素材文件夹{os.path.abspath(base_material_path)}"
    draft_folder = draft.DraftFolder(draft_path)
    # 创建剪映草稿
    script = draft_folder.create_draft(story.name, 1440, 2560, allow_replace=True)  # 1920x1080分辨率
    # 添加音频、视频和文本轨道
    (script
     .add_track(draft.TrackType.audio, track_name="open")
     .add_track(draft.TrackType.audio, track_name="bgm")
     .add_track(draft.TrackType.audio, track_name="voice")
     .add_track(draft.TrackType.video)
     .add_track(draft.TrackType.text, track_name="title")
     .add_track(draft.TrackType.text, track_name="text"))
    # 添加标题
    title_segment = draft.TextSegment(
        story.name, Timerange(0, 1),  # 文本片段的首尾与上方视频片段一致
        font=draft.FontType.江湖体,  # 设置字体
        style=draft.TextStyle(size=25, color=(0.992156862745098, 0.8784313725490196, 0.0), align=1, letter_spacing=5,
                              auto_wrapping=True),
        # 字体样式
        clip_settings=draft.ClipSettings(transform_y=0.3),  # 位置
        border=draft.TextBorder(color=(0.0, 0.0, 0.0)),  # 描边
    )
    script.add_segment(title_segment, track_name="title")
    # 添加开场音乐
    audio_segment = draft.AudioSegment(os.path.join(base_material_path, 'open_sound.mp3'),
                                       trange(0, 4884897),  # 片段将位于轨道上的0s-5s（注意5s表示持续时长而非结束时间）
                                       volume=6)  # 音量设置为60%(-4.4dB)
    script.add_segment(audio_segment, track_name="open")
    # 处理每个场景
    start_time = 0
    max_duration = 0
    for i, scene in enumerate(scenes_list):
        image_path = scene.image_path1
        if scene.image_index == 2:
            image_path = scene.image_path2
        elif scene.image_index == 3:
            image_path = scene.image_path3
        elif scene.image_index == 4:
            image_path = scene.image_path4

        # 添加配音
        voice_mat = draft.AudioMaterial(scene.audio_path)  # 先创建素材实例
        audio_segment = draft.AudioSegment(voice_mat,
                                           trange(start_time, voice_mat.duration),  # 片段将位于轨道上的0s-5s（注意5s表示持续时长而非结束时间）
                                           volume=10)  # 音量设置为60%(-4.4dB)
        script.add_segment(audio_segment, track_name="voice")
        # 添加视频\图片
        if scene.video_path1:
            if voice_mat.duration < 10000000:
                video_segment = draft.VideoSegment(os.path.join(scene.video_path1),
                                                   trange(start_time, voice_mat.duration),
                                                   # 片段将位于轨道上的0s-4.2s（取素材前4.2s内容，注意此处4.2s表示持续时长）
                                                   clip_settings=ClipSettings(scale_x=1.0, scale_y=1.0)
                                                   )
                video_segment.add_transition(TransitionType.叠化)  # 注意转场添加在“前一个”视频片段上
                script.add_segment(video_segment)
            else:
                video_segment = draft.VideoSegment(os.path.join(scene.video_path1),
                                                   trange(start_time, 10000000),
                                                   # 片段将位于轨道上的0s-4.2s（取素材前4.2s内容，注意此处4.2s表示持续时长）
                                                   clip_settings=ClipSettings(scale_x=1.0, scale_y=1.0)
                                                   )
                script.add_segment(video_segment)
                if voice_mat.duration < 20000000:
                    video_segment = draft.VideoSegment(os.path.join(scene.video_path2),
                                                       trange(start_time + 10000000, voice_mat.duration - 10000000),
                                                       # 片段将位于轨道上的0s-4.2s（取素材前4.2s内容，注意此处4.2s表示持续时长）
                                                       clip_settings=ClipSettings(scale_x=1.0, scale_y=1.0)
                                                       )
                    video_segment.add_transition(TransitionType.叠化)  # 注意转场添加在“前一个”视频片段上
                    script.add_segment(video_segment)
                else:
                    video_segment = draft.VideoSegment(os.path.join(scene.video_path2),
                                                       trange(start_time+ 10000000, 10000000),
                                                       # 片段将位于轨道上的0s-4.2s（取素材前4.2s内容，注意此处4.2s表示持续时长）
                                                       clip_settings=ClipSettings(scale_x=1.0, scale_y=1.0)
                                                       )
                    script.add_segment(video_segment)
                    video_segment = draft.VideoSegment(os.path.join(scene.video_path3),
                                                       trange(start_time + 20000000, voice_mat.duration - 10000000),
                                                       # 片段将位于轨道上的0s-4.2s（取素材前4.2s内容，注意此处4.2s表示持续时长）
                                                       clip_settings=ClipSettings(scale_x=1.0, scale_y=1.0)
                                                       )
                    video_segment.add_transition(TransitionType.叠化)  # 注意转场添加在“前一个”视频片段上
                    script.add_segment(video_segment)

        else:
            video_segment = draft.VideoSegment(os.path.join(image_path),
                                               trange(start_time, voice_mat.duration),
                                               # 片段将位于轨道上的0s-4.2s（取素材前4.2s内容，注意此处4.2s表示持续时长）
                                               clip_settings=ClipSettings(scale_x=1.1, scale_y=1.1)
                                               )
            # 添加一个转场
            video_segment.add_transition(TransitionType.叠化)  # 注意转场添加在“前一个”视频片段上
            # if i != 0:
            #     video_segment.add_animation(IntroType.横向模糊)
            # if i != len(scenes_list) - 1:
            #     video_segment.add_animation(OutroType.横向模糊)
            # 添加两个不移动关键帧形成上下移动的效果
            start_value = -0.09765625
            end_value = 0.09765625
            if (i - 1) % 2 == 0:
                start_value = 0.09765625
                end_value = -0.09765625
            video_segment.add_keyframe(KeyframeProperty.position_y, 0, start_value)
            video_segment.add_keyframe(KeyframeProperty.position_y, video_segment.duration, end_value)
            script.add_segment(video_segment)

        # 添加字幕
        result = process_single_subtitle(scene.caption, voice_mat.duration)
        text_start_time = start_time
        for j, item in enumerate(result):
            text_segment = draft.TextSegment(
                item['text'], Timerange(text_start_time, item['duration']),  # 文本片段的首尾与上方视频片段一致
                font=draft.FontType.江湖体,  # 设置字体
                style=draft.TextStyle(size=12, color=(1.0, 1.0, 1.0), align=1, auto_wrapping=True),
                # 字体样式
                clip_settings=draft.ClipSettings(transform_y=-0.6),  # 位置
                border=draft.TextBorder(color=(0.0, 0.0, 0.0)),  # 描边
            )
            script.add_segment(text_segment, track_name="text")
            text_start_time += item['duration']

        start_time += voice_mat.duration
        max_duration = start_time

    # 添加背景音乐
    bgm_mat = draft.AudioMaterial(base_material_path + r'\historical_bgm.mp3')  # 先创建素材实例
    if bgm_mat.duration > max_duration:
        audio_segment = draft.AudioSegment(bgm_mat,
                                           trange(0, max_duration),  # 片段将位于轨道上的0s-5s（注意5s表示持续时长而非结束时间）
                                           volume=1)  # 音量
        audio_segment.add_fade(7000000, "0s")
        script.add_segment(audio_segment, track_name="bgm")
    else:
        voice_start = 0
        voice_duration = bgm_mat.duration
        count = math.ceil(max_duration / bgm_mat.duration)
        in_duration = 7000000
        for i in range(1, count + 1):
            if i == count:
                voice_duration = max_duration - voice_start
                if voice_duration < in_duration:
                    in_duration = voice_duration
            audio_segment = draft.AudioSegment(bgm_mat,
                                               trange(voice_start, voice_duration),  # 片段将位于轨道上的0s-5s（注意5s表示持续时长而非结束时间）
                                               volume=1)  # 音量
            audio_segment.add_fade(in_duration, "0s")
            script.add_segment(audio_segment, track_name="bgm")
            voice_start += bgm_mat.duration

    # 保存草稿
    script.save()


if __name__ == '__main__':
    story_id = input("请输入故事Id：")
    create_jy_traft(int(story_id))
