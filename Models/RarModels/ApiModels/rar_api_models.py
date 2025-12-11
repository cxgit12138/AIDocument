"""
RAR模块API相关模型
"""
from pydantic import BaseModel
from typing import Optional
from Models.RarModels.DomainModels.rar_domain_models import RarConfig


class RarConfigWrapper(BaseModel):
    """RAR配置包装类"""
    annotation: Optional[str] = None
    rar_config: RarConfig
    
    class Config:
        populate_by_name = True
