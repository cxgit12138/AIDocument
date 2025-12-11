"""
执行:
     agent_语法审核
     agent_术语审核
     agent_格式审核
"""
import os
import json
import logging
from Agents.FileReviewAgents.content_extraction import extract_docx_styles
from Agents.FileReviewAgents.text_segmentation import split_into_blocks,split_into_textblocks
from Agents.FileReviewAgents.agent_syntax import check_grammar_errors
from Agents.FileReviewAgents.agent_terminology import check_term_errors
from Agents.FileReviewAgents.agent_format import check_format_errors
from Models.FileReviewModels.ApiModels.file_review_api_models import FileReviewResult
from docx import Document
import asyncio
import functools

logger = logging.getLogger("file_review")

async def agent_file_review_run(file_path,term_bank_path,file_review_result_path,client,model_name,format_standards):
    logger.info(f"Starting file review process for: {file_path}")
    print("提取文件信息...")
    _, ext = os.path.splitext(file_path)

    # 提取带格式的内容
    if ext == '.docx':
        logger.debug("Processing DOCX file")
        doc=Document(file_path)
        text = '\n'.join([para.text for para in doc.paragraphs])
        styled_content = extract_docx_styles(file_path)
        # 分块处理
        logger.info("Chunk the text...")
        print("正在对文本分块处理...")
        blocks = split_into_blocks(styled_content, 50)
        text_blocks=split_into_textblocks(text,max_length=50)
        logger.info(f"Block finish")
        print("正在执行语法、术语和格式审核...")
        logger.info("Start executing file review...")
        # 语法检查使用异步
        grammar_task = asyncio.create_task(check_grammar_errors(text_blocks, client, model_name))
        # 术语和格式检查保持同步
        term_task = asyncio.get_event_loop().run_in_executor(
            None,
            functools.partial(check_term_errors, text_blocks, term_bank_path)
        )
        format_task = asyncio.get_event_loop().run_in_executor(
            None,
            functools.partial(check_format_errors, blocks, format_standards)
        )
        #开始执行
        grammar_errors, term_errors, format_errors = await asyncio.gather(grammar_task, term_task, format_task)

        errors = FileReviewResult(
            grammar_errors=grammar_errors,
            term_errors=term_errors,
            format_errors=format_errors
        )
        # 保存结果
        with open(file_review_result_path, 'w', encoding='utf-8') as f:
            json.dump(errors.model_dump(), f, ensure_ascii=False, indent=4)
        print(f"文件审核结果已保存到：{file_review_result_path}")
        logger.info(f"File review completed. Results saved to: {file_review_result_path}")

        return errors.model_dump()
    else:
        logger.warning(f"Unsupported file format: {ext}")
        print("文件格式不合要求")
        return "文件格式不合要求"
