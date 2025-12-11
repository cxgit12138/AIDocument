"""
API路由定义模块
包含所有API端点和处理逻辑
"""

import os
import shutil
import json
import logging
from openai import AsyncOpenAI
from fastapi import APIRouter, HTTPException, UploadFile, File,Query
from Agents.FileReviewAgents.agent_run_f import agent_file_review_run
from Models.FileReviewModels.ApiModels.file_review_api_models import FileReviewResult, Example, Config

# 创建日志记录器
logger = logging.getLogger("file_review")

# 创建路由器
router = APIRouter()

def load_file_review_config(agent_id:str):
    """加载配置参数，按agent_id（例如1或2）加载不同的配置:"""
    config_path = f'./Configs/FileReviewConfig/fileReviewConfig{agent_id}.json'
    try:
        logger.info(f"Loading configuration for agent ID: {agent_id}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            # 使用模型解析配置
            config_obj = Config(**config_data)
            client = AsyncOpenAI(
                api_key=config_obj.file_review.api_key,
                base_url=config_obj.file_review.base_url
            )
            # 解析其他固定参数
            logger.info(f"Configuration loaded successfully for agent ID: {agent_id}")
            return {
                "client": client,
                "model_name": config_obj.file_review.model_name,
                "term_bank_path": config_obj.file_review.term_bank_path,
                "file_review_result_path": config_obj.file_review.file_review_result_path,
                "format_standards": {
                    item.style_name: {
                        "font_size": item.font_size,
                        "font_color": item.font_color,
                        "allowed_fonts": item.allowed_fonts
                    } for item in config_obj.file_review.format_standards
                }
            }
    except FileNotFoundError:
        logger.error(f"Configuration file not found for agent ID: {agent_id}")
        raise HTTPException(status_code=404,detail=f"文件ReviewConfig{agent_id}.json未找到")


@router.post(
    "/filereview",
    summary="文件审核助手",
    description="上传文件进行语法、术语、格式审核",
    status_code=200,
    response_model=FileReviewResult,
    responses={
        200: {
            "model": FileReviewResult,
            "description": "文件审核结果字段说明",
             "content": {
                "application/json": {
                    "example": Example.json_schema_extra["example"]
                }
             }
        }
    }
)
async def review_file(
        file: UploadFile = File(..., description="上传待审核的文件，仅支持docx格式"),
        agent_id:str=Query(...,description="agent_id，1或2，由此加载不同的配置文件参数")
):
    try:
        logger.info(f"Received file review request: {file.filename}, agent ID: {agent_id}")
        # 创建临时保存目录
        temp_dir = "./Files/FileReviewUploads"
        os.makedirs(temp_dir, exist_ok=True)
        #加载配置文件
        config=load_file_review_config(agent_id)
        # 保存上传文件
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)  # type: ignore

        logger.info(f"Saved file to: {file_path}")
        # 调用原有处理逻辑
        result = await agent_file_review_run(
            file_path=file_path,
            term_bank_path=config["term_bank_path"],
            file_review_result_path=config["file_review_result_path"],
            client=config["client"],
            model_name=config["model_name"],
            format_standards=config["format_standards"]
        )

        # 删除上传的文件（如果保留就注释掉）
        os.remove(file_path)
        logger.info(f"File review completed for: {file.filename}")

        return result

    except Exception as e:
        logger.error(f"Error during file review: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

