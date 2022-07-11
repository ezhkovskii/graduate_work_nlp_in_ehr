import os
import logging

import pandas as pd

from parse_epicrise import EpicriseHTML, EpicriseType

PATH_EPICRISES = "./epicrises/"


def skip(html_doc: str) -> bool:
    """
    Пропускаем файл, если он не подходит
    """
    # Проверка на этапный эпикриз
    if EpicriseType.stage.value in html_doc:
        return True
    
    return False
    

def get_dataset(epicrises: list[str]) -> pd.DataFrame:
    """
    Создание датасета из эпикризов
    """
    data_for_dataset = []  # будущий датасет
    cnt_skipped = 0  # пропускаемые эпикризы
    for ind, epicrise in enumerate(epicrises):
        with open(PATH_EPICRISES + epicrise, 'r', encoding='utf-8') as file:
            logging.info(f'{ind + 1}: {epicrise}')
            html_doc = file.read()    
            
        if skip(html_doc):
            logging.info(f'{ind + 1}: {epicrise} пропускаем')
            cnt_skipped += 1
            continue
        
        data = EpicriseHTML(html_doc).get_result()
        data['filename'] = epicrise
        
        data_for_dataset.append(data)

    dataframe = pd.DataFrame(data_for_dataset)

    return dataframe, cnt_skipped


def main() -> None:
    logging.basicConfig(level=logging.DEBUG)

    epicrises = next(os.walk(PATH_EPICRISES))[2]  # получаем названия всех файлов в папке
    dataset, cnt_skipped = get_dataset(epicrises)
    dataset.to_csv('epicrises_text.csv', index=False, encoding='utf-8')
    
    logging.info(f'Готово. Пропущено {cnt_skipped}')

if __name__ == '__main__':
    main()
