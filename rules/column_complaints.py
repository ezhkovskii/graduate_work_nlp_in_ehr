import json
from copy import copy

from yargy import (
    or_, rule, not_
)
from yargy.pipelines import morph_pipeline
from yargy.predicates import (
    eq, in_caseless
)
from yargy.interpretation import fact

from .consts import  AMOUNT


with open('data/complaints.json', encoding='utf-8') as f:
    complaints = json.load(f)
    
Complaint = fact(
    'Complaint',
    list(complaints.keys())
)

temperature = copy(complaints['temperature'])
complaints.pop('temperature', None)
complaints.pop('temperature_value', None)

complaint_pipelines = []
for complaint, synonyms in complaints.items():
    complaint_pipelines.append(
        rule(morph_pipeline(synonyms)).interpretation(getattr(Complaint, complaint).normalized()).interpretation(Complaint)
    )

temperature_pipeline = morph_pipeline(temperature)
TEMPERATURE = or_(
    # rule(
    #     temperature_pipeline.interpretation(Complaint.temperature)
    # ),
    rule(
        temperature_pipeline.interpretation(Complaint.temperature),
        not_(eq(AMOUNT)).optional().repeatable(), 
        AMOUNT.optional().interpretation(Complaint.temperature),
        in_caseless('СC')
    )
)

COMPLAINT = or_(*complaint_pipelines, TEMPERATURE).interpretation(Complaint)
