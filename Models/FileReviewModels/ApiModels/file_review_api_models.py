# 保留以下与API直接相关的模型
from pydantic import BaseModel, Field
from typing import List, Optional
from Models.FileReviewModels.DomainModels.file_review_domain_models import FileReviewConfig,GrammarError,TermError,FormatError



class Config(BaseModel):
    annotation: Optional[str] = None
    file_review: FileReviewConfig = Field(alias='fileReview')
    
    class Config:
        populate_by_name = True



class FileReviewResult(BaseModel):
    grammar_errors: List[GrammarError]
    term_errors: List[TermError]
    format_errors: List[FormatError]


class Example:
    """返回结果示例"""
    json_schema_extra = {
        "example": {
            "grammarErrors": [
                {
                    "errorStatement":"她很好我觉得",
                    "typeOfError":"语序混乱",
                    "revised":"我觉得她很好"
                }
            ],
            "termErrors":[
                {
                    "errorStatement": "这个json文件需要解析。",
                    "typeOfError":"术语大小写不规范",
                    "errorWord":"json",
                    "revised":"JSON"
                }
            ],
            "formatErrors":[
                {
                    "typeOfError": "正文字体大小异常",
                    "currentValue": "16.0pt",
                    "expectedValue": "10.5pt",
                    "textSnippet": "明天打算去看电影"
                }
            ]
        }
    }