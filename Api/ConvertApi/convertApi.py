"""
文档格式转换API模块
支持多种文档格式之间的相互转换
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException,BackgroundTasks
from fastapi.responses import FileResponse
import tempfile
import os
from typing import List
import logging
import shutil
import uuid

from Agents.FileConvertAgents import md_converter, txt_converter, docx_converter
from Agents.FileConvertAgents import pdf_converter, html_converter, json_converter, yaml_converter

router = APIRouter()
logger = logging.getLogger("convert_api")

# 支持的输入格式
SUPPORTED_INPUT_FORMATS = {'.md', '.txt', '.docx', '.pdf', '.html', '.json', '.yaml', '.yml'}

# 每种格式适合转换的目标格式
CONVERSION_MAP = {
    '.md': ['.html', '.docx','.txt'],  # Markdown适合转换为HTML、PDF、纯文本
    '.txt': ['.md', '.html'],  # 纯文本适合转换为Markdown、HTML
    '.docx': ['.pdf', '.html', '.txt', '.md'],  # Word文档适合转换为PDF、HTML、纯文本、Markdown
    '.pdf': ['.txt', '.html','.md'],  # PDF适合转换为纯文本、HTML（提取内容）
    '.html': ['.md', '.docx', '.txt'],  # HTML适合转换为Markdown、docx、纯文本
    '.json': ['.yaml', '.yml', '.txt','.xml','.csv','.html'],  # JSON适合转换为YAML、纯文本、XML、CSV、HTML
    '.yaml': ['.json', '.txt'],  # YAML适合转换为JSON、纯文本
    '.yml': ['.json', '.txt']  # YML适合转换为JSON、纯文本
}


@router.post(
    "/convert",
    summary="文档格式转换",
    description="支持多种文档格式之间的相互转换"
)
async def convert_document(
        background_tasks: BackgroundTasks,
        file: UploadFile = File(..., description="待转换的文档文件"),
        target_format: str = Form(..., description="目标格式，如: docx,pdf, html, txt, md, json, yaml,xml,csv")
):
    """
    文档格式转换接口

    Args:
        background_tasks: FastAPI后台任务
        file: 上传的文档文件
        target_format: 目标格式

    Returns:
        转换后的文件
    """
    logger.info(f"Received conversion request: {file.filename} to {target_format}")

    # 获取文件扩展名
    _, ext = os.path.splitext(file.filename)
    ext = ext.lower()

    # 验证输入格式
    if ext not in SUPPORTED_INPUT_FORMATS:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的输入格式: {ext}。支持的格式: {', '.join(SUPPORTED_INPUT_FORMATS)}"
        )

    target_format = target_format.lower()
    target_ext = f".{target_format}"

    # 验证目标格式
    if target_ext not in CONVERSION_MAP[ext]:
        available_formats = ', '.join([fmt[1:] for fmt in CONVERSION_MAP[ext]])
        raise HTTPException(
            status_code=400,
            detail=f"无法将 {ext} 转换为 {target_format}。支持的目标格式: {available_formats}"
        )

    #使用系统临时目录，避免权限问题
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
        await perform_conversion(input_path, output_path, ext, target_ext)

        # 检查输出文件是否存在
        if not os.path.exists(output_path):
            # 清理临时目录
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to clean up temp directory {temp_dir}: {e}")
            raise HTTPException(status_code=500, detail="转换失败：输出文件未正确生成")

        # 添加后台清理任务，在响应发送完成后清理临时文件
        background_tasks.add_task(cleanup_temp_directory, temp_dir)

        return FileResponse(
            output_path,
            media_type=get_media_type(target_ext),
            filename=output_filename
        )

    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")


async def perform_conversion(input_path: str, output_path: str, source_ext: str, target_ext: str):
    """
    执行具体的文件格式转换

    Args:
        input_path: 输入文件路径
        output_path: 输出文件路径
        source_ext: 源文件扩展名
        target_ext: 目标文件扩展名
    """
    logger.info(f"Performing conversion from {source_ext} to {target_ext}")

    try:
        # 根据源文件和目标文件类型调用相应的转换函数
        if source_ext == '.md':
            if target_ext == '.html':
                md_converter.convert_md_to_html(input_path, output_path)
            elif target_ext == '.txt':
                md_converter.convert_md_to_txt(input_path, output_path)
            elif target_ext == '.docx':
                md_converter.convert_md_to_docx(input_path, output_path)
            # 可以添加更多格式转换

        elif source_ext == '.txt':
            if target_ext == '.md':
                txt_converter.convert_txt_to_md(input_path, output_path)
            elif target_ext == '.html':
                txt_converter.convert_txt_to_html(input_path, output_path)
            # 可以添加更多格式转换

        elif source_ext == '.docx':
            if target_ext == '.txt':
                docx_converter.convert_docx_to_txt(input_path, output_path)
            elif target_ext == '.html':
                docx_converter.convert_docx_to_html(input_path, output_path)
            elif target_ext == '.md':
                docx_converter.convert_docx_to_md(input_path, output_path)
            elif target_ext == '.pdf':
                docx_converter.convert_docx_to_pdf(input_path, output_path)
            # 可以添加更多格式转换

        elif source_ext == '.pdf':
            if target_ext == '.txt':
                pdf_converter.convert_pdf_to_txt(input_path, output_path)
            elif target_ext == '.html':
                pdf_converter.convert_pdf_to_html(input_path, output_path)
            elif target_ext == '.md':
                pdf_converter.convert_pdf_to_md(input_path, output_path)
            # 可以添加更多格式转换

        elif source_ext == '.html':
            if target_ext == '.txt':
                html_converter.convert_html_to_txt(input_path, output_path)
            elif target_ext == '.md':
                html_converter.convert_html_to_md(input_path, output_path)
            elif target_ext == '.docx':
                html_converter.convert_html_to_docx(input_path, output_path)
            # 可以添加更多格式转换

        elif source_ext == '.json':
            if target_ext in ['.yaml', '.yml']:
                json_converter.convert_json_to_yaml(input_path, output_path)
            elif target_ext == '.txt':
                json_converter.convert_json_to_txt(input_path, output_path)
            elif target_ext == '.csv':
                json_converter.convert_json_to_csv(input_path, output_path)
            elif target_ext == '.xml':
                json_converter.convert_json_to_xml(input_path, output_path)
            elif target_ext == '.html':
                json_converter.convert_json_to_html(input_path, output_path)
            # 可以添加更多格式转换

        elif source_ext in ['.yaml', '.yml']:
            if target_ext == '.json':
                yaml_converter.convert_yaml_to_json(input_path, output_path)
            elif target_ext == '.txt':
                yaml_converter.convert_yaml_to_txt(input_path, output_path)
            # 可以添加更多格式转换

        else:
            # 默认处理方式，直接复制文件
            with open(input_path, 'rb') as src, open(output_path, 'wb') as dst:
                dst.write(src.read())

        logger.info(f"Conversion completed: {output_path}")

    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        raise e

def cleanup_temp_directory(temp_dir: str):
    """清理临时目录"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        logger.warning(f"Failed to clean up temp directory {temp_dir}: {e}")

def get_media_type(ext: str) -> str:
    """
    根据文件扩展名获取MIME类型

    Args:
        ext: 文件扩展名

    Returns:
        MIME类型字符串
    """
    media_types = {
        '.pdf': 'application/pdf',
        '.html': 'text/html',
        '.txt': 'text/plain',
        '.md': 'text/markdown',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.json': 'application/json',
        '.yaml': 'application/yaml',
        '.yml': 'application/yaml'
    }
    return media_types.get(ext, 'application/octet-stream')


@router.get(
    "/convert/formats",
    summary="获取支持的转换格式",
    description="返回所有支持的输入格式及其可转换的目标格式"
)
async def get_supported_formats():
    """
    获取支持的转换格式信息

    Returns:
        包含所有支持格式的字典
    """
    format_info = {}
    for source_ext, target_formats in CONVERSION_MAP.items():
        format_info[source_ext] = {
            "description": get_format_description(source_ext),
            "target_formats": [
                {
                    "extension": target_ext,
                    "description": get_format_description(target_ext)
                }
                for target_ext in target_formats
            ]
        }
    return format_info


def get_format_description(ext: str) -> str:
    """
    获取文件格式描述

    Args:
        ext: 文件扩展名

    Returns:
        格式描述字符串
    """
    descriptions = {
        '.md': 'Markdown文档',
        '.txt': '纯文本文件',
        '.docx': 'Word文档',
        '.pdf': 'PDF文档',
        '.html': 'HTML网页',
        '.json': 'JSON数据文件',
        '.yaml': 'YAML配置文件',
        '.yml': 'YAML配置文件'
    }
    return descriptions.get(ext, f'{ext}格式文件')
