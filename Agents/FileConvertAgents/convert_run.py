# file: Agents/FileConvertAgents/convert_run.py
"""
文件格式转换执行模块
处理具体的文件格式转换逻辑
"""

import os
import logging
import tempfile
import uuid
import shutil
from typing import Dict, Any
import importlib

from Configs.FileConvertConfig.convert_config_init import conversion_config

logger = logging.getLogger("convert_run")


def get_supported_formats_info():
    """
    获取支持的转换格式信息

    Returns:
        包含所有支持格式的字典
    """
    format_info = {}
    conversion_map=conversion_config["conversion_map"]
    format_descriptions=conversion_config["format_descriptions"]

    for source_ext, target_info in conversion_map.items():
        format_info[source_ext] = {
            "description": format_descriptions.get(source_ext, f'{source_ext}格式文件'),
            "target_formats": [
                {
                    "extension": target_ext,
                    "description": format_descriptions.get(target_ext, f'{target_ext}格式文件')
                }
                for target_ext in target_info["target_formats"]
            ]
        }
    return format_info


async def execute_conversion(file, target_format: str) -> Dict[str, Any]:
    """
    执行文档格式转换

    Args:
        file: 上传的文件对象
        target_format: 目标格式

    Returns:
        包含输出文件路径和相关信息的字典
    """
    logger.info(f"Received conversion request: {file.filename} to {target_format}")

    # 获取文件扩展名
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()

    # 验证输入格式
    supported_formats = set(conversion_config["supported_input_formats"])
    if ext not in supported_formats:
        raise ValueError(
            f"不支持的输入格式: {ext}。支持的格式: {', '.join(supported_formats)}"
        )

    target_format = target_format.lower()
    target_ext = f".{target_format}"

    # 验证目标格式
    conversion_map = conversion_config["conversion_map"]
    if ext not in conversion_map:
        raise ValueError(f"不支持的输入格式: {ext}")

    if target_ext not in conversion_map[ext]["target_formats"]:
        available_formats = ', '.join([fmt[1:] for fmt in conversion_map[ext]["target_formats"]])
        raise ValueError(
            f"无法将 {ext} 转换为 {target_format}。支持的目标格式: {available_formats}"
        )

    # 使用系统临时目录，避免权限问题
    temp_dir = tempfile.mkdtemp()
    try:
        # 保存上传文件
        input_path = os.path.join(temp_dir, file.filename)
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # 生成输出文件路径
        # 保证文件名不重复
        output_filename = f"{os.path.splitext(file.filename)[0]}_{uuid.uuid4().hex[:8]}{target_ext}"
        output_path = os.path.join(temp_dir, output_filename)

        # 执行转换
        await _perform_conversion(input_path, output_path, ext, target_ext)

        # 检查输出文件是否存在
        if not os.path.exists(output_path):
            raise Exception("转换失败：输出文件未正确生成")

        return {
            "temp_dir": temp_dir,
            "output_path": output_path,
            "output_filename": output_filename,
            "media_type": _get_media_type(target_ext)
        }

    except Exception as e:
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
        except Exception as cleanup_error:
            logger.warning(f"Failed to clean up temp directory {temp_dir}: {cleanup_error}")
        raise e


async def _perform_conversion(input_path: str, output_path: str, source_ext: str, target_ext: str):
    """
    执行具体的文件格式转换（插件化）

    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        source_ext: 源文件扩展名
        target_ext: 目标文件扩展名
    """
    logger.info(f"Performing conversion from {source_ext} to {target_ext}")

    try:
        conversion_map = conversion_config["conversion_map"]
        converter_name = conversion_map[source_ext]["converter"]

        # 动态导入转换器模块
        converter_module = importlib.import_module(f"Agents.FileConvertAgents.{converter_name}")

        # 构造转换函数名
        convert_func_name = f"convert_{source_ext[1:]}_to_{target_ext[1:]}"

        # 检查是否存在特定的转换函数
        if hasattr(converter_module, convert_func_name):
            convert_func = getattr(converter_module, convert_func_name)
            convert_func(input_path, output_path)
        else:
            # 如果没有特定函数，尝试使用通用转换方法
            logger.warning(f"未找到特定转换函数 {convert_func_name}，尝试通用转换方法")

            # 抛出异常
            raise Exception(f"不支持的转换：{source_ext} 到 {target_ext}")
            # # 为了保持向后兼容，我们保留原有的转换逻辑
            # _perform_conversion_legacy(converter_module, input_path, output_path, source_ext, target_ext)

        logger.info(f"Conversion completed: {output_path}")

    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        raise e


def _get_media_type(ext: str) -> str:
    """
    根据文件扩展名获取MIME类型

    Args:
        ext: 文件扩展名

    Returns:
        MIME类型字符串
    """
    media_types = conversion_config["media_types"]
    return media_types.get(ext, 'application/octet-stream')
