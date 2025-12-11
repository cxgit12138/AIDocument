"""
每个元素以run为单位(格式相同的文本为一个run),提取带格式(标题级别、字体、字体大小、字体颜色)的文本内容
"""

import os
import aspose.words as aw
from aspose.words import NodeType

def extract_docx_styles(file_review_result_path):
    raw_styled_paragraphs = []
    para_count = 0
    run_total = 0

    # 验证文件路径
    abs_path = os.path.abspath(file_review_result_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"文件不存在: {abs_path}")

    # 打开文档
    doc = aw.Document(abs_path)
    print(f"已成功打开文档: {abs_path}")

    try:
        # 获取所有段落
        paragraphs = [node.as_paragraph() for node in doc.get_child_nodes(NodeType.PARAGRAPH, True)] #type: ignore
        print(f"总段落数: {len(paragraphs)}")

        # 遍历段落
        for para_idx, para in enumerate(paragraphs, 1):
            para_count += 1
            para_text = para.get_text().strip()
            # print(f"\n段落 {para_idx} 内容: '{para_text}'")

            # 段落样式和标题级别
            style_name = para.paragraph_format.style.name
            heading_level = None

            # ... 其余代码保持不变 ...

            if style_name.startswith("标题") or style_name.startswith("Heading"):
                try:
                    if style_name.startswith("标题"):
                        level_str = style_name.replace("标题", "").strip()
                    else:  # "Heading"
                        level_str = style_name.replace("Heading", "").strip()
                    if level_str.isdigit():
                        heading_level = int(level_str)
                except ValueError:
                    heading_level = None

            # 处理段落级别的字体信息
            para_font_name = None
            para_font_size = None
            para_font_color = (0, 0, 0)  # 默认黑色

            runs = []

            # 收集段落级数据（仅当段落文本非空时）
            if para_text:
                # 遍历段落内的Runs
                runs = para.get_child_nodes(NodeType.RUN, False) #type: ignore

                # 如果段落有runs，使用第一个run的字体信息作为段落字体信息
                if runs.count > 0:
                    first_run = runs[0].as_run()
                    para_font_name = first_run.font.name
                    para_font_size = first_run.font.size

                    # 获取颜色
                    if first_run.font.color.to_argb() != 0:
                        argb = first_run.font.color.to_argb()
                        # ARGB格式转换为RGB (跳过Alpha通道)
                        r = (argb >> 16) & 0xFF
                        g = (argb >> 8) & 0xFF
                        b = argb & 0xFF
                        para_font_color = (r, g, b)

                # raw_styled_paragraphs.append({
                #     "text": para_text,
                #     "font_size": para_font_size,
                #     "font_color": para_font_color,
                #     "font_name": para_font_name,
                #     "style_name": style_name,
                #     "heading_level": heading_level
                # })
                run_total += 1

            # 遍历段落内的Runs
            for run_idx, run_node in enumerate(runs, 1):
                run = run_node.as_run()
                text = run.get_text().strip()
                if not text:
                    continue

                run_total += 1
                # print(f"Run {run_idx} 内容: '{text}'")

                # 获取Run的字体属性
                font_name = run.font.name
                font_size = run.font.size

                # 获取颜色
                font_color = (0, 0, 0)  # 默认黑色
                if run.font.color.to_argb() != 0:
                    argb = run.font.color.to_argb()
                    # ARGB格式转换为RGB (跳过Alpha通道)
                    r = (argb >> 16) & 0xFF
                    g = (argb >> 8) & 0xFF
                    b = argb & 0xFF
                    font_color = (r, g, b)

                # 收集Run数据
                raw_styled_paragraphs.append({
                    "text": text,
                    "font_size": font_size,
                    "font_color": font_color,
                    "font_name": font_name,
                    "style_name": style_name,
                    "heading_level": heading_level
                })

        print(f"\n处理完成，共扫描 {para_count} 段落，{run_total} Runs")

        styled_paragraphs = raw_styled_paragraphs[3:-2]
        return styled_paragraphs

    except Exception as e:
        print(f"全局错误: {str(e)}")
        return []
    finally:
        # 释放资源
        if 'doc' in locals():
            del doc