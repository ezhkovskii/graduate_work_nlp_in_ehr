import enum
from bs4 import BeautifulSoup


class EpicriseType(enum.Enum):
    """
    Типы эпикризов
    """
    end = 'ВЫПИСНОЙ ЭПИКРИЗ'
    stage = 'ЭТАПНЫЙ ЭПИКРИЗ'
    justification = 'ОБОСНОВАНИЕ ДИАГНОЗА'
    

class EpicriseHTML:
    """
    Класс Эпикриз.
    Получает строку с html кодом полученную из file.read(),
    с помощью BeautifulSoup парсим необходимые данные,
    добавляем данные из html в словарь
    """
    
    def __init__(self, html_doc: str) -> None:
        self._soup = BeautifulSoup(html_doc, 'html.parser')
        self._data = {}
        self._type_epicrise = self._get_type_epicrise()
        
    def _get_type_epicrise(self):
        for type in EpicriseType:
            if type.value in self._soup.text:
                return type.name
    
    def get_result(self) -> dict:
        """
        Парсинг html и возврат словаря с данными из html
        """
    
        self._parse_epicrise()
        
        return self._data
    
    def _parse_epicrise(self):
        self._add_diagnosis()
        self._add_complaint()
        self._add_anamnesis()
        self._add_clinical_research()
        self._add_consultation()
        self._add_treatment()
        self._add_recommendations()
        self._add_status_end()
        self._add_disease_outcome()

    def _add_complaint(self):
        """
        Жалобы пациента при поступлении
        """
        data_complaint = self._soup.find('div', class_='template-block-data', id='data_complaint')
        self._data['complaint'] = data_complaint.text.strip() if data_complaint else None

    def _add_anamnesis(self):
        """
        Анамнез настоящего заболевания
        """
        data_anamnesmorbi = self._soup.find('div', class_='template-block-data', id='data_anamnesmorbi')
        self._data['anamnesis'] = data_anamnesmorbi.text.strip() if data_anamnesmorbi else None
        
        # Клинической картины заболевания
        if self._type_epicrise == EpicriseType.justification.name:
            data_objectivestatus = self._soup.find('div', class_='template-block-data', id='data_objectivestatus')
            if data_objectivestatus:
                self._data['anamnesis'] += f'\n {data_anamnesmorbi.text.strip()}'
        
    
    def _add_clinical_research(self):
        """
        Данные клинико-инструментальных исследований
        """
        data_clinical = self._soup.find_all('div', class_='template-block-data', id='data_autoname62')
        self._data['clinical_research'] = data_clinical[len(data_clinical)-1].text.strip() if data_clinical else None
       
    def  _add_consultation(self):
        """
        Консультирован
        """
        data_consultation = self._soup.find('div', class_='template-block-data', id='data_autoname73')
        self._data['consultation'] = data_consultation.text.strip() if data_consultation else None
        
    def _add_treatment(self):
        """
        Проведенное лечение
        """
        if self._type_epicrise == EpicriseType.justification.name:
            self._data['treatment'] = None
            return
        
        data_treatment = self._soup.find('div', class_='template-block-data', id='data_autoname1')
        self._data['treatment'] = data_treatment.text.strip() if data_treatment else None
        
        # В некоторых выписных эпикризах под id=data_autoname1 записаны персональные данные, а лечение записано в data_TreatmentPlan
        if self._data['treatment'] and 'ФИО' in self._data['treatment']:
            data_treatment = self._soup.find('div', class_='template-block-data', id='data_TreatmentPlan')
            self._data['treatment'] = data_treatment.text.strip() if data_treatment else None
    
    def _add_recommendations(self):
        """
        При выписке даны рекомендации
        """
        data_recommendations = self._soup.find('div', class_='template-block-data', id='data_recommendations')
        self._data['recommendations'] = data_recommendations.text.strip() if data_recommendations else None
        
        if self._data['recommendations'] is None:
            data_recommendations = self._soup.find('div', class_='template-block-data', id='data_edification')
            self._data['recommendations'] = data_recommendations.text.strip() if data_recommendations else None
        
    def _add_diagnosis(self):
        """
        Диагноз основной, осложнение и сопутствующий
        """
        if self._type_epicrise == EpicriseType.justification.name:
            data_diagnosis_89 = self._soup.find('div', class_='template-block-data', id='data_autoname89')
            data_diagnosis_50 = self._soup.find('div', class_='template-block-data', id='data_autoname50')
            data_diagnosis_74 = self._soup.find('div', class_='template-block-data', id='data_autoname74')
            
            self._data['diagnosis'] = ''
            if data_diagnosis_89:
                self._data['diagnosis'] += ' ' + data_diagnosis_89.text.strip()
            if data_diagnosis_50:
                self._data['diagnosis'] += ' ' + data_diagnosis_50.text.strip()
            if data_diagnosis_74:
                self._data['diagnosis'] += ' ' + data_diagnosis_74.text.strip()
            
            if not self._data['diagnosis']:
                self._data['diagnosis'] = None
            
            return        
        
        data_diagnosis = self._soup.find('div', class_='template-block-data', id='data_diagnos')
        self._data['diagnosis'] = data_diagnosis.text.strip() if data_diagnosis else None
        
    
    def _add_status_end(self):
        """
        Состояние при выписке
        """
        text = 'Состояние при выписке'
        data_status_end = self._soup.find(lambda tag:tag.name == 'b' and text in tag.text)
        self._data['status_end'] = data_status_end.next_sibling.text.strip() if data_status_end else None
    
    def _add_disease_outcome(self):
        """
        Исход заболевания
        """
        text = 'Исход заболевания'
        data_disease_outcome = self._soup.find(lambda tag: tag.name == 'b' and text in tag.text)
        self._data['disease_outcome'] = data_disease_outcome.next_sibling.text.strip() if data_disease_outcome else None
