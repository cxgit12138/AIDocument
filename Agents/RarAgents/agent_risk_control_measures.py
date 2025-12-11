import asyncio
from Agents.RarAgents.client import client, MODEL_NAME
from Models.RarModels.DomainModels.rar_domain_models import RarData


async def analyze_risk_control_measures(data: RarData, semaphore: asyncio.Semaphore) -> None:
    """
    分析风险控制措施

    Args:
        data: RAR数据对象
        semaphore: 并发控制信号量
    """
    system_prompt = """
    【角色设定】
    用户将给你数据，请严格作为风险控制措施生成器，基于以下规则处理输入数据：

    【规则】
    1.输出结构强制遵循：
    在DQ进行设计确认[固定首项]
    [仅当需求含配置要素时]在IQ对配置的{{关键参数}}进行确认
    [仅当需求含功能要素时]在OQ对功能的{{核心功能}}进行确认[风险优先级为中/高时追加""并进行挑战性测试""]
    [仅当需求含业务流程时]在PQ对业务的{{业务环节}}进行确认
    [仅当上述措施未覆盖风险时]SOP规定：<需人工审核补充>

    2.要素提取规则：        
    - {{关键参数}}：从需求中提取不超过3个核心配置参数
    - {{核心功能}}：关联失效事件提炼单一核心功能
    - {{业务环节}}：映射潜在失效后果定位关键业务节点

    3.生成约束条件：
    a) 每类确认项（IQ/OQ/PQ）最多存在1项
    b) 总措施条目不超过4项（含固定DQ项）
    c) 挑战性测试仅附加不单独成项

    4.过滤机制：        
    - 排除硬件故障/人员操作类描述
    - 使用纯文本无符号的连贯句式
    - 自动省略非必要修饰词
    - 处理逻辑：需求分析→要素匹配→条件触发→语句合成

    【输出示例】：
    在DQ进行设计确认，在IQ对配置的[参数A]进行确认，在OQ对功能的[功能B]进行确认并进行挑战性测试，在PQ对业务的[流程C]进行确认
    """

    user_prompt = f"需求：{data.requirement_desc}\n失效事件：{data.failure_event}\n潜在失效后果：{data.potential_failure_consequences}\n严重性：{data.severity}\n可能性：{data.probability}\n风险等级：{data.risk_level}\n可检测性：{data.detectability}\n风险优先级：{data.risk_priority}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # 使用信号量控制并发
    async with semaphore:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages
        )
        data.risk_control_measures = response.choices[0].message.content.strip()