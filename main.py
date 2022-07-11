from datetime import datetime
from typing import List, Dict

import pandas as pd

from extraction.extraction_diagnosis import ExtractionDiagnosis
from extraction.extraction_complaint import ExtractionComplaints
from extraction.extraction_anamnesis import ExtractionAnamnesis

COUNT_ROWS = 2346


def load_dataset() -> pd.DataFrame:
    """
    Загрузка датасета
    """
    df = pd.read_csv('epicrises_text.csv')
    df = df.fillna('')
    return df


def add_id(df_id: pd.Series, df_facts: List[pd.DataFrame]) -> None:
    """
    Добавление колонки id в датасеты
    """
    for df in df_facts:
        df['id'] = df_id


def create_excel(sheets: Dict, name: str) -> None:
    """
    Создание файла excel с несколькими листами sheets
    """
    writer = pd.ExcelWriter(name, engine='xlsxwriter')
    for sheet_name in sheets.keys():
        sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()


if __name__ == "__main__":
    print(f'Запуск. Обработка текстов - {COUNT_ROWS} шт.')
    start_time = datetime.now()

    df = load_dataset()
    df['id'] = list(range(1, len(df) + 1))
    df_id = df.id.copy()

    print('Обработка колонки diagnosis')
    df_diagnosis = list(df.diagnosis.copy())[:COUNT_ROWS]
    extraction = ExtractionDiagnosis(df_diagnosis)
    df_facts_main, df_facts_complication, df_facts_concomitant = extraction()

    print('Обработка колонки complaint')
    df_complaint = list(df.complaint.copy())[:COUNT_ROWS]
    extraction = ExtractionComplaints(df_complaint)
    df_facts_complaint = extraction()

    print('Обработка колонки anamnesis')
    df_anamnesis = list(df.anamnesis.copy())[:COUNT_ROWS]
    extraction = ExtractionAnamnesis(df_anamnesis)
    df_facts_anamnesis = extraction()

    sheets = {
        'Main': df_facts_main,
        'Complication': df_facts_complication,
        'Concomitant': df_facts_concomitant,
        'Complaint': df_facts_complaint,
        'Anamnesis': df_facts_anamnesis
    }
    add_id(df_id, sheets.values())

    create_excel(sheets, 'epicrises_extract.xlsx')

    print(f'Готово. Время выполнения: {datetime.now() - start_time}')
