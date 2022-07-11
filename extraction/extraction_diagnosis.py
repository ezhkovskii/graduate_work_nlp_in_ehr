"""
Извлечение информации из колонки diagnosis
"""

from typing import List, Tuple, Dict
from collections import namedtuple, defaultdict
import re
from multiprocessing import Process, Manager

import pandas as pd
from pandas import DataFrame

from utils.preprocessing import preprocess
from utils.utils import Extractor, update, matches_extractor
from rules.column_diagnosis import MAIN_DIAGNOSIS, СOMPLICATION_DIAGNOSIS, CONCOMITANT_DIAGNOSIS


class ExtractionDiagnosis:
    """
    Класс для извлечения основного диагноза, осложнений и сопутствующих болезней.
    Предобработка, разделение текста диагноза на основной, осложнение и сопутствующий.
    Извлечение из трех разделов информации тремя процессами.
    """
    def __init__(self, diagnosis: List[str]) -> None:
        self.diagnosis = diagnosis

    def __call__(self, *args, **kwargs) -> Tuple[DataFrame, DataFrame, DataFrame]:
        clean_texts = self.preprocessing()
        main_texts, complication_texts, concomitant_texts = self.split_texts(clean_texts)

        facts_main, facts_complication, facts_concomitant = self.get_facts(
            (main_texts, complication_texts, concomitant_texts)
        )

        df_facts_main = pd.DataFrame(facts_main)
        df_facts_complication = pd.DataFrame(facts_complication)
        df_facts_concomitant = pd.DataFrame(facts_concomitant)

        return df_facts_main, df_facts_complication, df_facts_concomitant
    
    def preprocessing(self) -> List[str]:
        """
        Предобработка текста
        """
        for index in range(len(self.diagnosis)):
            if 'U07.2' in self.diagnosis[index]:
                find_diagnosis = self.diagnosis[index].find('U07.2')
                self.diagnosis[index] = self.diagnosis[index][:find_diagnosis + 5] + ' ' + self.diagnosis[index][find_diagnosis + 5:]
                
            if 'среднетяжелая' in self.diagnosis[index]:
                self.diagnosis[index] = self.diagnosis[index].replace('среднетяжелая', 'средне-тяжелая')
    
        clean_texts = [preprocess(text) for text in self.diagnosis]
        
        return clean_texts

    @staticmethod
    def split_texts(clean_texts: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Разделение колонки diagnosis на подразделы
        Основной, Осложение и Сопутствующий
        """
        Diagnosis_text = namedtuple('Diagnosis', 'ind main complication concomitant', defaults=[None, '', '', ''])
        split_text = []
        for ind, text in enumerate(clean_texts):
            _diagnosis =  Diagnosis_text(ind, *re.split('Соп|Осл', text, maxsplit=2))
            split_text.append(_diagnosis)

        main_texts = [text.main for text in split_text]
        complication_texts = [text.complication for text in split_text]
        concomitant_texts = [text.concomitant for text in split_text]
        
        for ind in range(len(concomitant_texts)):
            concomitant_texts[ind] = re.sub('утствующий:', '', concomitant_texts[ind])
            concomitant_texts[ind] = re.sub('утствующие:', '', concomitant_texts[ind])
            
        for ind in range(len(complication_texts)):
            complication_texts[ind] = re.sub('ожнение:', '', complication_texts[ind])
            
        return main_texts, complication_texts, concomitant_texts

    @staticmethod
    def extract_main_diagnosis(texts: List[str], return_dict: Dict) -> None:
        """
        Извлечение из основного подраздела
        """
        extractor = Extractor(MAIN_DIAGNOSIS)
        facts = []
        for text in texts:
            try:
                facts_by_text = matches_extractor(extractor, text)
                main_fact = defaultdict(list)
                for fact in facts_by_text:
                    update(main_fact, fact, ['diseases'])

                if main_fact.get('form'):
                    new_form = str(main_fact['form']['start'])
                    if main_fact['form'].get('stop'):
                        new_form += f"-{str(main_fact['form']['stop'])}"
                    main_fact['form'] = new_form
            except Exception:
                print(f'Text: {text}\nFacts: {facts_by_text}\nDict: {main_fact}')
                raise

            facts.append(main_fact)

        return_dict['facts_main'] = facts

    @staticmethod
    def extract_complication_diagnosis(texts: List[str], return_dict: Dict) -> None:
        """
        Осложнение
        """
        extractor = Extractor(СOMPLICATION_DIAGNOSIS)
        facts = []
        for text in texts:
            try:
                facts_by_text = matches_extractor(extractor, text)
                main_fact = defaultdict(list)
                for fact in facts_by_text:
                    update(main_fact, fact, ['diseases'])

                if main_fact.get('form'):
                    new_form = str(main_fact['form']['start'])
                    if main_fact['form'].get('stop'):
                        new_form += f"-{str(main_fact['form']['stop'])}"
                    main_fact['form'] = new_form

                if main_fact.get('respiratory_failure'):
                    value = main_fact['respiratory_failure']['value']
                    if isinstance(value, int):
                        respiratory_failure = str(value)
                    elif isinstance(value, dict):
                        respiratory_failure = str(value['start'])
                        respiratory_failure += f"-{str(value['stop'])}"
                    else:
                        respiratory_failure = None
                        #raise ValueError(f"respiratory_failure type: {type(value)}, value: {value}")
                        print(f'Ошибка. respiratory_failure type: {type(value)}, value: {value}')
                        print(f'Text: {text}\nFacts: {facts_by_text}\nDict: {main_fact}')

                    main_fact['respiratory_failure'] = respiratory_failure
            except Exception:
                print(f'Text: {text}\nFacts: {facts_by_text}\nDict: {main_fact}')
                raise

            facts.append(main_fact)

        return_dict['facts_complication'] = facts

    @staticmethod
    def extract_concomitant_diagnosis(texts: List[str], return_dict: Dict) -> None:
        """
        Сопутствующий
        """
        extractor = Extractor(CONCOMITANT_DIAGNOSIS)
        facts = []
        for text in texts:
            try:
                facts_by_text = matches_extractor(extractor, text)
                main_fact = defaultdict(list)
                for fact in facts_by_text:
                    update(main_fact, fact, ['diseases', 'info'])
            except Exception:
                print(f'Text: {text}\nFacts: {facts_by_text}\nDict: {main_fact}')
                raise

            facts.append(main_fact)

        return_dict['facts_concomitant'] = facts
    
    def get_facts(self, texts: Tuple) -> Tuple[Dict, Dict, Dict]:
        """
        Запуск извлечения информации из текстов
        """
        return_dict = Manager().dict()
        jobs = []
        funcs = (self.extract_main_diagnosis, self.extract_complication_diagnosis, self.extract_concomitant_diagnosis)
        for func, text in zip(funcs, texts):
            proc = Process(target=func, args=(text, return_dict))
            jobs.append(proc)
            proc.start()

        for proc in jobs:
            proc.join()

        return return_dict['facts_main'], return_dict['facts_complication'], return_dict['facts_concomitant']


