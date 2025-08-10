"""
执行:
     agent_语法审核
     agent_术语审核
     agent_格式审核
"""
import os
import json
from Agents.FileReviewAgents.文件内容提取 import extract_docx_styles
from Agents.FileReviewAgents.文本切分 import split_into_blocks,split_into_textblocks
from Agents.FileReviewAgents.agent_语法审核 import check_grammarErrors
from Agents.FileReviewAgents.agent_术语审核 import check_termErrors
from Agents.FileReviewAgents.agent_格式审核 import check_formatErrors
from Models.FileReviewModels.ApiModels.fileReviewApiModels import FileReviewResult
from docx import Document



def agent_file_review_run(filePath,termBankPath,fileReviewResultPath,client,modelName,formatStandards):
    print("提取文件信息...")
    _, ext = os.path.splitext(filePath)

    # 提取带格式的内容
    if ext == '.docx':
        doc=Document(filePath)
        text = '\n'.join([para.text for para in doc.paragraphs])
        styled_content = extract_docx_styles(filePath)
        # 分块处理
        print("正在对文本分块处理...")
        blocks = split_into_blocks(styled_content, 50)
        text_blocks=split_into_textblocks(text,max_length=50)
        # 语法审核
        print("正在对文本进行语法审核...")
        grammarErrors = check_grammarErrors(text_blocks,client,modelName)
        # 术语审核
        print("正在对文本进行术语审核...")
        termErrors = check_termErrors(text_blocks,termBankPath)
        # 格式检查
        print("正在对文本进行格式审核...")
        formatErrors = check_formatErrors(blocks,formatStandards)

        errors=FileReviewResult(
            grammarErrors=grammarErrors,
            termErrors=termErrors,
            formatErrors=formatErrors
        )
        # 保存结果
        with open(fileReviewResultPath, 'w', encoding='utf-8') as f:
            json.dump(errors.dict(), f, ensure_ascii=False, indent=4)
        print(f"文件审核结果已保存到：{fileReviewResultPath}")

        return errors.dict()
    else:
        print("文件格式不合要求")
        return "文件格式不合要求"
