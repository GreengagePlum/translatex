import logging
import sys

import requests

from translatex.translator import TranslationService

log = logging.getLogger("translatex.custom_api")


class IRMA(TranslationService):
    """Translate using Unistra IRMA DLMDS.

    You need to be on Unistra's network to be able to access this translation service.
    """

    name = "IRMA - M2M100"
    overall_char_limit = 500000
    char_limit = 1000
    array_support = True
    array_item_limit = 1024
    array_item_char_limit = 0
    array_overall_char_limit = 30000
    url = "https://dlmds.math.unistra.fr/translation"
    doc_url = "https://dlmds.math.unistra.fr/"
    short_description = (
        "IRMA's translation service running the M2M100 model "
        "on a Quadro P6000 Nvidia GPU. Privacy is guaranteed!"
    )

    def __init__(self):
        try:
            requests.get(self.url, timeout=(4, None))
        except requests.ConnectTimeout:
            log.error(
                f"{self.name} API unavailable, can't establish a connection. "
                "Most likely due to you not being on the Unistra network."
            )
            sys.exit(1)

    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        payload = {
            "text": text,
            "source_lang": source_lang,
            "target_lang": dest_lang,
        }
        r = requests.post(self.url, json=payload, timeout=10)
        try:
            return r.json()["translations"][0]["text"]
        except Exception as e:
            log.error(e)
            log.error(str(r))
            log.error(r.json())
            return text
