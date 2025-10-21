"""
执行:
     agent_语法审核
     agent_术语审核
     agent_格式审核
"""
import os
import json
import logging
from Agents.FileReviewAgents.文件内容提取 import extract_docx_styles
from Agents.FileReviewAgents.文本切分 import split_into_blocks,split_into_textblocks
from Agents.FileReviewAgents.agent_语法审核 import check_grammarErrors
from Agents.FileReviewAgents.agent_术语审核 import check_termErrors
from Agents.FileReviewAgents.agent_格式审核 import check_formatErrors
from Models.FileReviewModels.ApiModels.fileReviewApiModels import FileReviewResult
from docx import Document
import asyncio
import functools

logger=logging.getLogger("file_review")

async def agent_file_review_run(filePath,termBankPath,fileReviewResultPath,client,modelName,formatStandards):
    logger.info(f"Starting file review process for: {filePath}")
    print("提取文件信息...")
    _, ext = os.path.splitext(filePath)

    # 提取带格式的内容
    if ext == '.docx':
        logger.debug("Processing DOCX file")
        doc=Document(filePath)
        text = '\n'.join([para.text for para in doc.paragraphs])
        styled_content = extract_docx_styles(filePath)
        # 分块处理
        logger.info("Chunk the text...")
        print("正在对文本分块处理...")
        blocks = split_into_blocks(styled_content, 50)
        text_blocks=split_into_textblocks(text,max_length=50)
        logger.info(f"Block finish")
        print("正在执行语法、术语和格式审核...")
        logger.info("Start executing file review...")
        # 语法检查使用异步
        grammar_task = asyncio.create_task(check_grammarErrors(text_blocks, client, modelName))
        # 术语和格式检查保持同步
        term_task = asyncio.get_event_loop().run_in_executor(
            None,
            functools.partial(check_termErrors, text_blocks, termBankPath)
        )
        format_task = asyncio.get_event_loop().run_in_executor(
            None,
            functools.partial(check_formatErrors, blocks, formatStandards)
        )
        #开始执行
        grammarErrors, termErrors, formatErrors = await asyncio.gather(grammar_task, term_task, format_task)

        errors=FileReviewResult(
            grammarErrors=grammarErrors,
            termErrors=termErrors,
            formatErrors=formatErrors
        )
        # 保存结果
        with open(fileReviewResultPath, 'w', encoding='utf-8') as f:
            json.dump(errors.dict(), f, ensure_ascii=False, indent=4)
        print(f"文件审核结果已保存到：{fileReviewResultPath}")
        logger.info(f"File review completed. Results saved to: {fileReviewResultPath}")

        return errors.dict()
    else:
        logger.warning(f"Unsupported file format: {ext}")
        print("文件格式不合要求")
        return "文件格式不合要求"
