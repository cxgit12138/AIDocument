"""
1.split_into_textblocks:语法审核、术语库审核使用，不会切分完整句子，按句子分割文本为不超过max_length的块
2.split_into_blocks:格式审核专用，因为“文本内容提取”是以run为单位，所以可能将完整句子分割
"""

import re

def split_into_textblocks(text, max_length):
    """语法审核、术语库审核使用，不会切分完整句子，按句子分割文本为不超过max_length的块"""

    # 使用正则表达式匹配句子，分割成句子列表
    sentences = re.split(r'(?<=[。！？.?!])', text)
    text_blocks = []  #存储最终分割后的块
    current_block = []  #当前正在构建的块
    current_length = 0  #当前块的总字符数

    for sent in sentences:
        if not sent.strip(): #跳过仅含空白的句子
            continue
        if current_length + len(sent) <= max_length: #判断不超过max_length的前提下加入当前块
            current_block.append(sent)
            current_length += len(sent)
        else:#若超过max_length,将当前块合并为字符串并加入 blocks。重置 current_block 为当前句子，current_length 为该句子的长度。
            text_blocks.append(''.join(current_block))
            current_block = [sent]
            current_length = len(sent)
    if current_block:#将剩余 current_block 合并并加入结果列表
        text_blocks.append(''.join(current_block))
    return text_blocks

def split_into_blocks(styled_content, max_length):
    """格式审核使用"""
    blocks = []
    current_block = []
    current_text = ""

    # 直接遍历样式项，保留原始顺序
    for item in styled_content:
        new_text = current_text + item["text"]

        # 分块条件：超过长度或遇到句子结尾
        if len(new_text) > max_length or re.search(r'[。！？.?!]$', new_text):
            if current_block:
                blocks.append({
                    "text": current_text,
                    "styles": current_block
                })
                current_block = []
                current_text = ""

        current_block.append(item)
        current_text += item["text"]

    # 处理剩余内容
    if current_block:
        blocks.append({"text": current_text, "styles": current_block})
    return blocks