class BotAuth:
    def __init__(self,
                 admins: [int],
                 authorized_users: [int] = None):
        if len(admins) == 0:
            raise ValueError("Administrators list may not be empty")
        self.admins = admins
        self.authorized_users = authorized_users if authorized_users else []

    def is_authorized(self, user_id: int) -> bool:
        return user_id in self.admins or user_id in self.authorized_users

    def is_admin(self, user_id: int) -> bool:
        return user_id in self.admins

    def get_user_access_level(self, user_id: int) -> int:
        if self.is_admin(user_id):
            return 100
        elif self.is_authorized(user_id):
            return 1
        else:
            return 0

    def get_admins(self) -> [int]:
        return self.admins
