#!/usr/bin/env python3
"""
Browse ChromaDB Knowledge Base
Simple tool to explore all collections, sources, and chunks in your RAG database.
"""

import chromadb
import json
from pathlib import Path
from datetime import datetime

def browse_knowledge_base():
    """Browse and display all content in the ChromaDB knowledge base"""
    
    # Connect to your ChromaDB (CORRECTED PATH)
    db_path = "./knowledge_base/chroma_db"  # Relative to MCP directory
    client = chromadb.PersistentClient(path=db_path)
    
    print("=" * 80)
    print("🔍 BROWSING RAG KNOWLEDGE BASE")
    print("=" * 80)
    print(f"📍 Database location: {db_path}")
    print(f"🕒 Browsed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get all collections
    try:
        collections = client.list_collections()
        print(f"\n📚 Found {len(collections)} collections:")
        
        for i, collection_obj in enumerate(collections, 1):
            collection_name = collection_obj.name
            print(f"\n{'-' * 60}")
            print(f"📁 COLLECTION {i}: {collection_name}")
            print(f"{'-' * 60}")
            
            # Get the collection
            collection = client.get_collection(collection_name)
            
            # Get all data from this collection
            all_data = collection.get(include=['documents', 'metadatas'])
            
            num_chunks = len(all_data['documents'])
            print(f"📊 Total chunks in '{collection_name}': {num_chunks}")
            
            if num_chunks == 0:
                print("   ⚠️  Collection is empty")
                continue
            
            # Analyze sources
            sources = {}
            for j, (doc, meta) in enumerate(zip(
                all_data['documents'], 
                all_data['metadatas']
            )):
                source = meta.get('source_url') or meta.get('source_name', 'unknown')
                source_type = meta.get('source_type', 'unknown')
                
                if source not in sources:
                    sources[source] = {
                        'chunks': [],
                        'type': source_type,
                        'total_chars': 0,
                        'timestamps': []
                    }
                
                sources[source]['chunks'].append({
                    'id': f"chunk_{j}",
                    'content': doc,
                    'length': len(doc),
                    'metadata': meta
                })
                sources[source]['total_chars'] += len(doc)
                
                if meta.get('timestamp'):
                    sources[source]['timestamps'].append(meta['timestamp'])
            
            # Display sources
            print(f"🗂️  Sources in this collection: {len(sources)}")
            
            for source_name, source_data in sources.items():
                print(f"\n   📄 SOURCE: {source_name}")
                print(f"      Type: {source_data['type']}")
                print(f"      Chunks: {len(source_data['chunks'])}")
                print(f"      Total characters: {source_data['total_chars']:,}")
                
                if source_data['timestamps']:
                    latest = max(source_data['timestamps'])
                    print(f"      Latest update: {latest}")
                
                # Show first few chunks with preview
                print(f"      📝 Chunks:")
                for k, chunk in enumerate(source_data['chunks'][:3]):  # Show first 3 chunks
                    content_preview = chunk['content'][:100].replace('\n', ' ')
                    print(f"         {k+1}. [{chunk['length']} chars] {content_preview}...")
                
                if len(source_data['chunks']) > 3:
                    print(f"         ... and {len(source_data['chunks']) - 3} more chunks")
    
    except Exception as e:
        print(f"❌ Error browsing database: {str(e)}")
        return
    
    print(f"\n{'=' * 80}")
    print("✅ Database browsing complete!")
    print("💡 Use search_kb() to find specific content")
    print("💡 Use get_kb_stats() for detailed statistics")
    print("=" * 80)

def show_specific_collection(collection_name: str, show_full_content: bool = False):
    """Show detailed content of a specific collection"""
    
    db_path = "./knowledge_base/chroma_db"  # CORRECTED PATH
    client = chromadb.PersistentClient(path=db_path)
    
    try:
        collection = client.get_collection(collection_name)
        all_data = collection.get(include=['documents', 'metadatas'])
        
        print(f"\n📁 DETAILED VIEW: {collection_name}")
        print("=" * 60)
        
        for i, (doc, meta) in enumerate(zip(
            all_data['documents'], 
            all_data['metadatas']
        ), 1):
            print(f"\n🔖 CHUNK {i}")
            print(f"   Source: {meta.get('source_url') or meta.get('source_name', 'unknown')}")
            print(f"   Type: {meta.get('source_type', 'unknown')}")
            print(f"   Length: {len(doc)} characters")
            print(f"   Timestamp: {meta.get('timestamp', 'unknown')}")
            
            if show_full_content:
                print(f"   Content:\n{doc}")
            else:
                preview = doc[:200].replace('\n', ' ')
                print(f"   Preview: {preview}...")
            
            print("-" * 40)
            
    except Exception as e:
        print(f"❌ Collection '{collection_name}' not found or error: {str(e)}")

if __name__ == "__main__":
    # Browse all collections
    browse_knowledge_base()
    
    # Uncomment to see detailed view of specific collections:
    # show_specific_collection("search_test", show_full_content=True)
    # show_specific_collection("test_collection", show_full_content=False)
    # show_specific_collection("ai_knowledge", show_full_content=True)
    # show_specific_collection("integration_test", show_full_content=True)