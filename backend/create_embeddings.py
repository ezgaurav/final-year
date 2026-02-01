"""
Script to pre-create embeddings for all medicines.
Run this once after setting up the project:
    python create_embeddings.py
"""

from vector_db_handler import VectorDBHandler
import time

if __name__ == "__main__":
    print("Creating medicine embeddings...")
    print("This may take a few minutes on first run...")
    
    start_time = time.time()
    
    # Initialize handler (this will create embeddings if not exists)
    handler = VectorDBHandler(data_path="../data")
    
    # Test search
    print("\nTesting search...")
    results = handler.search("paracetamol", n_results=3)
    
    print("\nSearch results for 'paracetamol':")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['name']}")
    
    elapsed = time.time() - start_time
    print(f"\nCompleted in {elapsed:.2f} seconds")
    print(f"Total medicines in database: {handler.collection.count()}")
