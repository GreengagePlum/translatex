from translatex.translator import TranslationService


class DoNoTTranslate(TranslationService):
    """A Mockup translation service that does not translate anything."""

    name = "Do not translate"

    def translate(self, text: str, source_lang: str, dest_lang: str) -> str:
        return text
