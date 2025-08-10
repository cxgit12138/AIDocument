import asyncio
from Agents.RarAgents.client import client, MODEL_NAME
from Models.RarModels.DomainModels.rarDomainModels import RarData


async def analyze_probability(data: RarData, semaphore: asyncio.Semaphore) -> None:
    """
    分析可能性等级

    Args:
        data: RAR数据对象
        semaphore: 并发控制信号量
    """
    system_prompt = """
    【角色设定】
    你是一个质量分析风险评估工具，现在需要针对失效事件，评估风险'可能性等级'。

    【参考资料】
    (低):
    - 通常业务场景下，通过系统功能设计或业务流程管理等措施，几乎不可能发生
    - 系统的标准功能，或通过调整标准配置实现        
    (中):
    - 极端业务场景下，可能会发生
    - 预防控制措施可以起到一定作用，很少发生重复性的错误
    - 在系统的标准功能基础上进行少量的开发        
    (高):
    - 通常业务场景下，可能会发生
    - 不知原因的错误，无法采取有效控制措施
    - 所采取的预防措施效果有限，重复性错误发生可能性高
    - 系统标准功能不能实现，需要再次开发

    【规则】
    1. 根据'失效事件'和'潜在失效后果'，评估事件的发生概率等级；
    2. **仅返回1个字**：高、中、低，禁止任何其他字符或格式；
    3. 思考时可根据以上参考资料，但仅返回一个字：高、中、低，禁止其他字符或格式

    【示例】
    输入：失效事件：当主流浏览器的兼容性问题导致渲染错误时，系统无法正确显示界面
         潜在失效后果：导致界面无法正确显示，影响用户体验。
    输出：中
    """

    user_prompt = f"失效事件：{data.FailureEvent}\n潜在失效后果：{data.PotentialFailureConsequences}"
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
        data.Probability = most_frequent