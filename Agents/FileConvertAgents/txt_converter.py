"""
纯文本文件转换代理
处理TXT到其他格式的转换
"""



def convert_txt_to_md(input_path: str, output_path: str):
    """将纯文本转换为Markdown"""
    with open(input_path, 'r', encoding='utf-8') as f:
        txt_content = f.read()

    # 简单处理，将文本包装在Markdown中
    md_content = txt_content

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(md_content)


def convert_txt_to_html(input_path: str, output_path: str):
    """将纯文本转换为HTML"""
    with open(input_path, 'r', encoding='utf-8') as f:
        txt_content = f.read()

    # 简单处理，将文本包装在HTML中
    html_content = f"<html><body><pre>{txt_content}</pre></body></html>"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

