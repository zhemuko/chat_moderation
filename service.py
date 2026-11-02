"""群聊拉黑管理服务。

提供拉黑 / 解封 / 查询能力，供 Action 与 EventHandler 共享状态。
状态保存在模块级字典中（进程内），重启后自动清空。
"""

from __future__ import annotations

import time
from typing import Any

from src.app.plugin_system.api.log_api import get_logger
from src.app.plugin_system.base import BaseService

logger = get_logger("chat_moderation")

# 拉黑表：key = "{platform}:{user_id}"，value = 到期时间戳（time.time()）
_BAN_TABLE: dict[str, float] = {}
# 拉黑原因表：key 同上，value = 原因文本
_BAN_REASONS: dict[str, str] = {}


def _make_key(platform: str, user_id: str) -> str:
    """构造拉黑表的键。"""

    return f"{platform}:{user_id}"


class BanManagerService(BaseService):
    """群聊拉黑管理服务。"""

    name = "ban_manager"
    description = "管理群聊中被拉黑的用户：拉黑、解封、查询"

    def ban(
        self,
        platform: str,
        user_id: str,
        minutes: int,
        reason: str = "",
    ) -> float:
        """拉黑一个用户。

        Args:
            platform: 平台标识（如 qq）
            user_id: 用户 ID
            minutes: 拉黑时长（分钟）
            reason: 拉黑原因

        Returns:
            到期时间戳（time.time() 格式）
        """

        key = _make_key(platform, user_id)
        expire_at = time.time() + minutes * 60
        _BAN_TABLE[key] = expire_at
        _BAN_REASONS[key] = reason
        logger.info(
            f"拉黑用户 {user_id}（{platform}），{minutes} 分钟，原因：{reason or '未说明'}"
        )
        return expire_at

    def is_banned(self, platform: str, user_id: str) -> bool:
        """检查用户当前是否处于拉黑状态（过期记录会自动清除）。

        Args:
            platform: 平台标识
            user_id: 用户 ID

        Returns:
            是否仍在拉黑期内
        """

        key = _make_key(platform, user_id)
        expire_at = _BAN_TABLE.get(key)
        if expire_at is None:
            return False

        if time.time() >= expire_at:
            _BAN_TABLE.pop(key, None)
            _BAN_REASONS.pop(key, None)
            logger.debug(f"用户 {user_id}（{platform}）拉黑已到期，自动解除")
            return False

        return True

    def unban(self, platform: str, user_id: str) -> bool:
        """解除对某个用户的拉黑。

        Args:
            platform: 平台标识
            user_id: 用户 ID

        Returns:
            是否成功解除（之前存在拉黑记录时为 True）
        """

        key = _make_key(platform, user_id)
        existed = _BAN_TABLE.pop(key, None) is not None
        _BAN_REASONS.pop(key, None)
        if existed:
            logger.info(f"已解除对 {user_id}（{platform}）的拉黑")
        return existed

    def list_bans(self) -> dict[str, dict[str, Any]]:
        """列出当前所有有效的拉黑记录。

        Returns:
            键为 "{platform}:{user_id}" 的字典，值包含到期时间、剩余秒数、原因
        """

        now = time.time()
        result: dict[str, dict[str, Any]] = {}
        for key, expire_at in list(_BAN_TABLE.items()):
            if now >= expire_at:
                _BAN_TABLE.pop(key, None)
                _BAN_REASONS.pop(key, None)
                continue
            result[key] = {
                "expire_at": expire_at,
                "remaining_seconds": int(expire_at - now),
                "reason": _BAN_REASONS.get(key, ""),
            }
        return result
