"""chat_moderation 插件入口。

群聊行为管理：被骚扰 / 嘲讽 / 阴阳怪气时，可毒舌回击后拉黑对方。
"""

from __future__ import annotations

from src.app.plugin_system.base import BasePlugin, register_plugin

from .action import BanUserAction
from .config import ChatModerationConfig
from .handler import BanMessageFilter
from .service import BanManagerService


@register_plugin
class ChatModerationPlugin(BasePlugin):
    """群聊行为管理插件。"""

    plugin_name = "chat_moderation"
    plugin_description = "群聊拉黑：被骚扰时毒舌回击并拉黑对方，拉黑期间忽略其消息"
    plugin_version = "1.0.0"

    configs: list[type] = [ChatModerationConfig]
    dependent_components: list[str] = []

    def get_components(self) -> list[type]:
        """返回插件提供的组件类。

        Returns:
            组件类列表（Action / Service / EventHandler）
        """

        return [BanUserAction, BanManagerService, BanMessageFilter]
