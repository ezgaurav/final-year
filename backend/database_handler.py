import json
import os
from typing import Optional, Dict, List
from difflib import SequenceMatcher

# Try to import vector DB handler
try:
    from vector_db_handler import VectorDBHandler
    VECTOR_DB_AVAILABLE = True
except ImportError:
    VECTOR_DB_AVAILABLE = False

class DatabaseHandler:
    def __init__(self):
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.drug_data1 = {}
        self.drug_data2 = {}
        self.all_medicines = {}
        self.load_databases()
        
        # Initialize vector DB if available
        self.vector_db = None
        if VECTOR_DB_AVAILABLE:
            try:
                self.vector_db = VectorDBHandler(self.data_dir)
                print("Vector database initialized successfully")
            except Exception as e:
                print(f"Vector DB init failed, using fallback: {e}")
    
    def load_databases(self):
        """Load both drug database JSON files"""
        try:
            # Load drug_data.json
            data1_path = os.path.join(self.data_dir, 'drug_data.json')
            with open(data1_path, 'r', encoding='utf-8') as f:
                self.drug_data1 = json.load(f)
            
            # Load drug_data2.json
            data2_path = os.path.join(self.data_dir, 'drug_data2.json')
            with open(data2_path, 'r', encoding='utf-8') as f:
                self.drug_data2 = json.load(f)
            
            # Combine both databases
            self.all_medicines = {**self.drug_data1, **self.drug_data2}
            
            print(f"Loaded {len(self.drug_data1)} medicines from drug_data.json")
            print(f"Loaded {len(self.drug_data2)} medicines from drug_data2.json")
            print(f"Total medicines in database: {len(self.all_medicines)}")
            
        except Exception as e:
            print(f"Error loading databases: {e}")
    
    def search_medicine(self, query: str) -> List[Dict]:
        """Search for medicines - uses vector DB if available, fallback to fuzzy"""
        # Try vector search first
        if self.vector_db:
            try:
                results = self.vector_db.search(query, n_results=5)
                if results:
                    return [{"key": r["data"].get("Medicine_name", ""), "data": r["data"], "match_score": 1 - r.get("score", 0)} for r in results]
            except Exception as e:
                print(f"Vector search failed: {e}")
        
        # Fallback to existing fuzzy search
        return self._fuzzy_search(query)
    
    def _fuzzy_search(self, query: str) -> List[Dict]:
        """Original fuzzy search method as fallback"""
        query_lower = query.lower()
        results = []
        
        for key, value in self.all_medicines.items():
            medicine_name = value.get('Medicine_name', '').lower()
            
            # Exact match
            if query_lower in medicine_name or medicine_name in query_lower:
                results.append({
                    'key': key,
                    'data': value,
                    'match_score': 1.0
                })
            # Fuzzy match
            elif self.similarity_ratio(query_lower, medicine_name) > 0.6:
                results.append({
                    'key': key,
                    'data': value,
                    'match_score': self.similarity_ratio(query_lower, medicine_name)
                })
        
        # Sort by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results[:10]  # Return top 10 results
    
    def get_medicine_by_name(self, name: str) -> Optional[Dict]:
        """Get medicine details by exact key or fuzzy match"""
        # Try exact key match
        if name in self.all_medicines:
            return self.all_medicines[name]
        
        # Try fuzzy search
        results = self.search_medicine(name)
        if results:
            return results[0]['data']
        
        return None
    
    def similarity_ratio(self, str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def get_all_medicine_names(self) -> List[str]:
        """Get list of all medicine names"""
        return [v.get('Medicine_name', '') for v in self.all_medicines.values()]
    
    def get_medicine_info(self, detected_text: Dict) -> Optional[Dict]:
        """
        Get medicine info based on detected text from YOLO
        detected_text should contain: brand_name, dosage, generic_name
        """
        brand_name = detected_text.get('brand_name', '')
        generic_name = detected_text.get('generic_name', '')
        dosage = detected_text.get('dosage', '')
        
        # Try to find medicine using brand name first
        if brand_name:
            result = self.get_medicine_by_name(brand_name)
            if result:
                return result
        
        # Try generic name
        if generic_name:
            result = self.get_medicine_by_name(generic_name)
            if result:
                return result
        
        # Try combined search
        combined = f"{brand_name} {dosage} {generic_name}".strip()
        if combined:
            results = self.search_medicine(combined)
            if results:
                return results[0]['data']
        
        return None
