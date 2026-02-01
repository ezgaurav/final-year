import chromadb
import json
import os
import hashlib
import re
from typing import List
from collections import Counter

class SimpleEmbeddingFunction:
    """Simple embedding function that works offline using word-based similarity"""
    
    def __init__(self):
        # Common medicine-related words for better matching
        self.common_words = {
            'tablet', 'capsule', 'syrup', 'mg', 'ml', 'injection', 'cream', 'gel',
            'suspension', 'drops', 'ointment', 'lotion', 'solution', 'powder'
        }
    
    def name(self) -> str:
        """Return the name of this embedding function"""
        return "simple_word_embedding"
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for input texts"""
        embeddings = []
        for text in input:
            embedding = self._text_to_embedding(text)
            embeddings.append(embedding)
        return embeddings
    
    def embed_query(self, input: List[str]) -> List[List[float]]:
        """Alias for __call__ to support query embedding"""
        return self.__call__(input)
    
    def _text_to_embedding(self, text: str, dim: int = 512) -> List[float]:
        """Convert text to an embedding vector using word-based approach"""
        # Normalize text
        text = text.lower()
        words = re.findall(r'\w+', text)
        
        # Create embedding vector
        embedding = [0.0] * dim
        
        # Get word frequencies
        word_freq = Counter(words)
        
        # Assign each unique word to positions in the embedding
        for word, freq in word_freq.items():
            # Skip very common words
            if word in self.common_words:
                # Give less weight to common words
                weight = 0.3 * freq
            else:
                # Give more weight to specific words (like medicine names)
                weight = 1.0 * freq
            
            # Hash word to multiple positions for better distribution
            for i in range(5):  # Use 5 hash functions
                hash_val = int(hashlib.md5(f"{word}_{i}".encode()).hexdigest(), 16)
                idx = hash_val % dim
                embedding[idx] += weight
        
        # Normalize the embedding
        magnitude = sum(x * x for x in embedding) ** 0.5
        if magnitude > 0:
            embedding = [x / magnitude for x in embedding]
        
        return embedding

class VectorDBHandler:
    def __init__(self, data_path="../data"):
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use custom embedding function (works offline)
        self.embedding_function = SimpleEmbeddingFunction()
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="medicines",
            embedding_function=self.embedding_function,
            metadata={"description": "Medicine database with embeddings"}
        )
        
        self.data_path = data_path
        
        # Load data if collection is empty
        if self.collection.count() == 0:
            self.load_medicines_to_vector_db()
    
    def load_medicines_to_vector_db(self):
        """Load all medicines from JSON files into ChromaDB"""
        medicines = []
        
        # Load drug_data.json
        drug_data_path = os.path.join(self.data_path, "drug_data.json")
        if os.path.exists(drug_data_path):
            with open(drug_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key, value in data.items():
                    medicines.append({
                        "id": key,
                        "name": value.get("Medicine_name", key),
                        "uses": value.get("Uses", ""),
                        "side_effects": value.get("Side_effects", []),
                        "data": value
                    })
        
        # Load drug_data2.json
        drug_data2_path = os.path.join(self.data_path, "drug_data2.json")
        if os.path.exists(drug_data2_path):
            with open(drug_data2_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for key, value in data.items():
                    if key not in [m["id"] for m in medicines]:  # Avoid duplicates
                        medicines.append({
                            "id": key,
                            "name": value.get("Medicine_name", key),
                            "uses": value.get("Uses", ""),
                            "side_effects": value.get("Side_effects", []),
                            "data": value
                        })
        
        # Add to ChromaDB in batches
        batch_size = 500
        for i in range(0, len(medicines), batch_size):
            batch = medicines[i:i+batch_size]
            
            documents = []
            metadatas = []
            ids = []
            
            for med in batch:
                # Create searchable document text - include both key and name
                # The key often contains the full medicine name including ingredients
                side_effects_str = ", ".join(med["side_effects"]) if isinstance(med["side_effects"], list) else str(med["side_effects"])
                doc_text = f"{med['id']} {med['name']} {med['uses']} {side_effects_str}"
                
                documents.append(doc_text)
                metadatas.append({
                    "name": med["name"] if med["name"].strip() else med["id"],
                    "uses": med["uses"],
                    "side_effects": side_effects_str,
                    "raw_data": json.dumps(med["data"])
                })
                ids.append(med["id"])
            
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        
        print(f"Loaded {len(medicines)} medicines into ChromaDB")
    
    def search(self, query, n_results=5):
        """Search medicines using semantic similarity"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        search_results = []
        if results and results['metadatas']:
            for i, metadata in enumerate(results['metadatas'][0]):
                # Get the ID (key) from results
                key = results['ids'][0][i] if results['ids'] else ""
                search_results.append({
                    "key": key,
                    "name": metadata.get("name", ""),
                    "uses": metadata.get("uses", ""),
                    "side_effects": metadata.get("side_effects", "").split(", "),
                    "data": json.loads(metadata.get("raw_data", "{}")),
                    "score": results['distances'][0][i] if results['distances'] else 0
                })
        
        return search_results
    
    def get_medicine_by_name(self, name):
        """Get exact medicine by name"""
        results = self.search(name, n_results=1)
        if results:
            return results[0]["data"]
        return None
