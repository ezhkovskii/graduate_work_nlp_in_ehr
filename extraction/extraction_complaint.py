"""
Извлечение информации из колонки с жалобами complaints
"""

from typing import List, Tuple, Dict
from collections import namedtuple, defaultdict
import re
from multiprocessing import Process, Manager, Pool

import pandas as pd

from utils.preprocessing import preprocess
from utils.utils import Extractor, matches_extractor, update
from rules.column_complaints import COMPLAINT, complaints


class ExtractionComplaints:
    """
    Класс для извлечения информации из раздела с жалобами
    """
    def __init__(self, texts: List[str]):
        self.texts = texts
        self.extractor = Extractor(COMPLAINT)

    def __call__(self, *args, **kwargs) -> pd.DataFrame:
        clean_texts = [preprocess(text) for text in self.texts]
        facts = self.get_facts(clean_texts)

        df_facts = pd.DataFrame(columns=complaints.keys())
        for fact in facts:
            #df_facts = pd.concat([df_facts, fact], ignore_index=True, axis=0)
            df_facts = df_facts.append(fact, ignore_index=True)

        return df_facts

    def get_facts(self, texts: List[str]) -> List:
        """
        Возвращает список найденных сущностей
        """
        facts = [self.extraction_fact(text) for text in texts]

        return facts

    def extraction_fact(self, text: str) -> Dict:
        """
        Извлечение сущностей из текста раздела с жалобами.
        """
        try:
            facts_by_text = matches_extractor(self.extractor, text)
            main_fact = defaultdict(list)
            for fact in facts_by_text:
                update(main_fact, fact)

            # Если есть температура и в тексте написано число, то нужно его вытащить.
            # Если температура написана как диапазон, то берем среднее значение.
            if main_fact.get('temperature') and isinstance(main_fact['temperature'], dict):
                if isinstance(main_fact['temperature']['value'], dict):
                    aver = (main_fact['temperature']['value']['start'] + main_fact['temperature']['value']['stop']) / 2
                    main_fact['temperature_value'] = str(aver)
                else:
                    main_fact['temperature_value'] = str(main_fact['temperature']['value'])
                main_fact['temperature'] = True

            for key in main_fact.keys():
                if key not in ('temperature_value',):
                    main_fact[key] = True
        except Exception:
            print(f'Text: {text}\nFacts: {facts_by_text}\nDict: {main_fact}')
            raise

        return main_fact

