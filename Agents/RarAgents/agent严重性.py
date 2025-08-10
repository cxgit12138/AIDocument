import asyncio
from Agents.RarAgents.client import client, MODEL_NAME
from Models.RarModels.DomainModels.rarDomainModels import RarData


async def analyze_severity(data: RarData, semaphore: asyncio.Semaphore) -> None:
    """
    分析严重性等级

    Args:
        data: RAR数据对象
        semaphore: 并发控制信号量
    """
    system_prompt = """
    【角色设定】
    你是一个质量分析风险评估工具，现在需要针对潜在失效后果，评估风险'严重性等级'。

    【参考资料】
    (低):
    - 系统使用受限（如操作不便）但通过系统处理的业务流程未中断
    - 不影响系统安全
    - 不影响产品质量、数据完整性及法规符合性        
    (中):
    - 通过系统处理的业务流程中断，该中断可以通过技术在短时间进行修复
    - 安全受限，但未经授权的人无法进行非法修改
    - 可能导致流程数据无法处理，需要再次执行才可进行处理
    - 不影响产品质量、数据完整性及法规符合性        
    (高):
    - 通过系统处理的业务流程中断，但是该中断可能因为技术问题不便解决，或无解决方案
    - 预期已产生的业务数据丢失或被修改
    - 安全受限，可能有不授权的修改
    - 影响产品质量、数据完整性及法规符合性

    【规则】
    1. **仅返回1个字**：高、中、低，禁止任何其他字符或格式；
    2. **禁用内容**：网络中断、电脑崩溃等硬件问题；
    3. 根据'潜在失效后果'的描述，评定影响等级；
    4. 思考时可根据以上参考资料，但仅返回一个字：高、中、低，禁止其他字符或格式

    【示例】
    输入：潜在失效后果：某设备电路短路且无备用电源
    输出：低
    """

    user_prompt = f"潜在失效后果：{data.PotentialFailureConsequences}"
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

        # 过滤输出内容
        s = response.choices[0].message.content.strip()
        levels = {'高', '中', '低'}
        count = {level: 0 for level in levels}

        for char in s:
            if char in levels:
                count[char] += 1

        # 找出出现次数最多的字符
        most_frequent = max(count.items(), key=lambda x: x[1])[0]
        data.Severity = most_frequent