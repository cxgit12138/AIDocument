import json
from pathlib import Path
from Models.RarModels.DomainModels.rar_domain_models import RarConfig

# 加载配置文件
_config_path = Path(__file__).parent / "rarConfig.json"
with open(_config_path, 'r', encoding='utf-8') as f:
    config_data = json.load(f)
    # 使用Pydantic模型解析配置
    rar_config = RarConfig(**config_data)