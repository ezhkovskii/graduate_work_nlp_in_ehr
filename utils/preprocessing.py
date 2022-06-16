import re


def make_translation(source, target):
    assert len(source) == len(target)
    return {
        ord(a): ord(b)
        for a, b in zip(source, target)
    }


DASHES_TRANSLATION = make_translation(
    '‑–—−',
    '----'
)


def delete_punct(text):
    punct = '[\\n\\xa0¬\\xad()]'
    text = re.sub(punct, ' ', text)
    text = re.sub(' +', ' ', text)
    text = re.sub('ё', 'е', text)
    text = re.sub('Ё', 'Е', text)
    return text


def preprocess(text):
    text = delete_punct(text)
    text = text.translate(DASHES_TRANSLATION)
    # text = tokenize_text(text)

    return text
