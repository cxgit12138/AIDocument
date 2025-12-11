from openai import AsyncOpenAI
from Configs.RarConfig.rar_config_init import rar_config

# 创建客户端
client = AsyncOpenAI(
    api_key=rar_config.api.key,
    base_url=rar_config.api.base_url
)

# 模型名称
MODEL_NAME = rar_config.api.model_name