from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import tempfile
import os
import asyncio
from pathlib import Path
from datetime import datetime
from io import BytesIO
from urllib.parse import quote_plus

from Models.RarModels.DomainModels.rarDomainModels import RarAnalysisResult
from Agents.RarAgents.文件读写 import read_urs_file, write_excel, export_to_json
from Agents.RarAgents.agent失效事件 import analyze_failure_event
from Agents.RarAgents.agent潜在失效后果 import analyze_potential_failure_consequences
from Agents.RarAgents.agent严重性 import analyze_severity
from Agents.RarAgents.agent可能性 import analyze_probability
from Agents.RarAgents.agent风险等级 import calculate_risk_level
from Agents.RarAgents.agent可检测性 import analyze_detectability
from Agents.RarAgents.agent风险优先级 import calculate_risk_priority
from Agents.RarAgents.agent风险控制措施 import analyze_risk_control_measures
from Configs.RarConfig.rarConfigInit import rar_config

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
            # 读取URS数据
            rar_data_array = read_urs_file(urs_path)

            # 限制处理数量
            if limit > 0 and limit < len(rar_data_array):
                rar_data_array = rar_data_array[:limit]

            # 创建信号量控制并发,因为硅基流动初始等级并发请求API调用时容易超出平台服务频率的问题，控制最大并发量
            semaphore = asyncio.Semaphore(config["concurrency"]["maxConcurrentRequests"])
            print("正在进行RAR风险评估...")
            # 分析每个需求
            for item in rar_data_array:
                await analyze_failure_event(item, semaphore)
                await analyze_potential_failure_consequences(item, semaphore)
                await analyze_severity(item, semaphore)
                await analyze_probability(item, semaphore)
                await calculate_risk_level(item)
                await analyze_detectability(item, semaphore)
                await calculate_risk_priority(item)
                await analyze_risk_control_measures(item, semaphore)

            # # 写入Excel文件
            write_excel(template_path, str(output_excel), rar_data_array)

            # 导出JSON数据
            export_to_json(rar_data_array, str(output_json))

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