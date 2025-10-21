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
from Agents.FileReviewAgents.agentRunF import agent_file_review_run
from Models.FileReviewModels.ApiModels.fileReviewApiModels import FileReviewResult, Example, Config

# 创建日志记录器
logger=logging.getLogger("file_review")

# 创建路由器
router = APIRouter()

def load_file_review_config(agentID:str):
    """加载配置参数，按agentID（例如1或2）加载不同的配置:"""
    config_path=f'./Configs/FileReviewConfig/fileReviewConfig{agentID}.json'
    try:
        logger.info(f"Loading configuration for agent ID: {agentID}")
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
            # 使用模型解析配置
            config_obj = Config(**config_data)
            client = AsyncOpenAI(
                api_key=config_obj.fileReview.apiKey,
                base_url=config_obj.fileReview.baseUrl
            )
            # 解析其他固定参数
            logger.info(f"Configuration loaded successfully for agent ID: {agentID}")
            return {
                "client": client,
                "modelName": config_obj.fileReview.modelName,
                "termBankPath": config_obj.fileReview.termBankPath,
                "fileReviewResultPath": config_obj.fileReview.fileReviewResultPath,
                "formatStandards": {
                    item.styleName: {
                        "fontSize": item.fontSize,
                        "fontColor": item.fontColor,
                        "allowedFonts": item.allowedFonts
                    } for item in config_obj.fileReview.formatStandards
                }
            }
    except FileNotFoundError:
        logger.error(f"Configuration file not found for agent ID: {agentID}")
        raise HTTPException(status_code=404,detail=f"文件ReviewConfig{agentID}.json未找到")





# 初始化函数，在应用启动时调用
# def init_api():
#     global config
#     config = load_file_review_config()

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
        agentID:str=Query(...,description="agentID，1或2，由此加载不同的配置文件参数")
):
    try:
        logger.info(f"Received file review request: {file.filename}, agent ID: {agentID}")
        # 创建临时保存目录
        temp_dir = "./Files/FileReviewUploads"
        os.makedirs(temp_dir, exist_ok=True)
        #加载配置文件
        config=load_file_review_config(agentID)
        # 保存上传文件
        filePath = os.path.join(temp_dir, file.filename)
        with open(filePath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        logger.info(f"Saved file to: {filePath}")
        # 调用原有处理逻辑
        result = await agent_file_review_run(
            filePath=filePath,
            termBankPath=config["termBankPath"],
            fileReviewResultPath=config["fileReviewResultPath"],
            client=config["client"],
            modelName=config["modelName"],
            formatStandards=config["formatStandards"]
        )

        # 删除上传的文件（如果保留就注释掉）
        os.remove(filePath)
        logger.info(f"File review completed for: {file.filename}")

        return result

    except Exception as e:
        logger.error(f"Error during file review: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

