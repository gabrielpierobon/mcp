#!/usr/bin/env python3
"""
Debug ChromaDB location and find where your test data actually went
"""

import chromadb
import os
import sys
from pathlib import Path

def check_chroma_locations():
    """Check multiple possible ChromaDB locations"""
    
    possible_locations = [
        "C:/Users/usuario/agent_playground/knowledge_base/chroma_db",
        "./knowledge_base/chroma_db", 
        "./chroma_db",
        "C:/Users/usuario/mcp/chroma_db",
        "C:/Users/usuario/mcp/knowledge_base/chroma_db"
    ]
    
    print("🔍 SEARCHING FOR CHROMADB INSTANCES")
    print("=" * 60)
    
    for location in possible_locations:
        print(f"\n📍 Checking: {location}")
        
        # Check if directory exists
        if not os.path.exists(location):
            print("   ❌ Directory doesn't exist")
            continue
        
        # Check if it has ChromaDB files
        path_obj = Path(location)
        chroma_files = list(path_obj.glob("*"))
        print(f"   📁 Found {len(chroma_files)} files/folders")
        
        if chroma_files:
            for file in chroma_files[:5]:  # Show first 5
                print(f"      - {file.name}")
            if len(chroma_files) > 5:
                print(f"      - ... and {len(chroma_files) - 5} more")
        
        # Try to connect and see what's there
        try:
            client = chromadb.PersistentClient(path=str(location))
            collections = client.list_collections()
            
            print(f"   ✅ Connected successfully!")
            print(f"   📚 Collections found: {len(collections)}")
            
            for col in collections:
                col_obj = client.get_collection(col.name)
                count = col_obj.count()
                print(f"      - {col.name}: {count} items")
                
                if count > 0:
                    # Get sample data
                    sample = col_obj.get(limit=1, include=['documents', 'metadatas'])
                    if sample['documents']:
                        source = sample['metadatas'][0].get('source_name') or sample['metadatas'][0].get('source_url', 'unknown')
                        preview = sample['documents'][0][:100]
                        print(f"        Sample: {source} - {preview}...")
            
            if collections:
                print(f"\n   🎯 THIS LOCATION HAS YOUR DATA!")
                
        except Exception as e:
            print(f"   ❌ Connection failed: {str(e)}")

def check_current_working_directory():
    """Check what directory we're running from"""
    print(f"\n🗂️  CURRENT WORKING DIRECTORY")
    print("=" * 60)
    print(f"Current directory: {os.getcwd()}")
    
    # Check for any ChromaDB directories in current location
    for item in os.listdir("."):
        if "chroma" in item.lower() or "knowledge" in item.lower():
            print(f"Found related directory: {item}")

def use_your_rag_tools():
    """Use your existing RAG tools to see where the data actually is"""
    print(f"\n🔧 USING YOUR RAG TOOLS")
    print("=" * 60)
    
    try:
        # Add tools to path
        sys.path.append('tools')
        from rag_knowledge_base_tool import _initialize_chroma, _load_config
        
        # Get config
        config = _load_config()
        db_path = config["storage"]["database_path"]
        print(f"Config says database is at: {db_path}")
        
        # Try to connect using your tools
        client = _initialize_chroma()
        collections = client.list_collections()
        
        print(f"✅ Your RAG tools connected successfully!")
        print(f"📚 Collections found: {len(collections)}")
        
        for col in collections:
            col_obj = client.get_collection(col.name)
            count = col_obj.count()
            print(f"   - {col.name}: {count} items")
            
            if count > 0:
                print(f"     🎯 FOUND DATA IN {col.name}!")
                
    except Exception as e:
        print(f"❌ Error using RAG tools: {str(e)}")

if __name__ == "__main__":
    check_current_working_directory()
    check_chroma_locations()
    use_your_rag_tools()
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("1. Use the location that shows 'FOUND DATA' above")
    print("2. Update browse_chroma_db.py with the correct path")
    print("3. Or use your existing RAG tools: get_kb_stats(), list_kb_sources()")