import asyncio
from Agents.RarAgents.client import client, MODEL_NAME
from Models.RarModels.DomainModels.rarDomainModels import RarData


async def analyze_detectability(data: RarData, semaphore: asyncio.Semaphore) -> None:
    """
    分析可检测性等级

    Args:
        data: RAR数据对象
        semaphore: 并发控制信号量
    """
    system_prompt = """
    【角色设定】
    你是一个质量分析风险评估工具，现在需要针对失效事件，评估风险'可检测性等级'。

    【参考资料】
    (低):
    - 有检测方法，但可能偶尔能检测到错误通常常规的设计审核，测试与验证很难直接检测，没有其他有效的检测方法来发现错误        
    (中):
    - 发生错误后，后续流程中可以检测出和报告这个错误
    - 如果出错，有系统报警或可通过人工检查能直观发现错误，但不能在当前步骤中检测出错误，通过设计审核，测试与验证等方法可以检测        
    (高):
    - 如果出错，后续流程步骤无法被执行
    - 如果出错，有系统报警或可通过人工检查能直观发现错误，且能在当前步骤中，能检测出错误
    - 通过常规的设计审核，测试与验证等方法很容易被检测     

    【规则】
    1. 根据'失效事件'、'潜在失效后果'，评估失效事件的可被检测的概率等级。
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
        data.Detectability = most_frequent