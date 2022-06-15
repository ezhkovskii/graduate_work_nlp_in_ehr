from typing import Optional
from collections import defaultdict

from pymorphy2.shapes import is_roman_number
from ipymarkup import show_span_ascii_markup as show_markup
from yargy import (
    Parser
)
from IPython.display import display


ROMAN = {
    'I':1,
    'V':5,
    'X':10,
    'L':50,
    'C':100,
    'D':500,
    'M':1000
}


def roman_to_int(S: str) -> Optional[int]:
    """
    Перевод римских чисел в арабские.
    """
    if is_roman_number(S):
        summ = 0
        for i in range(len(S)-1, -1, -1):
            num = ROMAN[S[i]]
            if 3 * num < summ: 
                summ = summ - num
            else: 
                summ = summ + num
        return summ

    return None


def show_matches(rule, *lines):
    """
    Вывод найденных сущностей 
    """
    parser = Parser(rule)
    for line in lines:
        try:
            matches = parser.findall(line)
            if matches:
                matches = sorted(matches, key=lambda _: _.span)
                spans = [_.span for _ in matches]
                show_markup(line, spans)
                facts = [_.fact for _ in matches]
                if len(facts) == 1:
                    facts = facts[0]
                display(facts)            
        except Exception as e:
            print(f'Строка: {line}.\n {e} \n{list(matches)}')
            raise
           

def join_spans(text, spans):
    spans = sorted(spans)
    return ' '.join(
        text[start:stop]
        for start, stop in spans
    )


class Match(object):
    def __init__(self, facts, spans):
        self.facts = facts
        self.spans = spans


class Extractor:
    def __init__(self, RULE):
        self.parser = Parser(RULE)

    def __call__(self, line):
        matches = self.parser.findall(line)
        spans = [_.span for _ in matches]
        line = join_spans(line, spans)
        matches = self.parser.findall(line)
        matches = sorted(matches, key=lambda _: _.span)
        facts = [_.fact for _ in matches]
        return Match(facts, spans)


def update(main, fact, feature=None):
    for key, value in fact.items():
        if key == feature:
            main[key].append(value)
        else:
            main[key] = value


def show_matches_extractor(rule, *lines):
    extractor = Extractor(rule)
    for line in lines:
        match = extractor(line)
        show_markup(line, match.spans)
        if match.facts:
            main_fact = defaultdict(list)
            for fact in match.facts:
                fact_json = fact.as_json
                update(main_fact, fact_json, 'diseases')
            print(main_fact)
            print()
            