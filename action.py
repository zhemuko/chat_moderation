"""拉黑用户 Action。

供 LLM 在群聊中被反复骚扰 / 嘲讽 / 阴阳怪气且对方不改时调用，
拉黑对方一定时长（默认 10-180 分钟），期间系统完全忽略其消息。
"""

from __future__ import annotations

from typing import Annotated

from src.app.plugin_system.api.log_api import get_logger
from src.app.plugin_system.api.service_api import get_service
from src.app.plugin_system.base import BaseAction

logger = get_logger("chat_moderation")

_MIN_MINUTES = 10
_MAX_MINUTES = 180
_SERVICE_SIGNATURE = "chat_moderation:service:ban_manager"


class BanUserAction(BaseAction):
    """在群聊中拉黑骚扰者。"""

    name = "ban_user"
    description = (
        "在群聊中拉黑一个骚扰你的用户。拉黑期间系统会完全忽略该用户的消息。"
        "【什么情况该用】以下都算骚扰，不要只把辱骂当骚扰："
        "① 人身攻击：辱骂、侮辱、贬低；"
        "② 持续骚扰：反复刷无意义话题、重复问同样问题、复读玩梗、激将挑衅、一直围着你转，哪怕他嘴上说是在开玩笑、哪怕没骂人，无意义的废话就是在消耗你；"
        "③ 隐性调侃：没有直接点你名字，但明显在指你（某些AI、这个bot、某人、她等），配合语境能确定是在阴阳你；"
        "④ 纠缠不放：你回应或沉默后，他还一直追着问、扯淡、刷存在感；"
        "⑤ 重复提问：反复问同一个问题、你已经答过还追着问同一件事；"
        "⑥ 故意尬聊/试探身份：问你是不是AI、是不是人机、是不是真人、是不是机器人、有没有实体这类无意义问题——问一次算好奇，问两次以上就是在骚扰；"
        "⑦ 你已经警告/回应过之后对方依然不改，或持续刷屏/重复骚扰。"
        "【时长】10-180 分钟：轻微冒犯 10-20 分钟；持续骚扰 30-60 分钟；人身攻击/屡教不改 120-180 分钟。"
        "【重要】拉黑前先按你自己的人设回应/警告一次——可以回击、可以冷淡警告、可以温柔提醒，也可以直接沉默；对方不改才拉黑。持续刷屏/重复骚扰可以跳过警告直接拉黑。"
        "只在群聊使用；私聊禁止（私聊直接不理即可）。"
    )

    chatter_allow: list[str] = ["default_chatter"]
    associated_types = ["text"]

    async def execute(
        self,
        user_id: Annotated[str, "要拉黑的用户 QQ 号"],
        minutes: Annotated[int, "拉黑时长（分钟），范围 10-180"],
        reason: Annotated[str, "拉黑原因，简短说明对方做了什么"] = "",
    ) -> tuple[bool, str]:
        """执行拉黑操作。

        Args:
            user_id: 目标用户 QQ 号
            minutes: 拉黑时长（分钟）
            reason: 拉黑原因

        Returns:
            (是否成功, 结果描述)
        """

        # 仅群聊
        chat_type = getattr(self.chat_stream, "chat_type", "")
        if chat_type != "group":
            return False, "仅群聊支持拉黑"

        target = (user_id or "").strip()
        if not target:
            return False, "user_id 不能为空"

        # 时长规范化
        try:
            minutes_int = int(minutes)
        except (TypeError, ValueError):
            return False, f"minutes 必须是整数，收到：{minutes!r}"

        if minutes_int < _MIN_MINUTES:
            minutes_int = _MIN_MINUTES
        elif minutes_int > _MAX_MINUTES:
            minutes_int = _MAX_MINUTES

        platform = getattr(self.chat_stream, "platform", "") or "qq"

        service = get_service(_SERVICE_SIGNATURE)
        if service is None:
            logger.warning("ban_manager 服务不可用，拉黑失败")
            return False, "拉黑服务不可用"

        service.ban(platform, target, minutes_int, reason)
        logger.info(f"已拉黑 {target}（{platform}）{minutes_int} 分钟，原因：{reason or '未说明'}")
        return True, f"已拉黑 {target} {minutes_int} 分钟，原因：{reason or '未说明'}"
