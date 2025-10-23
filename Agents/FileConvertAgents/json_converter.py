"""
JSON文件转换代理
处理JSON到其他格式的转换
"""

import json
import yaml
from typing import Dict, Any, Union
import csv
from xml.etree import ElementTree as ET
from xml.dom import minidom


def convert_json_to_yaml(input_path: str, output_path: str):
    """将JSON转换为YAML"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(json_data, f, allow_unicode=True, default_flow_style=False, indent=2)
    except json.JSONDecodeError as e:
        raise Exception(f"JSON格式错误: {str(e)}")
    except Exception as e:
        raise Exception(f"转换失败: {str(e)}")


def convert_json_to_txt(input_path: str, output_path: str):
    """将JSON转换为纯文本"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        txt_content = json.dumps(json_data, indent=2, ensure_ascii=False)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
    except json.JSONDecodeError as e:
        raise Exception(f"JSON格式错误: {str(e)}")
    except Exception as e:
        raise Exception(f"转换失败: {str(e)}")


def convert_json_to_csv(input_path: str, output_path: str):
    """将JSON数组转换为CSV"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # 检查数据是否为数组
        if not isinstance(json_data, list):
            raise Exception("JSON数据必须是数组格式才能转换为CSV")

        if not json_data:
            raise Exception("JSON数组为空")

        # 获取所有可能的字段名
        fieldnames = set()
        for item in json_data:
            if isinstance(item, dict):
                fieldnames.update(item.keys())

        fieldnames = sorted(list(fieldnames))

        # 写入CSV文件
        with open(output_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for item in json_data:
                if isinstance(item, dict):
                    # 处理嵌套对象，将其转换为字符串
                    processed_item = {}
                    for key, value in item.items():
                        if isinstance(value, (dict, list)):
                            processed_item[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            processed_item[key] = value
                    writer.writerow(processed_item)
    except json.JSONDecodeError as e:
        raise Exception(f"JSON格式错误: {str(e)}")
    except Exception as e:
        raise Exception(f"转换失败: {str(e)}")


def convert_json_to_xml(input_path: str, output_path: str):
    """将JSON转换为XML"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        # 创建根元素
        root = ET.Element("root")

        # 递归转换JSON到XML
        _dict_to_xml(json_data, root)

        # 格式化XML
        rough_string = ET.tostring(root, encoding='utf-8')
        reparsed = minidom.parseString(rough_string)
        xml_content = reparsed.toprettyxml(indent="  ", encoding='utf-8').decode('utf-8')

        # 移除XML声明中的版本信息（如果不需要）
        lines = xml_content.split('\n')
        if lines and '<?xml' in lines[0]:
            lines = lines[1:]
        xml_content = '\n'.join(lines)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
    except json.JSONDecodeError as e:
        raise Exception(f"JSON格式错误: {str(e)}")
    except Exception as e:
        raise Exception(f"转换失败: {str(e)}")


def _dict_to_xml(data: Union[Dict, Any], parent: ET.Element, key: str = "item"):
    """递归将字典转换为XML元素"""
    if isinstance(data, dict):
        for k, v in data.items():
            element = ET.SubElement(parent, k)
            _dict_to_xml(v, element, k)
    elif isinstance(data, list):
        for item in data:
            element = ET.SubElement(parent, key)
            _dict_to_xml(item, element, "item")
    else:
        parent.text = str(data)


def validate_json(input_path: str) -> Dict[str, Any]:
    """验证JSON文件格式并返回基本信息"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        info = {
            "valid": True,
            "size": len(json.dumps(json_data, ensure_ascii=False)),
            "type": type(json_data).__name__,
        }

        if isinstance(json_data, dict):
            info["keys_count"] = len(json_data)
            info["keys"] = list(json_data.keys())
        elif isinstance(json_data, list):
            info["items_count"] = len(json_data)
            if json_data:
                first_item = json_data[0]
                if isinstance(first_item, dict):
                    info["item_keys"] = list(first_item.keys())

        return info
    except json.JSONDecodeError as e:
        return {
            "valid": False,
            "error": str(e)
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"读取文件时出错: {str(e)}"
        }


def convert_json_to_html(input_path: str, output_path: str):
    """将JSON转换为HTML表格展示"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)

        html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>JSON Data</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        tr:nth-child(even) { background-color: #f9f9f9; }
    </style>
</head>
<body>
"""

        if isinstance(json_data, list) and json_data:
            # 处理数组数据
            html_content += "<h1>JSON Array Data</h1>\n"

            # 获取所有字段名
            fieldnames = set()
            for item in json_data:
                if isinstance(item, dict):
                    fieldnames.update(item.keys())

            fieldnames = sorted(list(fieldnames))

            # 创建表格
            html_content += "<table>\n"
            html_content += "<thead>\n<tr>\n"
            for field in fieldnames:
                html_content += f"<th>{field}</th>\n"
            html_content += "</tr>\n</thead>\n"

            html_content += "<tbody>\n"
            for item in json_data:
                html_content += "<tr>\n"
                if isinstance(item, dict):
                    for field in fieldnames:
                        value = item.get(field, "")
                        # 处理嵌套对象
                        if isinstance(value, (dict, list)):
                            value = json.dumps(value, ensure_ascii=False)
                        html_content += f"<td>{value}</td>\n"
                else:
                    html_content += f"<td>{item}</td>\n"
                html_content += "</tr>\n"
            html_content += "</tbody>\n"
            html_content += "</table>\n"

        elif isinstance(json_data, dict):
            # 处理对象数据
            html_content += "<h1>JSON Object Data</h1>\n"
            html_content += "<table>\n"
            html_content += "<thead>\n<tr>\n<th>Key</th>\n<th>Value</th>\n</tr>\n</thead>\n"
            html_content += "<tbody>\n"

            for key, value in json_data.items():
                html_content += "<tr>\n"
                html_content += f"<td>{key}</td>\n"
                # 处理嵌套对象
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, ensure_ascii=False, indent=2)
                    html_content += f"<td><pre>{value_str}</pre></td>\n"
                else:
                    html_content += f"<td>{value}</td>\n"
                html_content += "</tr>\n"

            html_content += "</tbody>\n"
            html_content += "</table>\n"
        else:
            # 处理简单值
            html_content += f"<h1>JSON Value</h1>\n<p>{json_data}</p>\n"

        html_content += "</body>\n</html>"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

    except json.JSONDecodeError as e:
        raise Exception(f"JSON格式错误: {str(e)}")
    except Exception as e:
        raise Exception(f"转换失败: {str(e)}")