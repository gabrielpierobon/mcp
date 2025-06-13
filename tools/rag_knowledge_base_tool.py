# tools/rag_knowledge_base_tool.py
from typing import Dict, Any, List, Optional
import os
import json
import importlib.util
from datetime import datetime
from pathlib import Path

# Check if RAG dependencies are available
CHROMADB_AVAILABLE = importlib.util.find_spec("chromadb") is not None
SENTENCE_TRANSFORMERS_AVAILABLE = importlib.util.find_spec("sentence_transformers") is not None
LANGCHAIN_AVAILABLE = importlib.util.find_spec("langchain_text_splitters") is not None

# Global variables for RAG components
_chroma_client = None
_embedding_model = None
_text_splitter = None
_config = None

# Configuration file path (in MCP server root)
CONFIG_FILE = "kb_config.json"
KNOWLEDGE_BASE_DIR = Path("C:/Users/usuario/agent_playground/knowledge_base")

def _get_config_path():
    """Get the path to the configuration file in the MCP server root directory."""
    # Get the directory where this script is located (tools/)
    current_dir = Path(__file__).parent
    # Go up one level to the MCP server root
    mcp_root = current_dir.parent
    return mcp_root / CONFIG_FILE

def _load_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    global _config
    if _config is not None:
        return _config
    
    config_path = _get_config_path()
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            _config = json.load(f)
    else:
        # Default configuration
        _config = {
            "version": "1.0.0",
            "embedding": {
                "model_name": "BAAI/bge-m3",
                "model_type": "sentence-transformers",
                "embedding_dimension": 1024,
                "normalize_embeddings": True
            },
            "chunking": {
                "chunk_size": 1000,
                "chunk_overlap": 100
            },
            "storage": {
                "database_path": str(KNOWLEDGE_BASE_DIR / "chroma_db"),
                "default_collection": "default"
            }
        }
        
        # Save default config to file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(_config, f, indent=4)
    
    return _config

def _initialize_chroma():
    """Initialize Chroma database client."""
    global _chroma_client
    if _chroma_client is not None:
        return _chroma_client
    
    if not CHROMADB_AVAILABLE:
        raise ImportError("ChromaDB not available. Install with: pip install chromadb")
    
    import chromadb
    from chromadb.config import Settings
    
    config = _load_config()
    db_path = config["storage"]["database_path"]
    
    # Ensure directory exists
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Initialize persistent client
    _chroma_client = chromadb.PersistentClient(
        path=db_path,
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    return _chroma_client

def _initialize_embedding_model():
    """Initialize embedding model."""
    global _embedding_model
    if _embedding_model is not None:
        return _embedding_model
    
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ImportError("sentence-transformers not available. Install with: pip install sentence-transformers")
    
    from sentence_transformers import SentenceTransformer
    
    config = _load_config()
    model_name = config["embedding"]["model_name"]
    
    print(f"INFO: Loading embedding model: {model_name}")
    _embedding_model = SentenceTransformer(model_name)
    
    return _embedding_model

def _initialize_text_splitter():
    """Initialize text splitter."""
    global _text_splitter
    if _text_splitter is not None:
        return _text_splitter
    
    if not LANGCHAIN_AVAILABLE:
        raise ImportError("langchain-text-splitters not available. Install with: pip install langchain-text-splitters")
    
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    
    config = _load_config()
    chunking_config = config["chunking"]
    
    _text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunking_config["chunk_size"],
        chunk_overlap=chunking_config["chunk_overlap"],
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    return _text_splitter

async def setup_knowledge_base() -> Dict[str, Any]:
    """
    Initialize the RAG knowledge base infrastructure.
    Creates directories, loads configuration, and tests all components.
    
    Returns:
        Dictionary with setup status and component information
    """
    print("INFO: Setting up RAG Knowledge Base infrastructure...")
    
    try:
        # Check dependencies
        missing_deps = []
        if not CHROMADB_AVAILABLE:
            missing_deps.append("chromadb")
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            missing_deps.append("sentence-transformers")
        if not LANGCHAIN_AVAILABLE:
            missing_deps.append("langchain-text-splitters")
        
        if missing_deps:
            return {
                "error": f"Missing dependencies: {', '.join(missing_deps)}",
                "install_command": f"pip install {' '.join(missing_deps)}",
                "status": "error"
            }
        
        # Create directory structure
        KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)
        (KNOWLEDGE_BASE_DIR / "chroma_db").mkdir(parents=True, exist_ok=True)
        
        # Load/create configuration
        config = _load_config()
        config_path = _get_config_path()
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        # Initialize components
        client = _initialize_chroma()
        embedding_model = _initialize_embedding_model()
        text_splitter = _initialize_text_splitter()
        
        # Test basic functionality
        # Create a test collection (handle both ChromaDB versions)
        try:
            test_collection = client.get_or_create_collection("setup_test")
        except Exception as e:
            print(f"WARNING: Collection creation issue: {str(e)}")
            # Try alternative approach for newer ChromaDB versions
            try:
                test_collection = client.create_collection("setup_test")
            except:
                # Collection might already exist
                test_collection = client.get_collection("setup_test")
        
        # Test embedding
        test_text = "This is a test document for RAG setup."
        test_embedding = embedding_model.encode([test_text])
        
        # Test chunking
        test_chunks = text_splitter.split_text("This is a longer test document. It should be split into chunks. Each chunk should maintain some context.")
        
        # Add test data
        test_collection.add(
            documents=[test_text],
            embeddings=test_embedding.tolist(),
            metadatas=[{"test": True, "timestamp": datetime.now().isoformat()}],
            ids=["test_doc_1"]
        )
        
        # Test query
        query_results = test_collection.query(
            query_embeddings=test_embedding.tolist(),
            n_results=1
        )
        
        # Clean up test collection (handle both ChromaDB versions)
        try:
            client.delete_collection("setup_test")
        except Exception as e:
            print(f"WARNING: Test cleanup issue: {str(e)}")
        
        # Get default collection ready (handle both ChromaDB versions)
        try:
            default_collection = client.get_or_create_collection(
                config["storage"]["default_collection"]
            )
        except Exception as e:
            print(f"WARNING: Default collection creation issue: {str(e)}")
            try:
                default_collection = client.create_collection(config["storage"]["default_collection"])
            except:
                default_collection = client.get_collection(config["storage"]["default_collection"])
        
        return {
            "status": "success",
            "message": "RAG Knowledge Base infrastructure setup complete",
            "config": {
                "knowledge_base_dir": str(KNOWLEDGE_BASE_DIR),
                "database_path": config["storage"]["database_path"],
                "embedding_model": config["embedding"]["model_name"],
                "chunk_size": config["chunking"]["chunk_size"],
                "chunk_overlap": config["chunking"]["chunk_overlap"]
            },
            "components": {
                "chroma_client": "initialized",
                "embedding_model": "loaded",
                "text_splitter": "configured",
                "default_collection": "ready"
            },
            "test_results": {
                "embedding_test": "passed",
                "chunking_test": f"generated {len(test_chunks)} chunks",
                "storage_test": "passed",
                "query_test": f"retrieved {len(query_results['documents'][0])} results"
            }
        }
        
    except Exception as e:
        print(f"ERROR: RAG setup failed: {str(e)}")
        return {
            "error": f"Setup failed: {str(e)}",
            "status": "error"
        }

async def get_kb_health() -> Dict[str, Any]:
    """
    Check the health status of the knowledge base infrastructure.
    
    Returns:
        Dictionary with health status of all components
    """
    print("INFO: Checking RAG Knowledge Base health...")
    
    try:
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {}
        }
        
        # Check dependencies
        health_status["components"]["dependencies"] = {
            "chromadb": CHROMADB_AVAILABLE,
            "sentence_transformers": SENTENCE_TRANSFORMERS_AVAILABLE,
            "langchain_text_splitters": LANGCHAIN_AVAILABLE
        }
        
        if not all(health_status["components"]["dependencies"].values()):
            health_status["status"] = "unhealthy"
            health_status["error"] = "Missing required dependencies"
            return health_status
        
        # Check configuration
        config = _load_config()
        health_status["components"]["configuration"] = "loaded"
        
        # Check database
        client = _initialize_chroma()
        try:
            # ChromaDB v0.6.0+ returns collection names as strings, not objects
            collections = client.list_collections()
            
            # In v0.6.0+, list_collections returns just names as strings
            if isinstance(collections, list):
                collection_names = collections  # Already strings in v0.6.0+
            else:
                collection_names = []
            
            health_status["components"]["database"] = {
                "status": "connected",
                "collections": len(collection_names),
                "collection_names": collection_names
            }
        except Exception as db_error:
            print(f"WARNING: Database collection listing issue: {str(db_error)}")
            # Still mark as connected if we can initialize client
            health_status["components"]["database"] = {
                "status": "connected_with_warnings",
                "collections": "unknown",
                "collection_names": [],
                "warning": str(db_error)
            }
        
        # Check embedding model
        embedding_model = _initialize_embedding_model()
        health_status["components"]["embedding_model"] = {
            "status": "loaded",
            "model_name": config["embedding"]["model_name"]
        }
        
        # Check text splitter
        text_splitter = _initialize_text_splitter()
        health_status["components"]["text_splitter"] = "configured"
        
        return health_status
        
    except Exception as e:
        print(f"ERROR: Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

async def add_url_to_kb(url: str, collection_name: str = "default", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Add URL content to the knowledge base by scraping and chunking it.
    
    Args:
        url: The URL to scrape and add
        collection_name: Collection to add content to
        metadata: Additional metadata to store with chunks
    
    Returns:
        Dictionary with ingestion results
    """
    print(f"INFO: Adding URL to knowledge base: {url}")
    
    try:
        # Initialize components
        client = _initialize_chroma()
        embedding_model = _initialize_embedding_model()
        text_splitter = _initialize_text_splitter()
        
        # Get or create collection
        collection = client.get_or_create_collection(collection_name)
        
        # Import crawl4ai here to avoid circular imports
        try:
            from tools.crawl4ai_tool import crawl_webpage
        except ImportError:
            return {
                "error": "crawl_webpage tool not available",
                "status": "error"
            }
        
        # Scrape the webpage
        print(f"INFO: Scraping webpage: {url}")
        scrape_result = await crawl_webpage(url, output_format="markdown")
        
        if "error" in scrape_result:
            return {
                "error": f"Failed to scrape URL: {scrape_result['error']}",
                "status": "error"
            }
        
        # Extract content
        content = scrape_result.get("markdown", "")
        if not content or len(content.strip()) < 50:
            return {
                "error": "No meaningful content extracted from URL",
                "status": "error"
            }
        
        # Chunk the content
        print(f"INFO: Chunking content ({len(content)} characters)")
        chunks = text_splitter.split_text(content)
        
        if not chunks:
            return {
                "error": "No chunks generated from content",
                "status": "error"
            }
        
        # Generate embeddings
        print(f"INFO: Generating embeddings for {len(chunks)} chunks")
        embeddings = embedding_model.encode(chunks, normalize_embeddings=True)
        
        # Prepare metadata for each chunk
        base_metadata = {
            "source_url": url,
            "source_type": "webpage",
            "timestamp": datetime.now().isoformat(),
            "collection": collection_name,
            "total_chunks": len(chunks),
            "content_length": len(content)
        }
        
        # Add user-provided metadata
        if metadata:
            base_metadata.update(metadata)
        
        # Create chunk-specific metadata
        chunk_metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_meta = base_metadata.copy()
            chunk_meta.update({
                "chunk_index": i,
                "chunk_length": len(chunk),
                "token_count": len(chunk.split())  # Rough token estimate
            })
            chunk_metadatas.append(chunk_meta)
        
        # Generate unique IDs for chunks
        chunk_ids = [f"{url}_{i}_{hash(chunk) % 100000}" for i, chunk in enumerate(chunks)]
        
        # Add to ChromaDB
        print(f"INFO: Storing {len(chunks)} chunks in collection '{collection_name}'")
        collection.add(
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=chunk_metadatas,
            ids=chunk_ids
        )
        
        return {
            "status": "success",
            "message": f"Successfully added URL content to knowledge base",
            "url": url,
            "collection": collection_name,
            "chunks_added": len(chunks),
            "total_characters": len(content),
            "chunk_ids": chunk_ids[:5]  # Show first 5 IDs
        }
        
    except Exception as e:
        print(f"ERROR: Failed to add URL to knowledge base: {str(e)}")
        return {
            "error": f"Failed to add URL: {str(e)}",
            "status": "error"
        }

async def add_text_to_kb(text: str, source_name: str, collection_name: str = "default", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Add plain text directly to the knowledge base.
    
    Args:
        text: The text content to add
        source_name: Name/identifier for this text source
        collection_name: Collection to add content to
        metadata: Additional metadata to store with chunks
    
    Returns:
        Dictionary with ingestion results
    """
    print(f"INFO: Adding text to knowledge base: {source_name}")
    
    try:
        # Validate input
        if not text or len(text.strip()) < 10:
            return {
                "error": "Text content is too short (minimum 10 characters)",
                "status": "error"
            }
        
        # Initialize components
        client = _initialize_chroma()
        embedding_model = _initialize_embedding_model()
        text_splitter = _initialize_text_splitter()
        
        # Get or create collection
        collection = client.get_or_create_collection(collection_name)
        
        # Chunk the content
        print(f"INFO: Chunking text content ({len(text)} characters)")
        chunks = text_splitter.split_text(text)
        
        if not chunks:
            return {
                "error": "No chunks generated from text",
                "status": "error"
            }
        
        # Generate embeddings
        print(f"INFO: Generating embeddings for {len(chunks)} chunks")
        embeddings = embedding_model.encode(chunks, normalize_embeddings=True)
        
        # Prepare metadata for each chunk
        base_metadata = {
            "source_name": source_name,
            "source_type": "text",
            "timestamp": datetime.now().isoformat(),
            "collection": collection_name,
            "total_chunks": len(chunks),
            "content_length": len(text)
        }
        
        # Add user-provided metadata
        if metadata:
            base_metadata.update(metadata)
        
        # Create chunk-specific metadata
        chunk_metadatas = []
        for i, chunk in enumerate(chunks):
            chunk_meta = base_metadata.copy()
            chunk_meta.update({
                "chunk_index": i,
                "chunk_length": len(chunk),
                "token_count": len(chunk.split())  # Rough token estimate
            })
            chunk_metadatas.append(chunk_meta)
        
        # Generate unique IDs for chunks
        chunk_ids = [f"{source_name}_{i}_{hash(chunk) % 100000}" for i, chunk in enumerate(chunks)]
        
        # Add to ChromaDB
        print(f"INFO: Storing {len(chunks)} chunks in collection '{collection_name}'")
        collection.add(
            documents=chunks,
            embeddings=embeddings.tolist(),
            metadatas=chunk_metadatas,
            ids=chunk_ids
        )
        
        return {
            "status": "success",
            "message": f"Successfully added text content to knowledge base",
            "source_name": source_name,
            "collection": collection_name,
            "chunks_added": len(chunks),
            "total_characters": len(text),
            "chunk_ids": chunk_ids[:5]  # Show first 5 IDs
        }
        
    except Exception as e:
        print(f"ERROR: Failed to add text to knowledge base: {str(e)}")
        return {
            "error": f"Failed to add text: {str(e)}",
            "status": "error"
        }

def register(mcp_instance):
    """Register the RAG knowledge base tools with the MCP server"""
    
    # Check if dependencies are available
    if not all([CHROMADB_AVAILABLE, SENTENCE_TRANSFORMERS_AVAILABLE, LANGCHAIN_AVAILABLE]):
        missing = []
        if not CHROMADB_AVAILABLE:
            missing.append("chromadb")
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            missing.append("sentence-transformers")
        if not LANGCHAIN_AVAILABLE:
            missing.append("langchain-text-splitters")
        
        print(f"WARNING: RAG Knowledge Base tools not registered - missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return
    
    # Register all RAG tools
    mcp_instance.tool()(setup_knowledge_base)
    mcp_instance.tool()(get_kb_health)
    mcp_instance.tool()(add_url_to_kb)
    mcp_instance.tool()(add_text_to_kb)
    
    print("INFO: RAG Knowledge Base tools registered successfully")
    print("INFO: Available tools: setup_knowledge_base, get_kb_health, add_url_to_kb, add_text_to_kb")
    print("INFO: Run setup_knowledge_base() to initialize the system")