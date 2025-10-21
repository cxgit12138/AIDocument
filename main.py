"""
项目主函数，负责初始化FastAPI应用和启动服务器
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from Api.FileReviewApi.fileReviewApi import router as file_review_router
from Api.RarApi.rarApi import router as rar_router,init_rar_config
from Api.RarApi.文件下载api import router as download_router
import uvicorn
import logging
from Configs.logging_config import setup_logging

logger=setup_logging()



@asynccontextmanager
async def lifespan(app: FastAPI):
    # 服务启动时初始化配置
    logger.info("Initializing application...")
    init_rar_config() # 初始化RarApi的配置
    logger.info("Application initialized successfully")
    yield
    # 此处可添加服务关闭时的清理逻辑（如有需要）
    logger.info("Application shutting down...")

def create_app():
    # 创建FastAPI应用实例
    app = FastAPI(
        title="AI小助手",
        description="提供文件审核、风险评估等功能的API接口",
        version="1.0.0",
        lifespan=lifespan
    )

    # 配置CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )


    # 包含路由
    # 将文件审核路由挂载到/api/fileReview路径
    app.include_router(file_review_router, prefix="/api")

    # 将风险评估路由挂载到/api/rar路径
    app.include_router(rar_router, prefix="/api")

    # 将下载路由挂载到/api/download/urstemplate路径
    app.include_router(download_router, prefix="/api")

    logger.info("Routes registered successfully")
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7001)