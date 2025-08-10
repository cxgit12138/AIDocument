"""
文件下载API路由模块
"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os

router = APIRouter()


@router.get(
    "/download/urstemplate",
    summary="urs模板文件下载接口",
    description="下载urs模板文件",
    responses={
        200: {
            "content": {"application/octet-stream": {}},
            "description": "文件流响应"
        }
    }
)
async def download_file():
    try:
        # TODO: 根据实际业务需求修改文件路径逻辑
        file_path = f"./Files/RarUploads/urstemplate.xlsx"

        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件未找到")

        return FileResponse(
            path=file_path,
            filename=os.path.basename(file_path),
            media_type="application/octet-stream"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
