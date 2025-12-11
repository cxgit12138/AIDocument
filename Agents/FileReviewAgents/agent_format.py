"""
对docx文件的字体、字体大小、字体颜色按不同标准（标题 1\2\3，正文）进行审核
格式审核不设计外部API调用，保留同步逻辑，不使用异步处理
"""
import ast
from Models.FileReviewModels.DomainModels.file_review_domain_models import FormatError

def determine_section_type(style_item):
    """根据格式特征判断段落类型"""
    # 优先使用段落样式判断
    style_name = style_item.get("style_name", "")
    # 匹配常见标题样式命名规则
    if 'Heading 1' in style_name or '标题 1' in style_name:
        return 'Heading 1'
    elif 'Heading 2' in style_name or '标题 2' in style_name:
        return 'Heading 2'
    elif "Heading 3" in style_name or '标题 3' in style_name:
        return 'Heading 3'

    # 默认作为正文
    else:
        return '正文'


def check_format_errors(blocks, format_standards):
    """检查格式规范"""
    format_errors = []

    for block in blocks:
        for style in block["styles"]:
            # 确定当前段落类型
            section_type = determine_section_type(style)
            standard = format_standards[section_type]
            
            # 检查字体
            if style.get("font_name") and style["font_name"] not in standard["allowed_fonts"]:
                # noinspection PyArgumentList
                format_errors.append(FormatError(
                    type_of_error=f"{section_type}字体异常",
                    current_value=style["font_name"],
                    expected_value=standard["allowed_fonts"],
                    text_snippet=style["text"][:50]  # 截取片段
                ))

            # 检查字号
            if style.get("font_size") and style["font_size"] != standard["font_size"]:
                # noinspection PyArgumentList
                format_errors.append(FormatError(
                    type_of_error=f"{section_type}字体大小异常",
                    current_value=f"{style['font_size']}pt",
                    expected_value=f"{standard['font_size']}pt",
                    text_snippet=style["text"][:50]  # 截取片段
                ))

            # 检查字体颜色
            if isinstance(style.get("font_color"), tuple) and style["font_color"] != ast.literal_eval(standard["font_color"]):
                # noinspection PyArgumentList
                format_errors.append(FormatError(
                    type_of_error=f"{section_type}字体颜色异常",
                    current_value=rgb_to_hex(style["font_color"]),
                    expected_value=rgb_to_hex(ast.literal_eval(standard["font_color"])),
                    text_snippet=style["text"][:50]
                ))

    print(f"格式检查完成，找到 {len(format_errors)} 个错误")
    return format_errors


def rgb_to_hex(rgb):
    """将RGB元组转换为十六进制"""
    return "#{:02x}{:02x}{:02x}".format(*rgb[:3]) # 只取前三个通道



