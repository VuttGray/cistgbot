from cistgbot.command.main import BaseBotCommand, get_commands, command_register


@command_register
class Help(BaseBotCommand):
    def __init__(self): super().__init__(command="/help",
                                         title="Help",
                                         access_level=1,
                                         aliases=['help', 'what can you do'])

    def run(self, user_access_level: int, *args):
        if user_access_level < self.access_level:
            return self.refuse_message(user_access_level)

        response = "Commands:\n"
        for bot_command in get_commands(user_access_level).values():
            response += f"{bot_command.title}: {bot_command.command}\n"
        return response

    def start_conversation(self, user_access_level: int) -> (bool, str, list, str):
        pass
