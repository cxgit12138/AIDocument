"""
文件审核助手的数据模型定义
包含所有与文件审核相关的数据结构和类
"""

from pydantic import BaseModel,Field
from typing import List, Tuple, Union, Optional

# 术语库相关模型
class TermEntry(BaseModel):
    """术语库中的单个术语条目"""
    correct_term: str = Field(alias='correctTerm')
    error_term: List[str] = Field(alias='errorTerm')
    
    class Config:
        populate_by_name = True


class TermBank(BaseModel):
    """术语库模型"""
    term_bank: List[TermEntry] = Field(alias='termBank')
    
    class Config:
        populate_by_name = True


# 格式标准相关模型
class FormatStandard(BaseModel):
    """格式标准条目"""
    standard_name: str = Field(alias='standardName')
    style_name: str = Field(alias='styleName')
    font_size: float = Field(alias='fontSize')
    font_color: str = Field(alias='fontColor')
    allowed_fonts: Union[str, List[str]] = Field(alias='allowedFonts')
    
    class Config:
        populate_by_name = True


class FileReviewConfig(BaseModel):
    api_key: str = Field(alias='apiKey')
    base_url: str = Field(alias='baseUrl')
    model_name: str = Field(alias='modelName')
    term_bank_path: str = Field(alias='termBankPath')
    file_review_result_path: str = Field(alias='fileReviewResultPath')
    format_standards: List[FormatStandard] = Field(alias='formatStandards')
    
    class Config:
        populate_by_name = True

# 文本样式相关模型
class TextStyle(BaseModel):
    """文本样式信息"""
    text: str
    font_size: Optional[float] = None
    font_color: Optional[Tuple[int, int, int]] = None
    font_name: Optional[str] = None
    style_name: Optional[str] = None
    heading_level: Optional[int] = None

class StyledBlock(BaseModel):
    """带样式的文本块"""
    text: str
    styles: List[TextStyle]

class GrammarError(BaseModel):
    """语法错误"""
    error_statement: str = Field(alias='errorStatement', description="语法错误语句")
    type_of_error: str = Field(alias='typeOfError', description="语法错误类型")
    revised: str = Field(description="语法修正后的语句")
    
    class Config:
        populate_by_name = True

class TermError(BaseModel):
    """术语错误"""
    error_statement: str = Field(alias='errorStatement', description="术语错误语句")
    type_of_error: str = Field(alias='typeOfError', description="术语错误类型")
    error_word: str = Field(alias='errorWord', description="术语错误词")
    revised: str = Field(description="术语修正后的语句")
    
    class Config:
        populate_by_name = True

class FormatError(BaseModel):
    """格式错误"""
    type_of_error: str = Field(alias='typeOfError', description="格式错误类型")
    current_value: str = Field(alias='currentValue', description="当前错误格式")
    expected_value: str = Field(alias='expectedValue', description="规定正确格式")
    text_snippet: str = Field(alias='textSnippet', description="格式错误片段")
    
    class Config:
        populate_by_name = True




