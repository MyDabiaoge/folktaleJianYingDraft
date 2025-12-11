import re
import math

SUB_CONFIG = {
    'MAX_LINE_LENGTH': 25,
    'SPLIT_PRIORITY': ['。', '！', '？', '，', ',', '：', ':', '、', '；', ';', ' '],
    'TIME_PRECISION': 3
}


def split_long_phrase(text, max_len):
    """分割长文本，确保每段不超过最大长度"""
    if len(text) <= max_len:
        return [text]

    # 在max_len范围内查找分隔符
    for delimiter in SUB_CONFIG['SPLIT_PRIORITY']:
        # 查找最后一个分隔符的位置（在max_len-1范围内）
        try:
            pos = text.rfind(delimiter, 0, max_len - 1)
            if pos > 0:
                split_pos = pos + 1
                return [
                    text[:split_pos].strip(),
                    *split_long_phrase(text[split_pos:].strip(), max_len)
                ]
        except ValueError:
            continue

    # 汉字边界检查
    start_pos = min(max_len, len(text)) - 1
    for i in range(start_pos, 0, -1):
        # 检查是否为汉字（CJK统一表意文字）
        if re.match(
                r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002b73f\U0002b740-\U0002b81f\U0002b820-\U0002ceaf]',
                text[i]):
            return [
                text[:i + 1].strip(),
                *split_long_phrase(text[i + 1:].strip(), max_len)
            ]

    # 强制分割
    split_pos = min(max_len, len(text))
    return [
        text[:split_pos].strip(),
        *split_long_phrase(text[split_pos:].strip(), max_len)
    ]


def process_subtitles(captions, subtitle_durations, start_time_us=0):
    """
    处理字幕，分割长句并生成时间轴

    Args:
        captions: 字幕文本列表
        subtitle_durations: 每段字幕的持续时间（微秒）
        start_time_us: 起始时间（微秒，默认为0）

    Returns:
        dict: 包含textTimelines和processedSubtitles的字典
    """
    # 清理正则表达式：匹配中文标点、全角标点、英文标点等
    clean_regex = re.compile(r'[\u3000\u3002-\u303F\uff00-\uffef\u2000-\u206F!"#$%&\'()*+\-./<=>?@\\^_`{|}~]')

    processed_subtitles = []
    processed_subtitle_durations = []

    for index, text in enumerate(captions):
        total_duration = subtitle_durations[index]

        # 分割长句
        phrases = split_long_phrase(text, SUB_CONFIG['MAX_LINE_LENGTH'])

        # 清理文本
        phrases = [clean_regex.sub('', p).strip() for p in phrases]
        phrases = [p for p in phrases if p]  # 移除空字符串

        if not phrases:
            processed_subtitles.append('[无内容]')
            processed_subtitle_durations.append(total_duration)
            continue

        # 计算总字符数
        total_chars = sum(len(p) for p in phrases)
        accumulated_us = 0

        # 分配时间
        for i, phrase in enumerate(phrases):
            ratio = len(phrase) / total_chars
            if i == len(phrases) - 1:
                # 最后一段使用剩余时间
                duration_us = total_duration - accumulated_us
            else:
                duration_us = round(total_duration * ratio)

            processed_subtitles.append(phrase)
            processed_subtitle_durations.append(duration_us)
            accumulated_us += duration_us

    # 生成时间轴
    text_timelines = []
    current_time = start_time_us

    for duration_us in processed_subtitle_durations:
        start_time = current_time
        end_time = start_time + duration_us

        text_timelines.append({
            'start': start_time,
            'end': end_time
        })

        current_time = end_time

    return {
        'textTimelines': text_timelines,
        'processedSubtitles': processed_subtitles
    }


def process_single_subtitle(text, total_duration_us):
    """
    处理单个字幕，分割长句并按字符比例分配时间

    Args:
        text: 字幕文本
        total_duration_us: 总持续时间（微秒）

    Returns:
        list: 包含字典的列表，每个字典包含text和duration
    """
    # 清理正则表达式：匹配中文标点、全角标点、英文标点等
    clean_regex = re.compile(r'[\u3000\u3002-\u303F\uff00-\uffef\u2000-\u206F!"#$%&\'()*+\-./<=>?@\\^_`{|}~]')

    # 分割长句
    phrases = split_long_phrase(text, SUB_CONFIG['MAX_LINE_LENGTH'])

    # 清理文本
    phrases = [clean_regex.sub('', p).strip() for p in phrases]
    phrases = [p for p in phrases if p]  # 移除空字符串

    if not phrases:
        return [{'text': '[无内容]', 'duration': total_duration_us}]

    # 计算总字符数
    total_chars = sum(len(p) for p in phrases)
    accumulated_us = 0
    result = []

    # 分配时间
    for i, phrase in enumerate(phrases):
        ratio = len(phrase) / total_chars

        if i == len(phrases) - 1:
            # 最后一段使用剩余时间
            duration_us = total_duration_us - accumulated_us
        else:
            duration_us = round(total_duration_us * ratio)

        result.append({
            'text': phrase,
            'duration': duration_us
        })

        accumulated_us += duration_us

    return result


# 使用示例
if __name__ == "__main__":
    # # 示例数据
    # captions = [
    #     "这是一个测试字幕，用来测试长句分割功能。这个句子很长，需要被分割成多个短句。",
    #     "短句不需要分割。",
    #     "这个句子也特别长，需要被分割成多个部分以便更好地显示在屏幕上。"
    # ]
    #
    # subtitle_durations = [5000000, 2000000, 6000000]  # 微秒
    #
    # # 处理字幕
    # result = process_subtitles(captions, subtitle_durations, start_time_us=0)
    #
    # print("处理后的字幕:")
    # for i, subtitle in enumerate(result['processedSubtitles']):
    #     timeline = result['textTimelines'][i]
    #     print(f"时间: {timeline['start']}μs - {timeline['end']}μs, 文本: {subtitle}")
    #
    # print(f"\n总字幕数: {len(result['processedSubtitles'])}")

    # 测试用例
    test_text = "这是一个测试字幕，用来测试长句分割功能。这个句子很长，需要被分割成多个短句，"
    test_duration = 5000000  # 微秒

    result = process_single_subtitle(test_text, test_duration)

    print("原始文本:")
    print(f"  '{test_text}'")
    print(f"总时长: {test_duration}μs ({test_duration / 1000000:.3f}秒)")
    print("\n分割结果:")

    for i, item in enumerate(result):
        seconds = item['duration'] / 1000000
        print(f"  片段 {i + 1}: 文本='{item['text']}'")
        print(f"        时长: {item['duration']}μs ({seconds:.3f}秒)")
        print(f"        字数: {len(item['text'])}")

    print(f"\n总片段数: {len(result)}")

    # 验证总时长
    total_result_duration = sum(item['duration'] for item in result)
    print(f"\n总时长验证: {total_result_duration}μs ({total_result_duration / 1000000:.3f}秒)")