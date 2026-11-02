"""拉黑消息过滤事件处理器。

订阅 ON_MESSAGE_RECEIVED，在消息进入聊天流之前检查发送者是否被拉黑。
命中拉黑 → 返回 EventDecision.STOP → 消息不再传给后续处理器（如 distributor）。
"""

from __future__ import annotations

from typing import Any

from src.app.plugin_system.api.log_api import get_logger
from src.app.plugin_system.api.service_api import get_service
from src.app.plugin_system.base import BaseEventHandler
from src.app.plugin_system.types import EventType
from src.kernel.event import EventDecision

logger = get_logger("chat_moderation")

_SERVICE_SIGNATURE = "chat_moderation:service:ban_manager"


class BanMessageFilter(BaseEventHandler):
    """拦截被拉黑用户的消息。"""

    name = "ban_message_filter"
    description = "在消息进入聊天流前拦截被拉黑用户的消息"
    # 权重高于 distributor（默认 0），确保先于消息分发执行
    weight = 100
    intercept_message = True
    init_subscribe = [EventType.ON_MESSAGE_RECEIVED]

    async def execute(
        self,
        event_name: str,
        params: dict[str, Any],
    ) -> tuple[EventDecision, dict[str, Any]]:
        """检查消息发送者是否被拉黑。

        Args:
            event_name: 事件名称
            params: 事件参数，包含 message

        Returns:
            (事件决策, 事件参数)。命中拉黑时返回 STOP 阻断后续处理。
        """

        message = params.get("message")
        if message is None:
            return EventDecision.SUCCESS, params

        chat_type = getattr(message, "chat_type", "") or ""
        if chat_type != "group":
            return EventDecision.SUCCESS, params

        sender_id = str(getattr(message, "sender_id", "") or "").strip()
        platform = str(getattr(message, "platform", "") or "").strip() or "qq"
        if not sender_id:
            return EventDecision.SUCCESS, params

        service = get_service(_SERVICE_SIGNATURE)
        if service is None:
            return EventDecision.SUCCESS, params

        if service.is_banned(platform, sender_id):
            logger.info(f"已拦截被拉黑用户 {sender_id}（{platform}）的群聊消息")
            return EventDecision.STOP, params

        return EventDecision.SUCCESS, params
