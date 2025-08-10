import asyncio
from Agents.RarAgents.client import client, MODEL_NAME
from Models.RarModels.DomainModels.rarDomainModels import RarData


async def analyze_potential_failure_consequences(data: RarData, semaphore: asyncio.Semaphore) -> None:
    """
    分析潜在失效后果

    Args:
        data: RAR数据对象
        semaphore: 并发控制信号量
    """
    system_prompt = """
    【角色设定】
    你是一名专业的软件风险分析专员，根据"失效事件"和"需求"总结假设性后果。        

    【定义与规则】
    - **潜在失效后果定义**：失效事件发生后可能导致的**业务、法规、流程**影响。
    - **必须遵守**（违反将导致输出无效）：
      1. **核心任务**：仅根据"失效事件"和"需求"总结假设性后果，禁止虚构或扩展；
      2. **输出格式**：直接返回纯文本内容，禁止添加"潜在失效后果："等前缀或符号；
      3. **禁用内容**：硬件问题（如网络中断）、详细失效过程、主观推测。
      4. **字数限制**：总结内容不超过30字，需包含"导致"和明确结果（如"导致X，引发Y"）。
      5. 禁止引用需求原文，需转化为后果描述。
      6. 从以下3个方向**选择最相关的一个**总结：
        ① 影响业务执行（如数据错误、功能缺失）
        ② 违反法规要求（如隐私泄露、审计不通过）
        ③ 中断业务流程（如订单卡顿、服务不可用）

    【示例】
    输入：需求：用户支付后需实时生成电子发票
         失效事件：支付成功但发票生成服务异常
    输出：导致发票无法同步生成，违反税务合规要求

    输入：需求：后台需每日自动备份客户数据
         失效事件：备份脚本执行失败且未被监控发现
    输出：导致历史数据丢失，影响业务连续性
    """

    user_prompt = f"需求：{data.RequirementDesc}\n失效事件：{data.FailureEvent}"
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
        data.PotentialFailureConsequences = response.choices[0].message.content.strip()