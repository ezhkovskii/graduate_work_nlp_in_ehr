from typing import Optional

from yargy import (
    or_, rule, not_
)
from yargy.pipelines import morph_pipeline
from yargy.predicates import (
    eq, in_
)
from yargy.interpretation import fact

import pymorphy2

from .consts import Range, AMOUNT


with open('data\\diseases_сustom.txt', encoding='utf-8') as f:
    diseases = f.read()
    diseases = diseases.split('\n')

Diseases = morph_pipeline(
    diseases
)
DISEASES = rule(Diseases)

MORPH = pymorphy2.MorphAnalyzer()


# Правила для основного диагноза
MainDiagnosis = fact(
    'MainDiagnosis',
    ['form', 'virus', 'diseases']
)

virus_identified = (
    'идентифицирован',
    'подтвержденная',
    'подтверждённая',
    'U07.1'
)
VIRUS_IDENTIFIED = morph_pipeline(
    virus_identified
).interpretation(MainDiagnosis.virus.const(True))

virus_not_identified = (
    'не идентифицирован',
    'неидентифицирован',
    'неиндентифицирован',
    'U07.2',    
    'неподтвержденная',
    'неподтверждённая',
    'не подтверждённая',
    'не подтвержденная',
    'подозрение'
)
VIRUS_NOT_IDENTIFIED = morph_pipeline(
    virus_not_identified
).interpretation(MainDiagnosis.virus.const(False))

# Правило для подтверждения ковида (True, False)
VIRUS = or_(
    VIRUS_IDENTIFIED,
    VIRUS_NOT_IDENTIFIED
).interpretation(MainDiagnosis.virus)


# Правило для поиска заболеваний
DISEASES_FOR_MAIN = DISEASES.interpretation(MainDiagnosis.diseases)

Forms_dict = {
    'легкий': 1,
    'лёгкий': 1,
    'средний': 2,
    'тяжелый': 3,
    'тяжёлый': 3
}
Forms_set = set(Forms_dict.keys())

Forms = morph_pipeline(
    Forms_dict.keys()
)

def forms_morph(form: str) -> Optional[int]:
    """
    Поиск пересечения нормальных форм стадий ковида с нормальной формой слова из текста
    """
    parsers = MORPH.parse(form)
    normal_forms = {parser.normal_form for parser in parsers}
    intersection = Forms_set & normal_forms
    if intersection:
        return Forms_dict[list(intersection)[0]]
    print(f'НЕ НАЙДЕНА НОРМАЛЬНАЯ ФОРМА. word: {form}, forms: {normal_forms}')
    return None

FORM_RANGE = rule(
        Forms.interpretation(Range.start.normalized().custom(forms_morph)),
        not_(eq(Forms)).optional(),
        Forms.interpretation(Range.stop.normalized().custom(forms_morph)),
).interpretation(
    Range
)

FORM = rule(Forms).interpretation(
    Range.start.normalized().custom(forms_morph)
).interpretation(
    Range
)

# Правило для форм ковида
FORMS = or_(
    FORM,
    FORM_RANGE
).interpretation(
    MainDiagnosis.form
)

MAIN_DIAGNOSIS = or_(
    DISEASES_FOR_MAIN,
    FORMS,
    VIRUS
).interpretation(
    MainDiagnosis
)


# Осложнение в диагнозе
СomplicationDiagnosis = fact(
    'СomplicationDiagnosis',
    ['diseases', 'form', 'respiratory_failure']
)

DISEASES_FOR_COMPLICATION = DISEASES.interpretation(СomplicationDiagnosis.diseases)

FORMS = or_(
    FORM,
    FORM_RANGE
).interpretation(
    СomplicationDiagnosis.form
)

DN = morph_pipeline(['дн', 'дыхательная недостаточность'])

RESPIRATORY_FAILURE = rule(
    DN,
    not_(eq(AMOUNT)).optional(), 
    AMOUNT.interpretation(СomplicationDiagnosis.respiratory_failure),
    not_(eq(AMOUNT)).optional()
)

СOMPLICATION_DIAGNOSIS = or_(
        DISEASES_FOR_COMPLICATION,    
        FORMS,
        RESPIRATORY_FAILURE
).interpretation(СomplicationDiagnosis)


# Сопутствующий диагноз
ConcomitantDiagnosis = fact(
    'ConcomitantDiagnosis',
    ['diseases', 'info']
)

DISEASES_FOR_CONCOMITANT = DISEASES.interpretation(ConcomitantDiagnosis.diseases)

CONCOMITANT_DIAGNOSIS = or_(
    rule(
        DISEASES_FOR_CONCOMITANT
    ),
    rule(
        DISEASES_FOR_CONCOMITANT,
        not_(eq(DISEASES_FOR_CONCOMITANT)).repeatable().interpretation(ConcomitantDiagnosis.info),
        DISEASES_FOR_CONCOMITANT.optional()
    ),
    rule(
        not_(eq(DISEASES_FOR_CONCOMITANT)).repeatable().interpretation(ConcomitantDiagnosis.info),
        DISEASES_FOR_CONCOMITANT,
        in_('.,').optional()
    )
   ).interpretation(ConcomitantDiagnosis)
