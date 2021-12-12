from logging import getLogger
from time import sleep

from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from cistgbot.auth import BotAuth
from cistgbot.command.main import get_command, find_command, get_conversation_commands
from cistgbot.exceptions import TGBotConfigurationError
from cistgbot.lexicon import BotLexicon

logger = getLogger('logger')


class BotConfig:
    def __init__(self, **kwargs):
        token = kwargs.pop('token')
        self.token = token

        self.admins = kwargs.pop('admins', [])
        self.intents = kwargs.pop('intents', {})


_bc: BotConfig
_ba: BotAuth
_bl: BotLexicon
_bot: Bot


def configure(**kwargs):
    global _bc, _ba, _bl, _bot
    _bc = BotConfig(**kwargs)
    _ba = BotAuth(_bc.admins)
    _bl = BotLexicon(_bc.intents)
    _bot = Bot(_bc.token)


def __create_keyboard(button_settings: [str]) -> InlineKeyboardMarkup:
    buttons = []
    for line in button_settings:
        button_row = []
        for text, callback in line:
            button_row.append(InlineKeyboardButton(text=text, callback_data=callback))
        buttons.append(button_row)
    return InlineKeyboardMarkup(buttons)


def __start_conversation(update: Update, _: CallbackContext) -> int:
    command_name = update.message.text
    logger.debug(f'Conversation {command_name} was attempted to start by {update.message.from_user.id}')

    user_access_level = _ba.get_user_access_level(update.message.from_user.id)
    command = get_command(command_name, user_access_level)

    if command is None:
        return ConversationHandler.END

    logger.debug(f'Conversation {command} was started by {update.message.from_user.id}')
    has_access, response, buttons, conv_state = command.start_conversation(user_access_level)
    if not has_access:
        return ConversationHandler.END

    keyboard = __create_keyboard(buttons)
    if keyboard:
        update.message.reply_text(response, reply_markup=keyboard)
    else:
        update.message.reply_text(response)
    return conv_state


def __cancel_conversation(update: Update, _: CallbackContext) -> int:
    logger.debug(f'Conversation was canceled by {update.message.from_user.id}')
    update.message.reply_text(_bl.get_response(_bl.CANCEL_CONVERSATION))
    return ConversationHandler.END


def __handle_command(update: Update, context: CallbackContext) -> None:
    logger.debug(f'Command "{update.message.text}" was received from {update.message.from_user.id}')
    command_name = update.message.text.split(" ")[0]
    args = update.message.text.split(" ")[1:]

    user_access_level = _ba.get_user_access_level(update.message.from_user.id)
    command = get_command(command_name, user_access_level)

    if command.is_conversation:
        return
    response = command.run(user_access_level, *args) if command else _bl.get_response_by_intent(_bl.UNKNOWN_INTENT)
    context.bot.send_message(chat_id=update.message.chat_id, text=response)


def __handle_text(update: Update, context: CallbackContext) -> None:
    logger.debug(f'Bot gets the text "{update.message.text}" from {update.message.from_user.id}')
    if (response := __try_find_command(update.message.text, update.message.from_user.id)) is not None:
        context.bot.send_message(chat_id=update.message.chat_id, text=response)
    else:
        response = _bl.get_response(update.message.text)
        context.bot.send_message(chat_id=update.message.chat_id, text=response)


def __try_find_command(message_text: str, user_id: int) -> str:
    user_access_level = _ba.get_user_access_level(user_id)
    command, args = find_command(message_text, user_access_level)
    if command:
        return command.run(user_access_level, args)


def send_message(message: str, chats: [int] = None):
    logger.debug(f'Bot message to send "{message}" to chats {chats}')
    chats = chats if chats else _bc.admins
    for chat_id in chats: 
        _bot.send_message(chat_id, message)


def run():
    if _bc is None:
        raise TGBotConfigurationError('Bot is not configured. Please use the "configure" method')

    updater = Updater(token=_bc.token, use_context=True)
    # get the full list of bot commands
    conv_commands = get_conversation_commands()
    # create conversation handler and generate callback query handlers for each states in each command
    sh = {state: state_handlers
          for command in conv_commands.values()
          for state, state_handlers in command.states}
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler(command[1:], __start_conversation) for command in conv_commands.keys()],
        states=sh,
        fallbacks=[CommandHandler('cancel', __cancel_conversation)])
    # Register handlers
    updater.dispatcher.add_handler(conv_handler)
    updater.dispatcher.add_handler(MessageHandler(Filters.command, __handle_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, __handle_text))

    while True:
        try:
            logger.info('Bot launched')
            updater.start_polling(drop_pending_updates=True)
            updater.idle()
        except Exception as ex:
            logger.error(ex)
            sleep(2)
