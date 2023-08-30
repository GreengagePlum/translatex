import logging
import os
import sys

import requests

from translatex.translator import TranslationService

log = logging.getLogger("translatex.custom_api")


class TextSynth(TranslationService):
    """Translate using TextSynth API."""
    name = "TextSynth"
    char_limit = 1000
    url = 'https://api.textsynth.com/v1/engines/m2m100_1_2B/translate'
    doc_url = "https://textsynth.com/documentation.html#translations"
    short_description = (
        "TextSynth translation service based on M2M100 model.")

    def __init__(self):
        try:
            self.textsynth_api_key = os.environ['TEXTSYNTH_API_KEY']
        except KeyError:
            log.error("TEXTSYNTH_API_KEY environment variable is not set "
                      "so TextSynth is not available. "
                      "Please set the TEXTSYNTH_API_KEY "
                      "environment variable to your TextSynth API key.")
            sys.exit(1)

    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        headers = {'Authorization': f'Bearer {self.textsynth_api_key}'}
        payload = {'text': [text],
                   'source_lang': source_lang,
                   'target_lang': dest_lang}
        r = requests.post(self.url, headers=headers, json=payload, timeout=10)
        try:
            return r.json()["translations"][0]["text"]
        except Exception as e:
            log.error(e)
            log.error(str(r))
            log.error(r.json())
            return text
