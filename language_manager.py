from langdetect import detect_langs
from deep_translator import GoogleTranslator


def is_english(text:str) -> bool:
    languages = detect_langs(text)
    for language in languages:
        if language.lang == "en":
            if language.prob > 0.7:
                return True
            else:
                return None
    else:
        return None
    

def translate_to_english(text:str) -> str:
    return GoogleTranslator(source='auto', target='en').translate(text)
