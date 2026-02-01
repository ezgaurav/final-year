import chromadb
from chromadb.utils import embedding_functions
import json
import os

class VectorDBHandler:
    def __init__(self, data_path="../data"):
        # Initialize ChromaDB with persistent storage
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use sentence-transformers for embeddings (free, runs locally)
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
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
                # Create searchable document text
                side_effects_str = ", ".join(med["side_effects"]) if isinstance(med["side_effects"], list) else str(med["side_effects"])
                doc_text = f"{med['name']} {med['uses']} {side_effects_str}"
                
                documents.append(doc_text)
                metadatas.append({
                    "name": med["name"],
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
                search_results.append({
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
