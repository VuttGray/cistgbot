from abc import ABC, abstractmethod
from logging import getLogger

logger = getLogger('logger')


class BaseBotCommand(ABC):
    command = ''
    title = ''
    access_level = 1
    aliases = []
    is_conversation = False
    states = []

    def __init__(self, command: str, title: str, access_level: int,
                 aliases: list = None, is_conversation: bool = False, states: list = None) -> None:
        self.command = command
        self.title = title
        self.access_level = access_level
        self.aliases = aliases if aliases else []
        self.is_conversation = is_conversation
        self.states = states if states else []

    @staticmethod
    def refuse_message(user_access_level: int) -> str:
        if user_access_level > 0:
            return "This is confidential information. You don't have enough access."
        else:
            return "We can just chat. If you need a helper, you should authorized."

    @abstractmethod
    def run(self, user_access_level: int, args: [str]) -> str:
        pass

    @abstractmethod
    def start_conversation(self, user_access_level: int) -> (bool, str, list, str):
        pass

    def __repr__(self):
        return f'{self.title}: {self.command}'


__command_registry: {str: BaseBotCommand} = {}


def get_commands(user_access_level: int) -> {str: BaseBotCommand}:
    return {k: c for k, c in __command_registry.items() if c.access_level <= user_access_level}


def get_conversation_commands() -> {str: BaseBotCommand}:
    return {k: c for k, c in __command_registry.items() if c.is_conversation}


def get_command(command_name: str, user_access_level: int) -> BaseBotCommand:
    commands = get_commands(user_access_level)
    return commands.get(command_name)


def find_command(message_text: str, user_access_level: int) -> (BaseBotCommand, [str]):
    commands = get_commands(user_access_level)
    for c in commands.values():
        for a in c.aliases:
            if message_text.lower().startswith(a):
                args = message_text[len(a):].strip().split(' ')
                return c, args
    return None, None


def command_register(cls):
    global __command_registry
    instance = cls()
    __command_registry[instance.command] = instance
    return cls
