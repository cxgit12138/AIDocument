import asyncio
from Agents.RarAgents.client import client, MODEL_NAME
from Models.RarModels.DomainModels.rar_domain_models import RarData


async def analyze_failure_event(data: RarData, semaphore: asyncio.Semaphore) -> None:
    """
    分析失效事件

    Args:
        data: RAR数据对象
        semaphore: 并发控制信号量
    """
    system_prompt = """
    【角色设定】
    你是一名软件质量风险评估专员，需严格按以下规则生成失效事件假设。

    【定义与规则】
    - **失效事件定义**：对需求的失败性假设，描述**系统在运行中因与需求功能直接相关的事件触发导致不满足需求**的场景。
    - **规则**：
      1. 从需求中提取核心功能点，反推其失效可能性（例：需求要求'实时生成报告' → 失效事件为'报表引擎计算超时'）；
      2. 使用'当...时，系统无法/未能...'句式（禁止使用'如果''假设'等虚拟词）；
      3. 输出**纯文本**，禁止添加'失效事件：'等前缀或符号；
      4. 触发条件必须与需求功能存在直接因果关系，禁止隐性关联（如需求含'数据加密'→禁止用'服务器宕机'等无关因素）。
      (输出规则)
        1. 严格基于需求的核心功能点
        2. 触发条件必须与需求形成显性逻辑链
        3. 长度限制：不超过30字
      (禁用内容)
      - 硬件问题（网络中断、设备故障等）
      - 与需求无直接关联的间接因素（如'员工操作失误'）
      - 详细过程描述（如'因代码BUG引发XX模块崩溃'）
      - 主观推测（如'可能'、'或许'）
      - 授权认证方式（如'未登录'、'权限不足'、'授权检查模块'）
      - 软件安装问题 （软件版本、软件安装困难等）

    【示例】
    输入：用户提交订单后需在5秒内收到支付结果
    输出：当支付结果状态轮询线程阻塞时，系统未能更新交易状态

    输入：API必须验证用户权限后才返回敏感数据
    输出：当RBAC策略缓存失效时，系统错误返回未授权信息
    """

    user_prompt = data.requirement_desc
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
        data.failure_event = response.choices[0].message.content.strip()