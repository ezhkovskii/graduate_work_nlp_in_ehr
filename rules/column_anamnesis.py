"""
Правила для извлечения информации из колонки anamnesis.
Извлекаем жалобы пациента и лекарства, которые он принимал.
"""

import json

from yargy import (
    or_, rule
)
from yargy.pipelines import morph_pipeline, caseless_pipeline
from yargy.interpretation import fact


with open('data/medicaments.txt', encoding='utf-8') as f:
    medicaments = f.read()
    medicaments = medicaments.split('\n')


with open('data/complaints.json', encoding='utf-8') as f:
    complaints_json = json.load(f)
    complaints_json.pop('temperature_value', None)


Medicaments = caseless_pipeline(
    medicaments
)

Anamnesis = fact(
    'Anamnesis',
    ['medicaments', 'complaints']
)

MEDICAMENTS = rule(Medicaments).interpretation(Anamnesis.medicaments)

compalints_values = []
for values in complaints_json.values():
    compalints_values += values

complaint_pipeline = morph_pipeline(compalints_values).interpretation(Anamnesis.complaints.normalized())

COMPLAINTS = rule(complaint_pipeline).interpretation(Anamnesis)

ANAMNESIS = or_(
    MEDICAMENTS,
    COMPLAINTS
).interpretation(Anamnesis)
