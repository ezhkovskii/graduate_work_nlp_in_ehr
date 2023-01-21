"""
Извлечение информации из колонки с анамнезом anamnesis
"""

from typing import List, Dict
from collections import defaultdict
import pandas as pd

from utils.preprocessing import preprocess
from utils.utils import Extractor, update, matches_extractor
from rules.column_anamnesis import ANAMNESIS


class ExtractionAnamnesis:
    """
    Класс для извлечение информации из раздела anamnesis
    """
    def __init__(self, texts: List[str]) -> None:
        self.texts = texts
        self.extractor = Extractor(ANAMNESIS)

    def __call__(self, *args, **kwargs) -> pd.DataFrame:
        clean_texts = self.preprocessing()
        facts = self.get_facts(clean_texts)
        df_facts = pd.DataFrame(facts)

        return df_facts

    def preprocessing(self) -> List[str]:
        """
        Предобработка текста
        """
        for index in range(len(self.texts)):
            if 'Состояние' in self.texts[index]:
                find_texts = self.texts[index].find('Состояние')
                self.texts[index] = self.texts[index][:find_texts] + ' ' + self.texts[index][find_texts:]
        clean_texts = [preprocess(text) for text in self.texts]

        return clean_texts

    @staticmethod
    def show_extract(texts: List[str]) -> None:
        """
        Вывод в консоль найденных сущностей (найденных лекарств и жалоб) в разделе анамнезе
        """
        extractor = Extractor(ANAMNESIS)
        for text in texts:
            facts_by_text = matches_extractor(extractor, text, True)
            main_fact = defaultdict(list)
            for fact in facts_by_text:
                update(main_fact, fact, ['medicaments', 'complaints'])
            print(dict(main_fact))

    def extraction_fact(self, text: str) -> Dict:
        """
        Извлечение найденных найденных сущностей  (лекарств и жалоб) из раздела анамнеза
        """
        try:
            facts_by_text = matches_extractor(self.extractor, text)
            main_fact = defaultdict(list)
            for fact in facts_by_text:
                update(main_fact, fact, ['medicaments', 'complaints'])
        except Exception:
            print(f'Text: {text}\nFacts: {facts_by_text}\nDict: {main_fact}')
            raise

        return main_fact

    def get_facts(self, texts: List[str]) -> List:
        """
        Возвращает список найденных сущностей из раздела анамнеза
        """
        facts = [self.extraction_fact(text) for text in texts]

        return facts
