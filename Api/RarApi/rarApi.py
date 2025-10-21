from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
import asyncio
from pathlib import Path
from datetime import datetime

from Configs.RarConfig.rarConfigInit import rar_config
from Agents.RarAgents.agentRunR import run_rar_analysis

router=APIRouter()

# 初始化配置
def init_rar_config():
    global config
    config = {
        "output_dir": Path(rar_config["output"]["path"]),
        "concurrency": rar_config["concurrency"],
        "template_path": Path("./Files/RarUploads/RAR空白模板.xlsx")
    }
    config["output_dir"].mkdir(parents=True, exist_ok=True)


@router.post(
    "/rar",
    # response_model=RarAnalysisResult,
    summary="RAR需求评估分析",
    description="生成风险分析报告，上传文件:URS需求文件"
)
async def analyze_urs(
        urs_file: UploadFile = File(...,description="URS需求文件，Excel表格"),
        limit: int = Form(5,description="限制处理需求条数，默认5条")  # 默认处理5条数据
):
    """
    上传URS文件和模板文件，生成RAR分析结果

    Args:
        urs_file: URS Excel文件
        template_file: RAR模板Excel文件
        limit: 处理的数据条数限制

    Returns:
        分析结果和输出文件路径
    """
    # 创建临时目录保存上传的文件，处理后自动清理文件
    with tempfile.TemporaryDirectory() as temp_dir:
        # 保存上传的文件
        urs_path = os.path.join(temp_dir, urs_file.filename)

        # 写入上传的文件
        with open(urs_path, "wb") as f:
            f.write(await urs_file.read())

        template_path=config["template_path"]

        # 生成输出文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_excel = config["output_dir"] / f"RAR分析结果_{timestamp}.xlsx"
        output_json= config["output_dir"] / f"RAR分析结果_{timestamp}.json"

        try:
            # 执行RAR分析
            await run_rar_analysis(
                urs_path=urs_path,
                template_path=template_path,
                output_excel=output_excel,
                output_json=output_json,
                limit=limit,
                max_concurrent_requests=config["concurrency"]["maxConcurrentRequests"],
                timeout_seconds=600
            )

            # 构建返回结果
            return FileResponse(
                output_excel,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=f"RAR分析结果_{timestamp}.xlsx"
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@router.get("/health", summary="服务健康检查")
async def health_check():
    return {"status": "ok"}