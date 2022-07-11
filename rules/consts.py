"""
Константы и правила для извлечения чисел из текста.
Извлекаются float, integer, roman, intervals.
"""

import re

from yargy.predicates import (
    eq, type as type_, gram,
    in_, dictionary
)
from yargy import (
    or_, rule
)
from yargy import interpretation as interp
from yargy.interpretation import fact

from utils.utils import roman_to_int


#CONSTANTS
INT = type_('INT')
NOUN = gram('NOUN')
ADJF = gram('ADJF')
PRTF = gram('PRTF')
GENT = gram('gent')
NUMR = gram('NUMR')
NUMB = gram('NUMB')
PNCT = type_('PUNCT')
LATIN = type_('LATIN')
DOT = eq('.')
COLON = eq(':')


#NUMBERS
def normalize_float(value):
    value = re.sub('[\s,.]+', '.', value)
    return float(value)

FLOAT = rule(
    INT,
    in_('.,'),
    INT
).interpretation(
    interp.custom(normalize_float)
)

DIGIT = INT.interpretation(
    interp.custom(int)
)

ROMN = rule(
    LATIN
).interpretation(
    interp.custom(roman_to_int)
)

LITERALS = {
    'один': 1,
    'два': 2,
    'три': 3,
    'четыре': 4,
    'пять': 5,
    'шесть': 6,
    'семь': 7,
    'восемь': 8,
    'девять': 9,
    'десять': 10
}

LITERAL = dictionary(LITERALS).interpretation(
    interp.normalized().custom(LITERALS.get)
)

Range = fact(
    'Range',
    ['start', 'stop']
)

VALUE = or_(
    DIGIT,
    FLOAT,
    LITERAL,
    ROMN
)

RANGE = or_(
    rule(
        VALUE.interpretation(Range.start),
        '-',
        VALUE.interpretation(Range.stop),
    ),
    rule(
         VALUE.interpretation(Range.start),
        '-',
        VALUE,
        '-',
        VALUE.interpretation(Range.stop)
    )
).interpretation(
    Range
)

Amount = fact(
    'Amount',
    ['value']
)

AMOUNT = or_(
    VALUE,
    RANGE
).interpretation(
    Amount.value
).interpretation(
    Amount
)