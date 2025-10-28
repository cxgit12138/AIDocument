"""
插件管理器，用于动态加载和管理转换插件
"""

import importlib
import logging
from typing import Dict, Any, Callable
from pathlib import Path

logger = logging.getLogger("plugin_manager")


class ConversionPluginManager:
    """转换插件管理器"""

    def __init__(self):
        self.plugins = {}
        self._load_plugins()

    def _load_plugins(self):
        """动态加载所有转换插件"""
        plugins_dir = Path(__file__).parent
        for plugin_file in plugins_dir.glob("*_converter.py"):
            if plugin_file.name != "plugin_manager.py":
                module_name = plugin_file.stem
                try:
                    module = importlib.import_module(f"Agents.FileConvertAgents.{module_name}")
                    self.plugins[module_name] = module
                    logger.info(f"Loaded plugin: {module_name}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {module_name}: {e}")

    def get_converter(self, converter_name: str):
        """获取指定的转换器"""
        return self.plugins.get(converter_name)

    def get_all_plugins(self):
        """获取所有插件"""
        return self.plugins

    def register_plugin(self, name: str, plugin_module):
        """注册新的插件"""
        self.plugins[name] = plugin_module
        logger.info(f"Registered plugin: {name}")

    def unregister_plugin(self, name: str):
        """注销插件"""
        if name in self.plugins:
            del self.plugins[name]
            logger.info(f"Unregistered plugin: {name}")


# 创建全局插件管理器实例
plugin_manager = ConversionPluginManager()
