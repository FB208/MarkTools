from flask_login import UserMixin


class SessionUser(UserMixin):
    """轻量级的基于会话的用户对象，用于不落库场景。

    仅保存必要字段，支持 Flask-Login 的序列化/反序列化。
    """

    def __init__(self, user_id, email=None, nikename=None, extra=None):
        # Flask-Login 期望 get_id() 可返回字符串
        self.id = str(user_id) if user_id is not None else None
        self.email = email
        self.nikename = nikename
        self.extra = extra or {}

    @classmethod
    def from_dict(cls, data: dict | None):
        if not data:
            return None
        user_id = data.get('id') or data.get('user_id') or data.get('email')
        nikename = data.get('nikename') or data.get('nickname') or data.get('name')
        return cls(user_id=user_id, email=data.get('email'), nikename=nikename, extra=data)


