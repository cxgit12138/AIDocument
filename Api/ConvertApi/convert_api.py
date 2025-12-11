# file: Api/ConvertApi/convert_api.py
"""
文档格式转换API模块
支持多种文档格式之间的相互转换
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import logging
import shutil
import os

from Agents.FileConvertAgents.convert_run import execute_conversion, get_supported_formats_info

router = APIRouter()
logger = logging.getLogger("convert_api")


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
    try:
        # 执行转换
        result = await execute_conversion(file, target_format)

        # 添加后台清理任务，在响应发送完成后清理临时文件
        background_tasks.add_task(_cleanup_temp_directory, result["temp_dir"])

        return FileResponse(
            result["output_path"],
            media_type=result["media_type"],
            filename=result["output_filename"]
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"转换失败: {str(e)}")


def _cleanup_temp_directory(temp_dir: str):
    """清理临时目录"""
    try:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    except Exception as e:
        logger.warning(f"Failed to clean up temp directory {temp_dir}: {e}")


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
    return get_supported_formats_info()
