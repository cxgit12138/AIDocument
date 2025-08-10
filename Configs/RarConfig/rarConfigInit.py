import json
from pathlib import Path

# 加载配置文件
_config_path = Path(__file__).parent / "rarConfig.json"
with open(_config_path, 'r', encoding='utf-8') as f:
    rar_config = json.load(f)