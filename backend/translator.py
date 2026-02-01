from deep_translator import GoogleTranslator
from typing import Union, List

class NepaliTranslator:
    def __init__(self):
        self.translator = GoogleTranslator(source='en', target='ne')
    
    def translate_to_nepali(self, text: str) -> str:
        """Translate English text to Nepali"""
        if not text or not text.strip():
            return ""
        
        try:
            # Handle long text by splitting if needed (Google Translate has limits)
            if len(text) > 4500:
                # Split by sentences or paragraphs
                parts = text.split('. ')
                translated_parts = []
                for part in parts:
                    if part.strip():
                        translated = self.translator.translate(part.strip())
                        translated_parts.append(translated)
                return '. '.join(translated_parts)
            else:
                return self.translator.translate(text)
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original text if translation fails
    
    def translate_list(self, items: List[str]) -> List[str]:
        """Translate a list of strings to Nepali"""
        translated = []
        for item in items:
            try:
                translated.append(self.translate_to_nepali(item))
            except Exception as e:
                print(f"Error translating '{item}': {e}")
                translated.append(item)
        return translated
    
    def translate_medicine_data(self, medicine_data: dict) -> dict:
        """Translate medicine data structure to Nepali"""
        try:
            translated = {
                'Medicine_name': medicine_data.get('Medicine_name', ''),
                'Medicine_name_nepali': self.translate_to_nepali(medicine_data.get('Medicine_name', '')),
                'Uses': medicine_data.get('Uses', ''),
                'Uses_nepali': self.translate_to_nepali(medicine_data.get('Uses', '')),
                'Side_effects': medicine_data.get('Side_effects', []),
                'Side_effects_nepali': self.translate_list(medicine_data.get('Side_effects', []))
            }
            return translated
        except Exception as e:
            print(f"Error translating medicine data: {e}")
            # Return original data with empty translations
            return {
                'Medicine_name': medicine_data.get('Medicine_name', ''),
                'Medicine_name_nepali': '',
                'Uses': medicine_data.get('Uses', ''),
                'Uses_nepali': '',
                'Side_effects': medicine_data.get('Side_effects', []),
                'Side_effects_nepali': []
            }
