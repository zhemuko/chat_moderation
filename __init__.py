"""chat_moderation 插件包。

群聊行为管理：被骚扰 / 嘲讽 / 阴阳怪气时，按角色人设回应并拉黑对方。
拉黑期间系统会忽略该用户的消息。

插件入口在 :mod:`plugin` 模块中由 ``@register_plugin`` 装饰的
``ChatModerationPlugin`` 类注册，通过插件加载器自动发现。

注意：本文件不能 import .plugin，否则会与插件加载器形成循环导入。
"""

__all__: list[str] = []
