from pydantic import BaseModel, Field
from typing import Optional, List


class RarData(BaseModel):
    """定义RAR数据模型，包含所有需要的属性"""
    UrsNo: str=Field(description="URS编号")
    RequirementDesc: str=Field(description="URS需求描述")
    BelongChapter: str=Field(description="URS所属章节")
    # BelongModule: Optional[str] = Field(None,description="URS所属模块")
    FailureEvent: Optional[str] = Field(None,description="失效事件")
    PotentialFailureConsequences: Optional[str] = Field(None,description="潜在失效后果")
    Severity: Optional[str] = Field(None,description="严重性")
    Probability: Optional[str] = Field(None,description="可能性")
    RiskLevel: Optional[str] = Field(None,description="风险等级")
    Detectability: Optional[str] = Field(None,description="可检测性")
    RiskPriority: Optional[str] = Field(None,description="风险优先级")
    RiskControlMeasures: Optional[str] = Field(None,description="风险控制措施")

    class Config:
        arbitrary_types_allowed = True


class RiskMatrix:
    """风险矩阵模型，定义风险等级和风险优先级的计算规则"""

    # 风险等级矩阵
    risk_level_matrix = {
        "高": {  # 严重性为"高"
            "高": "1",  # 可能性为"高" → 高*高=1(高风险)
            "中": "1",
            "低": "2",
        },
        "中": {  # 严重性为"中"
            "高": "1",
            "中": "2",
            "低": "3",
        },
        "低": {  # 严重性为"低"
            "高": "2",
            "中": "3",
            "低": "3",
        }
    }

    # 风险优先级矩阵
    risk_priority_matrix = {
        "1": {  # 风险等级为"1"
            "高": "中",  # 可检测性"高" ->高风险*高可检测性="中"风险可优先级
            "中": "高",
            "低": "高",
        },
        "2": {
            "高": "低",
            "中": "中",
            "低": "高",
        },
        "3": {
            "高": "低",
            "中": "低",
            "低": "中"
        }
    }


class RarAnalysisResult(BaseModel):
    """RAR分析结果模型"""
    total_items: int
    items: List[RarData]
    output_file: str