"""
对文件内容的用词术语准确度，和术语库进行比对审核
"""
from Models.FileReviewModels.DomainModels.fileReviewDomainModels import TermBank,TermError
import concurrent.futures  # 新增并发库导入
import json
import re


def load_terminology(termBankPath):
    """加载新格式术语库"""
    try:
        with open(termBankPath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # 使用模型解析数据
            term_bank = TermBank(**data)
            return term_bank.termBank
    except Exception as e:
        print(f"术语库加载失败: {str(e)}")
        return []


def check_termErrors(text_blocks, termBankPath):
    termErrors = []
    terminology_db = load_terminology(termBankPath)  # 现在获取的是termBank数组

    # 构建反向映射词典（错误形式 -> 正确术语）
    reverse_terminology = {}
    correct_terms = []  # 存储所有正确术语用于后续检查
    for term_entry in terminology_db:
        correct_term = term_entry.correctTerm
        correct_terms.append(correct_term)
        for variant in term_entry.errorTerm:
            reverse_terminology[variant.lower()] = correct_term

    # 构建正则表达式匹配模式
    terms_to_match = []
    for term_entry in terminology_db:
        terms_to_match.append(term_entry.correctTerm)
        terms_to_match.extend(term_entry.errorTerm)

    pattern_str = '|'.join(r'{}'.format(re.escape(term)) for term in terms_to_match)
    pattern = re.compile(pattern_str, flags=re.IGNORECASE)

    # 后续process_block函数修改部分
    def process_block(text_block):
        block_errors = []
        text_block = text_block.strip()
        matches = list(pattern.finditer(text_block))

        for match in matches:
            matched_term = match.group()
            matched_lower = matched_term.lower()

            # 检查是否是正确术语本身
            if matched_lower in [term.lower() for term in correct_terms]:
                # 查找对应的正确术语
                for correct_term in correct_terms:
                    if correct_term.lower() == matched_lower and correct_term != matched_term:
                        block_errors.append(TermError(
                            errorStatement=text_block,
                            typeOfError="术语大小写不规范",
                            errorWord=matched_term,
                            revised=correct_term
                        ))
                continue

            # 检查是否是错误变体
            if matched_lower in reverse_terminology:
                correct_term = reverse_terminology[matched_lower]
                block_errors.append(TermError(
                    errorStatement=text_block,
                    typeOfError="术语不规范",
                    errorWord=matched_term,
                    revised=correct_term
                ))

        return block_errors

    # 使用线程池并发处理
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_block, text_block) for text_block in text_blocks]
        for future in concurrent.futures.as_completed(futures):
            block_errors = future.result()
            if block_errors:
                print(f"添加错误: {block_errors}")
            termErrors.extend(block_errors)

    print(f"术语检查完成，找到 {len(termErrors)} 个错误")
    return termErrors