# Agents/RarAgents/agent_run.py
"""
RAR分析主流程控制模块
负责协调各个分析Agent的执行流程
"""

import asyncio
import logging
from typing import List
from pathlib import Path

from Models.RarModels.DomainModels.rarDomainModels import RarData
from Agents.RarAgents.文件读写 import read_urs_file, write_excel, export_to_json
from Agents.RarAgents.agent失效事件 import analyze_failure_event
from Agents.RarAgents.agent潜在失效后果 import analyze_potential_failure_consequences
from Agents.RarAgents.agent严重性 import analyze_severity
from Agents.RarAgents.agent可能性 import analyze_probability
from Agents.RarAgents.agent风险等级 import calculate_risk_level
from Agents.RarAgents.agent可检测性 import analyze_detectability
from Agents.RarAgents.agent风险优先级 import calculate_risk_priority
from Agents.RarAgents.agent风险控制措施 import analyze_risk_control_measures




async def process_single_item(item: RarData, semaphore: asyncio.Semaphore) -> RarData:
    """
    处理单个RAR数据项

    Args:
        item: RAR数据项
        semaphore: 并发控制信号量

    Returns:
        处理后的RAR数据项
    """
    try:
        await analyze_failure_event(item, semaphore)
        await analyze_potential_failure_consequences(item, semaphore)
        await analyze_severity(item, semaphore)
        await analyze_probability(item, semaphore)
        await calculate_risk_level(item)
        await analyze_detectability(item, semaphore)
        await calculate_risk_priority(item)
        await analyze_risk_control_measures(item, semaphore)
        return item
    except Exception as e:
        raise


async def run_rar_analysis(
        urs_path: str,
        template_path: Path,
        output_excel: Path,
        output_json: Path,
        limit: int = 0,
        max_concurrent_requests: int = 5,
        timeout_seconds: int = 600
) -> None:
    """
    执行RAR分析主流程

    Args:
        urs_path: URS文件路径
        template_path: 模板文件路径
        output_excel: Excel输出文件路径
        output_json: JSON输出文件路径
        limit: 处理的数据条数限制，0表示不限制
        max_concurrent_requests: 最大并发请求数
        timeout_seconds: 处理超时时间（秒）
    """
    try:
        # 读取URS数据
        rar_data_array = read_urs_file(urs_path)

        # 限制处理数量
        if limit > 0 and limit < len(rar_data_array):
            rar_data_array = rar_data_array[:limit]

        # 创建信号量控制并发
        semaphore = asyncio.Semaphore(max_concurrent_requests)

        # 并发处理所有需求项
        tasks = []
        for item in rar_data_array:
            task = asyncio.create_task(process_single_item(item, semaphore))
            tasks.append(task)

        # 设置超时时间，避免长时间等待
        processed_items = await asyncio.wait_for(asyncio.gather(*tasks), timeout=timeout_seconds)

        # 写入Excel文件
        write_excel(template_path, str(output_excel), processed_items)

        # 导出JSON数据
        export_to_json(processed_items, str(output_json))

    except asyncio.TimeoutError:
        raise TimeoutError("处理超时，请减少处理条数或稍后重试")
    except Exception as e:
        raise
