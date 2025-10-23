"""
PDF文件转换代理
处理PDF到其他格式的转换
"""

import PyPDF2
from pdfminer.high_level import extract_text
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import HTMLConverter, TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
import io
from typing import Dict, Any, List
import os


def convert_pdf_to_txt(input_path: str, output_path: str):
    """将PDF转换为纯文本"""
    try:
        # 使用pdfminer提取文本（首选方法）
        text = extract_text(input_path)

        # 清理文本内容
        lines = [line.strip() for line in text.splitlines()]
        cleaned_text = '\n'.join(line for line in lines if line)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

    except Exception as e:
        # 备用方法：使用PyPDF2
        try:
            with open(input_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"

            # 清理文本内容
            lines = [line.strip() for line in text.splitlines()]
            cleaned_text = '\n'.join(line for line in lines if line)

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_text)
        except Exception as e2:
            raise Exception(f"PDF文本提取失败: {str(e2)}")


def convert_pdf_to_html(input_path: str, output_path: str):
    """将PDF转换为HTML"""
    try:
        # 使用pdfminer将PDF转换为HTML
        rsrcmgr = PDFResourceManager()
        retstr = io.StringIO()
        laparams = LAParams()
        device = HTMLConverter(rsrcmgr, retstr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        with open(input_path, 'rb') as fp:
            pages = PDFPage.get_pages(fp)
            for page in pages:
                interpreter.process_page(page)
            html_content = retstr.getvalue()

        device.close()
        retstr.close()

        # 添加基本的HTML结构和样式
        full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Converted PDF Document</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .page {{ margin-bottom: 30px; }}
        .text {{ line-height: 1.5; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_html)

    except Exception as e:
        # 备用方法：提取文本并包装为HTML
        try:
            text = extract_text(input_path)
            lines = [line.strip() for line in text.splitlines()]
            cleaned_text = '\n'.join(line for line in lines if line)

            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Converted PDF Document</title>
</head>
<body>
<pre>{cleaned_text}</pre>
</body>
</html>"""

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        except Exception as e2:
            raise Exception(f"PDF转换为HTML失败: {str(e2)}")


def convert_pdf_to_md(input_path: str, output_path: str):
    """将PDF转换为Markdown"""
    try:
        # 提取文本
        text = extract_text(input_path)

        # 简单处理文本结构
        lines = [line.strip() for line in text.splitlines()]
        cleaned_lines = [line for line in lines if line]

        # 尝试识别标题（通过字体大小等方式，这里简化处理）
        md_content = ""
        for line in cleaned_lines:
            # 如果行较长且以大写字母开头，可能是标题
            if len(line) > 5 and len(line) < 100 and line.isupper():
                md_content += f"\n# {line}\n\n"
            else:
                md_content += f"{line}\n"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

    except Exception as e:
        raise Exception(f"PDF转换为Markdown失败: {str(e)}")


def extract_pdf_metadata(input_path: str) -> Dict[str, Any]:
    """提取PDF文档元数据"""
    try:
        with open(input_path, 'rb') as file:
            parser = PDFParser(file)
            document = PDFDocument(parser)

            # 获取文档信息
            metadata = {}
            if 'Info' in document.catalog:
                info = document.catalog['Info']
                if hasattr(info, 'attrs'):
                    for key, value in info.attrs.items():
                        if hasattr(value, 'decode'):
                            try:
                                metadata[key[1:]] = value.decode('utf-8')
                            except:
                                metadata[key[1:]] = str(value)
                        else:
                            metadata[key[1:]] = str(value)

            # 获取页面数量
            try:
                reader = PyPDF2.PdfReader(file)
                metadata['page_count'] = len(reader.pages)
            except:
                metadata['page_count'] = 0

            return metadata

    except Exception as e:
        raise Exception(f"提取PDF元数据失败: {str(e)}")


def get_pdf_info(input_path: str) -> Dict[str, Any]:
    """获取PDF文档基本信息"""
    try:
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            info = {
                "page_count": len(reader.pages),
                "file_size": os.path.getsize(input_path)
            }

            # 获取文档信息
            doc_info = reader.metadata
            if doc_info:
                def get_info_value(key):
                    value = doc_info.get(key)
                    return str(value) if value is not None else ""

                info["title"] = get_info_value("/Title")
                info["author"] = get_info_value("/Author")
                info["subject"] = get_info_value("/Subject")
                info["creator"] = get_info_value("/Creator")
                info["producer"] = get_info_value("/Producer")
                info["creation_date"] = get_info_value("/CreationDate")
                info["modification_date"] = get_info_value("/ModDate")

            return info

    except Exception as e:
        raise Exception(f"获取PDF信息失败: {str(e)}")


def extract_pdf_pages(input_path: str, output_path: str, page_numbers: List[int]):
    """提取PDF指定页面"""
    try:
        with open(input_path, 'rb') as input_file:
            reader = PyPDF2.PdfReader(input_file)
            writer = PyPDF2.PdfWriter()

            # 添加指定页面
            for page_num in page_numbers:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
                else:
                    raise Exception(f"页面 {page_num} 不存在")

            # 写入输出文件
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)

    except Exception as e:
        raise Exception(f"提取PDF页面失败: {str(e)}")