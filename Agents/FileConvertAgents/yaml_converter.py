"""
YAML文件转换代理
处理YAML到其他格式的转换
"""

import yaml
import json


def convert_yaml_to_json(input_path: str, output_path: str):
    """将YAML转换为JSON"""
    with open(input_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(yaml_data, f, indent=2, ensure_ascii=False)


def convert_yaml_to_txt(input_path: str, output_path: str):
    """将YAML转换为纯文本"""
    with open(input_path, 'r', encoding='utf-8') as f:
        yaml_data = yaml.safe_load(f)

    txt_content = yaml.dump(yaml_data, allow_unicode=True, default_flow_style=False)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(txt_content)

