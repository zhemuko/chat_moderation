"""chat_moderation 插件配置。

提供群聊拉黑功能的开关与时长范围配置。
"""

from src.app.plugin_system.base import BaseConfig, Field, SectionBase, config_section


class ChatModerationConfig(BaseConfig):
    """群聊行为管理配置。"""

    name = "config"
    description = "群聊行为管理配置"

    @config_section("moderation")
    class ModerationSection(SectionBase):
        """拉黑功能参数。"""

        enabled: bool = Field(
            default=True,
            description="是否启用群聊拉黑功能",
        )
        min_ban_minutes: int = Field(
            default=10,
            description="最短拉黑时长（分钟）",
        )
        max_ban_minutes: int = Field(
            default=180,
            description="最长拉黑时长（分钟）",
        )

    moderation: ModerationSection = Field(
        default_factory=ModerationSection,
        description="拉黑功能配置",
    )
