"""
对docx文件的字体、字体大小、字体颜色按不同标准（标题 1\2\3，正文）进行审核
"""
import ast
from Models.FileReviewModels.DomainModels.fileReviewDomainModels import FormatError

def determine_section_type(styleItem):
    """根据格式特征判断段落类型"""
    # 优先使用段落样式判断
    styleName=styleItem.get("styleName","")
    # 匹配常见标题样式命名规则
    if 'Heading 1' in styleName or '标题 1' in styleName:
        return 'Heading 1'
    elif 'Heading 2' in styleName or '标题 2' in styleName:
        return 'Heading 2'
    elif "Heading 3" in styleName or '标题 3' in styleName:
        return 'Heading 3'

    # 默认作为正文
    else:
        return '正文'


def check_formatErrors(blocks,formatStandards):
    """检查格式规范"""
    formatErrors = []

    for block in blocks:
        for style in block["styles"]:
            # 确定当前段落类型
            section_type = determine_section_type(style)
            standard = formatStandards[section_type]
            # 检查字体
            if style.get("fontName") and style["fontName"] not in standard["allowedFonts"]:
                formatErrors.append(FormatError(
                    typeOfError=f"{section_type}字体异常",
                    currentValue=style["fontName"],
                    expectedValue=standard["allowedFonts"],
                    textSnippet=style["text"][:50]  # 截取片段
                ))

            # 检查字号
            if style.get("fontSize") and style["fontSize"] != standard["fontSize"]:
                formatErrors.append(FormatError(
                    typeOfError=f"{section_type}字体大小异常",
                    currentValue=f"{style['fontSize']}pt",
                    expectedValue=f"{standard['fontSize']}pt",
                    textSnippet=style["text"][:50]  # 截取片段
                ))

            # 检查字体颜色
            if isinstance(style.get("fontColor"), tuple) and style["fontColor"] != ast.literal_eval(standard["fontColor"]):
                formatErrors.append(FormatError(
                    typeOfError=f"{section_type}字体颜色异常",
                    currentValue=rgb_to_hex(style["fontColor"]),
                    expectedValue=rgb_to_hex(ast.literal_eval(standard["fontColor"])),
                    textSnippet=style["text"][:50]
                ))

    print(f"格式检查完成，找到 {len(formatErrors)} 个错误")
    return formatErrors


def rgb_to_hex(rgb):
    """将RGB元组转换为十六进制"""
    return "#{:02x}{:02x}{:02x}".format(*rgb[:3]) # 只取前三个通道


