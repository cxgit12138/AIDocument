"""
PDF文件转换代理
处理PDF到其他格式的转换，保留字体样式和颜色
"""

import PyPDF2
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LAParams, LTTextContainer, LTChar, LTTextLine
from typing import Dict, Any, List
import os
import re


# ==================== 工具函数（被转换函数调用） ====================

def get_text_formatting(element) -> List[Dict[str, Any]]:
    """提取文本的格式信息（字体、大小、颜色）"""
    formatted_texts = []

    if isinstance(element, LTTextContainer):
        for text_line in element:
            if isinstance(text_line, LTTextLine):
                current_format = None
                current_text = ""

                for char in text_line:
                    if isinstance(char, LTChar):
                        char_format = {
                            'font': char.fontname,
                            'size': round(char.height, 1),
                            'color': get_color_from_char(char),
                            'bold': is_bold(char.fontname),
                            'italic': is_italic(char.fontname)
                        }

                        if current_format and current_format != char_format:
                            if current_text.strip():
                                formatted_texts.append({
                                    'text': current_text,
                                    'format': current_format
                                })
                            current_text = char.get_text()
                            current_format = char_format
                        else:
                            current_text += char.get_text()
                            current_format = char_format
                    else:
                        current_text += char.get_text()

                if current_text.strip():
                    formatted_texts.append({
                        'text': current_text,
                        'format': current_format if current_format else {}
                    })

    return formatted_texts


def get_color_from_char(char: LTChar) -> str:
    """从字符中提取颜色信息"""
    try:
        if hasattr(char, 'graphicstate'):
            if hasattr(char.graphicstate, 'ncolor'):
                color = char.graphicstate.ncolor
                if color:
                    return rgb_to_hex(color)
            if hasattr(char.graphicstate, 'scolor'):
                color = char.graphicstate.scolor
                if color:
                    return rgb_to_hex(color)
    except:
        pass
    return '#000000'


def rgb_to_hex(color) -> str:
    """将RGB颜色转换为十六进制"""
    try:
        if isinstance(color, (list, tuple)):
            if len(color) >= 3:
                r, g, b = color[:3]
                return '#{:02x}{:02x}{:02x}'.format(
                    int(r * 255), int(g * 255), int(b * 255)
                )
        elif isinstance(color, (int, float)):
            gray = int(color * 255)
            return '#{:02x}{:02x}{:02x}'.format(gray, gray, gray)
    except:
        pass
    return '#000000'


def is_bold(fontname: str) -> bool:
    """判断字体是否为粗体"""
    fontname_lower = fontname.lower()
    return 'bold' in fontname_lower or 'heavy' in fontname_lower or 'black' in fontname_lower


def is_italic(fontname: str) -> bool:
    """判断字体是否为斜体"""
    fontname_lower = fontname.lower()
    return 'italic' in fontname_lower or 'oblique' in fontname_lower


def is_heading(format_info: Dict[str, Any], avg_size: float) -> int:
    """判断是否为标题及标题级别"""
    if not format_info:
        return 0

    size = format_info.get('size', 0)
    bold = format_info.get('bold', False)

    if size >= avg_size * 1.5:
        return 1
    elif size >= avg_size * 1.3:
        return 2
    elif size >= avg_size * 1.15:
        return 3
    elif bold and size >= avg_size * 1.05:
        return 4

    return 0


def calculate_average_font_size(input_path: str) -> float:
    """计算文档的平均字体大小"""
    laparams = LAParams()
    sizes = []

    for page_layout in extract_pages(input_path, laparams=laparams):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                    if isinstance(text_line, LTTextLine):
                        for char in text_line:
                            if isinstance(char, LTChar):
                                sizes.append(char.height)

    return sum(sizes) / len(sizes) if sizes else 12.0


def format_text_to_html(item: Dict[str, Any]) -> str:
    """将格式化文本转换为HTML"""
    text = item.get('text', '')
    format_info = item.get('format', {})

    if not text.strip():
        return text

    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    styles = []
    classes = []

    if 'size' in format_info and format_info['size']:
        styles.append(f"font-size: {format_info['size']}pt")

    if 'color' in format_info and format_info['color'] != '#000000':
        styles.append(f"color: {format_info['color']}")

    if format_info.get('bold', False):
        classes.append('bold')

    if format_info.get('italic', False):
        classes.append('italic')

    if styles or classes:
        style_attr = f' style="{"; ".join(styles)}"' if styles else ''
        class_attr = f' class="{" ".join(classes)}"' if classes else ''
        return f'<span{class_attr}{style_attr}>{text}</span>'

    return text


# ==================== 转换函数（被 convert_run.py 调用） ====================

def convert_pdf_to_txt(input_path: str, output_path: str):
    """
    将PDF转换为纯文本，保留段落结构

    Args:
        input_path: 输入PDF文件路径
        output_path: 输出TXT文件路径
    """
    try:
        laparams = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            detect_vertical=True
        )

        text = extract_text(input_path, laparams=laparams)

        # 智能清理文本，保留段落
        paragraphs = []
        current_paragraph = []

        for line in text.splitlines():
            line = line.strip()
            if not line:
                if current_paragraph:
                    paragraphs.append(' '.join(current_paragraph))
                    current_paragraph = []
            else:
                current_paragraph.append(line)

        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))

        cleaned_text = '\n\n'.join(paragraphs)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

    except Exception as e:
        raise Exception(f"PDF转换为TXT失败: {str(e)}")


def convert_pdf_to_html(input_path: str, output_path: str):
    """
    将PDF转换为HTML，保留字体样式和颜色

    Args:
        input_path: 输入PDF文件路径
        output_path: 输出HTML文件路径
    """
    try:
        laparams = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            detect_vertical=True
        )

        avg_font_size = calculate_average_font_size(input_path)
        html_parts = []

        for page_num, page_layout in enumerate(extract_pages(input_path, laparams=laparams), 1):
            page_html = f'<div class="page" data-page="{page_num}">\n'

            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    formatted_texts = get_text_formatting(element)

                    if not formatted_texts:
                        continue

                    first_format = formatted_texts[0].get('format', {})
                    heading_level = is_heading(first_format, avg_font_size)

                    if heading_level > 0:
                        page_html += f'<h{heading_level}>'
                        for item in formatted_texts:
                            page_html += format_text_to_html(item)
                        page_html += f'</h{heading_level}>\n'
                    else:
                        page_html += '<p>'
                        for item in formatted_texts:
                            page_html += format_text_to_html(item)
                        page_html += '</p>\n'

            page_html += '</div>\n'
            html_parts.append(page_html)

        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Converted PDF Document</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .page {{
            margin-bottom: 40px;
            padding-bottom: 40px;
            border-bottom: 2px solid #eee;
        }}
        .page:last-child {{
            border-bottom: none;
        }}
        h1, h2, h3, h4, h5, h6 {{
            margin-top: 20px;
            margin-bottom: 10px;
            line-height: 1.3;
        }}
        p {{
            margin: 10px 0;
            line-height: 1.6;
            text-align: justify;
        }}
        .bold {{
            font-weight: bold;
        }}
        .italic {{
            font-style: italic;
        }}
    </style>
</head>
<body>
<div class="container">
{''.join(html_parts)}
</div>
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

    except Exception as e:
        raise Exception(f"PDF转换为HTML失败: {str(e)}")


def convert_pdf_to_md(input_path: str, output_path: str):
    """
    将PDF转换为Markdown，保留基本格式

    Args:
        input_path: 输入PDF文件路径
        output_path: 输出MD文件路径
    """
    try:
        laparams = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            detect_vertical=True
        )

        avg_font_size = calculate_average_font_size(input_path)
        md_content = []

        for page_num, page_layout in enumerate(extract_pages(input_path, laparams=laparams), 1):
            if page_num > 1:
                md_content.append('\n---\n')

            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    formatted_texts = get_text_formatting(element)

                    if not formatted_texts:
                        continue

                    first_format = formatted_texts[0].get('format', {})
                    heading_level = is_heading(first_format, avg_font_size)

                    text_parts = []
                    for item in formatted_texts:
                        text = item.get('text', '')
                        format_info = item.get('format', {})

                        if format_info.get('bold', False) and format_info.get('italic', False):
                            text = f'***{text}***'
                        elif format_info.get('bold', False):
                            text = f'**{text}**'
                        elif format_info.get('italic', False):
                            text = f'*{text}*'

                        text_parts.append(text)

                    full_text = ''.join(text_parts).strip()

                    if not full_text:
                        continue

                    if heading_level > 0:
                        md_content.append(f'\n{"#" * heading_level} {full_text}\n')
                    else:
                        md_content.append(f'{full_text}\n')

                    md_content.append('\n')

        final_content = ''.join(md_content)
        final_content = re.sub(r'\n{3,}', '\n\n', final_content)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)

    except Exception as e:
        raise Exception(f"PDF转换为Markdown失败: {str(e)}")


# ==================== 辅助功能函数（可选，供其他模块调用） ====================

def get_pdf_info(input_path: str) -> Dict[str, Any]:
    """
    获取PDF文档基本信息

    Args:
        input_path: PDF文件路径

    Returns:
        包含PDF信息的字典
    """
    try:
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            info: Dict[str, Any] = {
                "page_count": len(reader.pages),
                "file_size": os.path.getsize(input_path)
            }

            doc_info = reader.metadata
            if doc_info:
                info["title"] = str(doc_info.get("/Title", ""))
                info["author"] = str(doc_info.get("/Author", ""))
                info["subject"] = str(doc_info.get("/Subject", ""))
                info["creator"] = str(doc_info.get("/Creator", ""))
                info["producer"] = str(doc_info.get("/Producer", ""))
                info["creation_date"] = str(doc_info.get("/CreationDate", ""))
                info["modification_date"] = str(doc_info.get("/ModDate", ""))

            return info

    except Exception as e:
        raise Exception(f"获取PDF信息失败: {str(e)}")


def extract_pdf_pages(input_path: str, output_path: str, page_numbers: List[int]):
    """
    提取PDF指定页面

    Args:
        input_path: 输入PDF文件路径
        output_path: 输出PDF文件路径
        page_numbers: 要提取的页码列表（从1开始）
    """
    try:
        with open(input_path, 'rb') as input_file:
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()

            for page_num in page_numbers:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
                else:
                    raise Exception(f"页面 {page_num} 不存在")

            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

    except Exception as e:
        raise Exception(f"提取PDF页面失败: {str(e)}")