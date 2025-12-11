from pydantic import BaseModel, Field
from typing import Optional, List


# API配置相关模型
class ApiConfig(BaseModel):
    """API配置"""
    key: str = Field(alias='key', description="API密钥")
    base_url: str = Field(alias='baseUrl', description="API基础URL")
    model_name: str = Field(alias='modelName', description="模型名称")
    
    class Config:
        populate_by_name = True


class ConcurrencyConfig(BaseModel):
    """并发配置"""
    max_concurrent_requests: int = Field(alias='maxConcurrentRequests', description="最大并发请求数")
    
    class Config:
        populate_by_name = True


class OutputConfig(BaseModel):
    """输出配置"""
    path: str = Field(description="输出路径")
    
    class Config:
        populate_by_name = True


class RarConfig(BaseModel):
    """RAR配置模型"""
    annotation: Optional[str] = Field(None, description="配置注释")
    api: ApiConfig = Field(description="API配置")
    concurrency: ConcurrencyConfig = Field(description="并发配置")
    output: OutputConfig = Field(description="输出配置")
    
    class Config:
        populate_by_name = True


class RarData(BaseModel):
    """定义RAR数据模型，包含所有需要的属性"""
    urs_no: str = Field(alias='UrsNo', description="URS编号")
    requirement_desc: str = Field(alias='RequirementDesc', description="URS需求描述")
    belong_chapter: str = Field(alias='BelongChapter', description="URS所属章节")
    failure_event: Optional[str] = Field(None, alias='FailureEvent', description="失效事件")
    potential_failure_consequences: Optional[str] = Field(None, alias='PotentialFailureConsequences', description="潜在失效后果")
    severity: Optional[str] = Field(None, description="严重性")
    probability: Optional[str] = Field(None, description="可能性")
    risk_level: Optional[str] = Field(None, alias='RiskLevel', description="风险等级")
    detectability: Optional[str] = Field(None, description="可检测性")
    risk_priority: Optional[str] = Field(None, alias='RiskPriority', description="风险优先级")
    risk_control_measures: Optional[str] = Field(None, alias='RiskControlMeasures', description="风险控制措施")

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True


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