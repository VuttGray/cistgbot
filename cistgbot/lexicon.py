from random import choice
from re import sub

from nltk import edit_distance


def clean(text: str) -> str:
    cleaned_text = sub(r'[^\w\s]+', '', text.lower())
    cleaned_text = sub(r'\s+', ' ', cleaned_text).strip()
    return cleaned_text


class BotLexicon:
    UNKNOWN_INTENT = 'unknown_intent'
    CANCEL_CONVERSATION = 'cancel_conversation'

    def __init__(self, intents: dict):
        self.intents = intents

    def get_intent(self, in_text: str) -> str:
        for intent in self.intents.keys():
            for example in self.intents[intent]['examples']:
                text1 = clean(example)
                text2 = clean(in_text)
                if edit_distance(text1, text2) / max(len(text1), len(text2)) < 0.4:
                    return intent
        return self.UNKNOWN_INTENT

    def get_response(self, in_text: str) -> str:
        intent = self.get_intent(in_text)
        return self.get_response_by_intent(intent)

    def get_response_by_intent(self, intent: str) -> str:
        return choice(self.intents[intent]['responses'])
