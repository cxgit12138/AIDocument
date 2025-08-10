"""
文件审核助手的数据模型定义
包含所有与文件审核相关的数据结构和类
"""

from pydantic import BaseModel,Field
from typing import List, Tuple, Union, Optional

# 术语库相关模型
class TermEntry(BaseModel):
    """术语库中的单个术语条目"""
    correctTerm: str
    errorTerm: List[str]

class TermBank(BaseModel):
    """术语库模型"""
    termBank: List[TermEntry]


# 格式标准相关模型
class FormatStandard(BaseModel):
    """格式标准条目"""
    standardName: str
    styleName: str
    fontSize: float
    fontColor: str
    allowedFonts: Union[str, List[str]]


class FileReviewConfig(BaseModel):
    apiKey: str
    baseUrl: str
    modelName: str
    termBankPath: str
    fileReviewResultPath: str
    formatStandards: List[FormatStandard]

# 文本样式相关模型
class TextStyle(BaseModel):
    """文本样式信息"""
    text: str
    fontSize: Optional[float] = None
    fontColor: Optional[Tuple[int, int, int]] = None
    fontName: Optional[str] = None
    styleName: Optional[str] = None
    headingLevel: Optional[int] = None

class StyledBlock(BaseModel):
    """带样式的文本块"""
    text: str
    styles: List[TextStyle]

class GrammarError(BaseModel):
    """语法错误"""
    errorStatement: str=Field(description="语法错误语句")
    typeOfError: str=Field(description="语法错误类型")
    revised: str=Field(description="语法修正后的语句")

class TermError(BaseModel):
    """术语错误"""
    errorStatement: str=Field(description="术语错误语句")
    typeOfError: str=Field(description="术语错误类型")
    errorWord: str=Field(description="术语错误词")
    revised: str=Field(description="术语修正后的语句")

class FormatError(BaseModel):
    """格式错误"""
    typeOfError: str=Field(description="格式错误类型")
    currentValue: str=Field(description="当前错误格式")
    expectedValue: str=Field(description="规定正确格式")
    textSnippet: str=Field(description="格式错误片段")




