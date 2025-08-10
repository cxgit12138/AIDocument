"""
对文件内容的基础语法进行ai审核
"""
from  Models.FileReviewModels.DomainModels.fileReviewDomainModels import GrammarError
import concurrent.futures  # 新增并发库导入
import json

def check_grammarErrors(text_blocks, client, modelName):
    """并发处理语法检查"""
    grammarErrors = []

    def process_block(text_block):
        system_prompt = """
        你是一名文档语法审核助手，用户将给你一些可能含有语法错误的文档，请你按json格式输出:
        1.请你找出里面的错误语句，
        2.说明错误原因，
        3.给出修改后的语句
        4.将有问题的句子分别输出
        5.输出格式为json格式

        EXAMPLE INPUT: 
        你们今天的装扮很好看我觉得。让人感觉很舒服今天的天气。

        EXAMPLE JSON OUTPUT:    
        [    
            {
            "errorStatement":"你们今天的装扮很好看我觉得。",
            "typeOfError":"语序混乱",
            "revised":"我觉得你们今天的装扮很好看。"
            },
            {
            "errorStatement":"让人感觉很舒服今天的天气",
            "typeOfError":"语序混乱",
            "revised":"今天的天气让人感觉很舒服"
            }    
        ]
        """  # 保持原有prompt内容不变

        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": text_block}]
        try:
            response = client.chat.completions.create(
                model=modelName,
                messages=messages,
                response_format={
                    "type": "json_object"
                }
            )
            result = json.loads(response.choices[0].message.content)
            # 转换为GrammarError对象列表
            return [GrammarError(**item) for item in result]
        except Exception as e:
            print(f"处理block时出错: {str(e)}")
            return []

    # 使用线程池并发处理（建议5并发，根据API限流调整）
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_block, text_block) for text_block in text_blocks]

        for future in concurrent.futures.as_completed(futures):
            try:
                result = future.result()
                if isinstance(result, list):
                    grammarErrors.extend(result)
            except Exception as e:
                print(f"处理结果时出错: {str(e)}")

    print(f"语法检查完成，找到 {len(grammarErrors)} 个错误")
    return grammarErrors