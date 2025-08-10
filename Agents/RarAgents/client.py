import json
# import os
from openai import AsyncOpenAI
from pathlib import Path

# 获取配置文件路径
config_path = (
    Path(__file__).parent          # 当前文件所在目录（Agents）
    .parent.parent          # 向上二级到项目根目录（AgentPlatform）
    / "Configs"
    / "RarConfig"
    / "rarConfig.json"             # 实际配置文件路径
)

# 读取配置
with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

# 创建客户端
client = AsyncOpenAI(
    api_key=config["api"]["key"],
    base_url=config["api"]["baseUrl"]
)

# 模型名称
MODEL_NAME = config["api"]["modelName"]