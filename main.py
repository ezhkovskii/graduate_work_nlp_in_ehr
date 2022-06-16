from datetime import datetime

import pandas as pd

from extraction.extraction_diagnosis import ExtractionDiagnosis
from extraction.extraction_complaint import ExtractionComplaints


COUNT_ROWS = 100


if __name__ == "__main__":
    print(f'Запуск. Обработка текстов - {COUNT_ROWS} шт.')
    start_time = datetime.now()

    df = pd.read_csv('epicrises_text.csv')
    df_clean = df.copy()
    df_clean = df_clean.fillna('')

    df_filename = df_clean.filename.copy()

    df_diagnosis = list(df_clean.diagnosis.copy())[:COUNT_ROWS]
    extraction = ExtractionDiagnosis(df_diagnosis)
    df_facts_main, df_facts_complication, df_facts_concomitant = extraction()

    df_complaint = list(df_clean.complaint.copy())[:COUNT_ROWS]
    extraction = ExtractionComplaints(df_complaint)
    df_facts_complaint = extraction()

    for df_facts in (df_facts_main, df_facts_complication, df_facts_concomitant, df_facts_complaint):
        df_facts['filename'] = df_filename

    sheets = {
        'Main': df_facts_main,
        'Complication': df_facts_complication,
        'Concomitant': df_facts_concomitant,
        'Complaint': df_facts_complaint
        }

    writer = pd.ExcelWriter('epicrises_extract.xlsx', engine='xlsxwriter')
    for sheet_name in sheets.keys():
        sheets[sheet_name].to_excel(writer, sheet_name=sheet_name, index=False)
    writer.save()

    print('Готово')
    print(f'Время выполнения: {datetime.now() - start_time}')
