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

# Configuration file path
CONFIG_FILE = "kb_config.json"
KNOWLEDGE_BASE_DIR = Path("C:/Users/usuario/agent_playground/knowledge_base")

def _load_config() -> Dict[str, Any]:
    """Load configuration from JSON file."""
    global _config
    if _config is not None:
        return _config
    
    config_path = KNOWLEDGE_BASE_DIR / CONFIG_FILE
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
        separators=chunking_config.get("separators", ["\n\n", "\n", ". ", " ", ""])
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
        config_path = KNOWLEDGE_BASE_DIR / CONFIG_FILE
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
        
        # Initialize components
        client = _initialize_chroma()
        embedding_model = _initialize_embedding_model()
        text_splitter = _initialize_text_splitter()
        
        # Test basic functionality
        # Create a test collection
        test_collection = client.get_or_create_collection("setup_test")
        
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
        
        # Clean up test collection
        client.delete_collection("setup_test")
        
        # Get default collection ready
        default_collection = client.get_or_create_collection(
            config["storage"]["default_collection"]
        )
        
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
        collections = client.list_collections()
        health_status["components"]["database"] = {
            "status": "connected",
            "collections": len(collections),
            "collection_names": [col.name for col in collections]
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
    
    # Register setup and health check tools
    mcp_instance.tool()(setup_knowledge_base)
    mcp_instance.tool()(get_kb_health)
    
    print("INFO: RAG Knowledge Base infrastructure tools registered successfully")
    print("INFO: Run setup_knowledge_base() to initialize the system")