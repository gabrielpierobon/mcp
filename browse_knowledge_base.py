#!/usr/bin/env python3
"""
Knowledge Base Browser Script
Browse and display all entries in your RAG knowledge base with detailed metadata.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the current directory to Python path to import the RAG tool
sys.path.append(str(Path(__file__).parent))

from tools.rag_knowledge_base_tool import (
    _initialize_chroma, 
    _load_config, 
    suppress_stdout_stderr,
    CHROMADB_AVAILABLE,
    SENTENCE_TRANSFORMERS_AVAILABLE,
    LANGCHAIN_AVAILABLE
)

def print_header(title: str, char: str = "="):
    """Print a formatted header."""
    print(f"\n{char * 60}")
    print(f"{title.center(60)}")
    print(f"{char * 60}")

def print_subheader(title: str):
    """Print a formatted subheader."""
    print(f"\n{'─' * 40}")
    print(f"📄 {title}")
    print(f"{'─' * 40}")

def format_metadata(metadata: Dict[str, Any]) -> str:
    """Format metadata for display."""
    if not metadata:
        return "No metadata"
    
    lines = []
    
    # Core fields
    core_fields = ["source_name", "source_url", "source_type", "timestamp", "chunk_index", "chunk_length", "token_count"]
    
    for field in core_fields:
        if field in metadata:
            value = metadata[field]
            if field == "timestamp" and value:
                try:
                    # Format timestamp nicely
                    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                    value = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            lines.append(f"  {field}: {value}")
    
    # Custom fields
    custom_fields = {k: v for k, v in metadata.items() if k not in core_fields + ["collection", "total_chunks", "content_length"]}
    if custom_fields:
        lines.append("  Custom metadata:")
        for key, value in custom_fields.items():
            lines.append(f"    {key}: {value}")
    
    return "\n".join(lines)

def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text for display."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

async def browse_knowledge_base(
    collection_name: Optional[str] = None,
    show_content: bool = True,
    max_content_length: int = 200,
    show_metadata: bool = True,
    filter_source: Optional[str] = None
):
    """
    Browse all entries in the knowledge base.
    
    Args:
        collection_name: Specific collection to browse (None for all)
        show_content: Whether to show document content
        max_content_length: Maximum content length to display
        show_metadata: Whether to show metadata
        filter_source: Filter by source name/URL (partial match)
    """
    
    print_header("🔍 KNOWLEDGE BASE BROWSER")
    
    # Check dependencies
    if not all([CHROMADB_AVAILABLE, SENTENCE_TRANSFORMERS_AVAILABLE, LANGCHAIN_AVAILABLE]):
        missing = []
        if not CHROMADB_AVAILABLE:
            missing.append("chromadb")
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            missing.append("sentence-transformers")  
        if not LANGCHAIN_AVAILABLE:
            missing.append("langchain-text-splitters")
        
        print(f"❌ Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return
    
    try:
        # Initialize ChromaDB client using MCP server location
        with suppress_stdout_stderr():
            import chromadb
            from chromadb.config import Settings
            
            # Use MCP server database path directly
            mcp_db_path = "C:/Users/usuario/agent_playground/knowledge_base/chroma_db"
            
            client = chromadb.PersistentClient(
                path=mcp_db_path,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            config = _load_config()
        
        # Get collections
        collections = client.list_collections()
        
        if not collections:
            print("📭 No collections found in the knowledge base.")
            return
        
        collection_names = []
        if hasattr(collections[0], 'name'):
            collection_names = [col.name for col in collections]
        else:
            collection_names = collections  # Newer ChromaDB versions
        
        print(f"📚 Found {len(collection_names)} collection(s): {', '.join(collection_names)}")
        
        # Filter collections if specified
        if collection_name:
            if collection_name not in collection_names:
                print(f"❌ Collection '{collection_name}' not found.")
                print(f"Available collections: {', '.join(collection_names)}")
                return
            collection_names = [collection_name]
        
        total_entries = 0
        
        # Browse each collection
        for col_name in collection_names:
            print_subheader(f"Collection: {col_name}")
            
            try:
                collection = client.get_collection(col_name)
                
                # Get all data
                all_data = collection.get(include=['documents', 'metadatas'])
                
                documents = all_data.get('documents', [])
                metadatas = all_data.get('metadatas', [])
                ids = all_data.get('ids', [])  # IDs are returned by default
                
                if not documents:
                    print("  📭 No entries found in this collection.")
                    continue
                
                # Apply source filter if specified
                filtered_entries = []
                for i, (doc, meta, doc_id) in enumerate(zip(documents, metadatas, ids)):
                    if filter_source:
                        source = meta.get('source_name', '') + meta.get('source_url', '')
                        if filter_source.lower() not in source.lower():
                            continue
                    
                    filtered_entries.append((doc, meta, doc_id, i))
                
                if not filtered_entries:
                    if filter_source:
                        print(f"  📭 No entries found matching source filter: '{filter_source}'")
                    continue
                
                print(f"  📊 Found {len(filtered_entries)} entries")
                
                # Group by source for better organization
                sources = {}
                for doc, meta, doc_id, original_idx in filtered_entries:
                    source = meta.get('source_name') or meta.get('source_url', 'Unknown Source')
                    if source not in sources:
                        sources[source] = []
                    sources[source].append((doc, meta, doc_id, original_idx))
                
                # Display entries grouped by source
                for source, entries in sources.items():
                    print(f"\n  📄 Source: {source}")
                    print(f"     Chunks: {len(entries)}")
                    
                    for doc, meta, doc_id, original_idx in entries:
                        print(f"\n    🔹 Entry #{original_idx + 1} (ID: {doc_id})")
                        
                        if show_metadata and meta:
                            print("    📋 Metadata:")
                            print(format_metadata(meta))
                        
                        if show_content:
                            print("    📝 Content:")
                            content = truncate_text(doc, max_content_length)
                            # Indent content for better readability
                            indented_content = '\n'.join(f"       {line}" for line in content.split('\n'))
                            print(indented_content)
                        
                        print()  # Empty line between entries
                
                total_entries += len(filtered_entries)
                
            except Exception as e:
                print(f"  ❌ Error accessing collection '{col_name}': {e}")
        
        print_header(f"📊 SUMMARY: {total_entries} total entries browsed")
        
        # Show configuration info
        print(f"\n🔧 Configuration:")
        print(f"   Database path: {mcp_db_path}")
        print(f"   Embedding model: {config['embedding']['model_name']}")
        print(f"   Chunk size: {config['chunking']['chunk_size']}")
        
    except Exception as e:
        print(f"❌ Error browsing knowledge base: {e}")

async def main():
    """Main function with command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Browse Knowledge Base entries")
    parser.add_argument("--collection", "-c", help="Specific collection to browse")
    parser.add_argument("--no-content", action="store_true", help="Don't show document content")
    parser.add_argument("--no-metadata", action="store_true", help="Don't show metadata") 
    parser.add_argument("--max-length", "-l", type=int, default=200, help="Max content length to show")
    parser.add_argument("--filter-source", "-s", help="Filter by source name/URL (partial match)")
    parser.add_argument("--stats-only", action="store_true", help="Show only statistics")
    
    args = parser.parse_args()
    
    if args.stats_only:
        # Quick stats view
        print_header("📊 KNOWLEDGE BASE STATISTICS")
        try:
            with suppress_stdout_stderr():
                import chromadb
                from chromadb.config import Settings
                
                # Use MCP server database path directly
                mcp_db_path = "C:/Users/usuario/agent_playground/knowledge_base/chroma_db"
                
                client = chromadb.PersistentClient(
                    path=mcp_db_path,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
            
            collections = client.list_collections()
            collection_names = []
            if hasattr(collections[0], 'name'):
                collection_names = [col.name for col in collections]
            else:
                collection_names = collections
            
            total_entries = 0
            for col_name in collection_names:
                collection = client.get_collection(col_name)
                count = collection.count()
                total_entries += count
                print(f"📚 {col_name}: {count} entries")
            
            print(f"\n🎯 Total: {total_entries} entries across {len(collection_names)} collections")
            
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
    else:
        await browse_knowledge_base(
            collection_name=args.collection,
            show_content=not args.no_content,
            max_content_length=args.max_length,
            show_metadata=not args.no_metadata,
            filter_source=args.filter_source
        )

if __name__ == "__main__":
    asyncio.run(main()) 