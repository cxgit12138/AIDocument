import json
from pathlib import Path

# 加载转换配置文件
_config_path = Path(__file__).parent / "fileConvertConfig.json"
with open(_config_path, 'r', encoding='utf-8') as f:
    conversion_config = json.load(f)