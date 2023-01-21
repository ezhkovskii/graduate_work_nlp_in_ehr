import re
from typing import Dict



def make_translation(source: str, target: str) -> Dict:
    """
    Сопоставление знаков с помощью функции ord
    """
    assert len(source) == len(target)
    return {
        ord(a): ord(b)
        for a, b in zip(source, target)
    }


DASHES_TRANSLATION = make_translation(
    '‑–—−',
    '----'
)


def delete_punct(text: str) -> str:
    """
    Очищаем текст, заменяем пунктуацию и символы
    """
    punct = '[\\n\\xa0¬\\xad()]'
    text = re.sub(punct, ' ', text)
    text = re.sub(' +', ' ', text)
    text = re.sub('ё', 'е', text)
    text = re.sub('Ё', 'Е', text)
    return text


def preprocess(text: str) -> str:
    """
    Очистка текста и преобразование знака тире разных видов в один
    """
    text = delete_punct(text)
    text = text.translate(DASHES_TRANSLATION)
    # text = tokenize_text(text)

    return text
