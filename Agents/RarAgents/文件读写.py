import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from Models.RarModels.DomainModels.rarDomainModels import RarData
from typing import List, Dict, Any
import json
from pathlib import Path


def read_urs_file(file_path: str) -> List[RarData]:
    """
    解析URS Excel文件，提取需求数据并存储为RarData对象列表

    Args:
        file_path: URS Excel文件路径

    Returns:
        RarData对象列表
    """
    urs_data_list = []
    df = pd.read_excel(file_path, sheet_name=None)
    print('正在读取数据...')

    for sheet_name, sheet in df.items():
        # current_module = None  # 当前模块状态维持

        # 使用itertuples提升性能
        for row in sheet.itertuples(index=False):
            first_cell = str(row[0]).strip()

            # 空行跳过而不终止
            if not first_cell:
                continue

            if len(first_cell) < 1:  # 最小长度检查
                continue
            # 新增ASCII码验证逻辑
            first_char = first_cell[0]  # 不再转换大小写
            char_code = ord(first_char)
            if not (0 <= char_code <= 127):  # 所有ASCII字符
                continue

            # 需求行处理
            urs_data = RarData(
                UrsNo=first_cell,
                RequirementDesc=str(row[1]).strip(),
                BelongChapter=sheet_name
            )
            urs_data_list.append(urs_data)

    print(f"共读取{len(urs_data_list)}条数据")
    return urs_data_list


def write_excel(template_file_path: str,output_file_path:str,rar_data_array: List[RarData]) -> None:
    """
    将分析后的RAR数据写入Excel模板文件
    Args:
        template_file_path: RAR模板Excel文件路径
        output_file_path: 输出文件路径
        rar_data_array: RarData对象列表
    """
    # 确保输出目录存在
    output_dir = Path(output_file_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    workbook = load_workbook(template_file_path)
    worksheet = workbook.active

    start_row = 6
    total_items = len(rar_data_array)
    print(f"共需写入{total_items}条数据\n")

    for idx, data in enumerate(rar_data_array, start_row):
        row = idx
        print(f"正在写入第{row - 5}条数据...\n")

        # 将数据写入Excel
        worksheet[f"A{row}"] = data.UrsNo
        worksheet[f"B{row}"] = data.RequirementDesc
        worksheet[f"C{row}"] = data.FailureEvent
        worksheet[f"D{row}"] = data.PotentialFailureConsequences
        worksheet[f"E{row}"] = data.Severity
        worksheet[f"F{row}"] = data.Probability
        worksheet[f"G{row}"] = data.RiskLevel
        worksheet[f"H{row}"] = data.Detectability
        worksheet[f"I{row}"] = data.RiskPriority

        # J列因内容较长特殊处理（风险控制措施）
        cell = worksheet[f"J{row}"]
        cell.value = data.RiskControlMeasures
        # 插入换行符
        cell.value = cell.value.replace(',', ',\n') if cell.value else ""
        # 启用自动换行
        cell.alignment = Alignment(wrap_text=True)

    # 调整列宽适应内容
    worksheet.column_dimensions['J'].width = 40

    workbook.save(output_file_path)
    print(f"文件写入成功，共写入{total_items}条数据")


def export_to_json(rar_data_array: List[RarData],output_file_path:str) -> None:
    """
    将RAR数据保存为json文件

    Args:
        rar_data_array: RarData对象列表

    """
    # 将Pydantic模型转换为字典列表
    data_list = [data.dict() for data in rar_data_array]

    # 创建结果对象
    result = {
        "totalItems": len(data_list),
        "items": data_list
    }

    # 确保输出目录存在
    json_path = Path(output_file_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    # 写入JSON文件
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"JSON数据已保存至: {output_file_path}")

    # 返回JSON字符串
    # return json.dumps(result, ensure_ascii=False)