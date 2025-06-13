# RAG Knowledge Base Tool

**Filename:** `rag_knowledge_base_tool.py`  
**Status:** ✅ Production Ready  
**Dependencies:** `chromadb`, `sentence-transformers`, `langchain-text-splitters`

## Overview

The RAG Knowledge Base Tool provides a complete Retrieval-Augmented Generation (RAG) system for your MCP server. It allows you to build, manage, and search a semantic knowledge base that your chat agents can use to provide accurate, source-backed responses.

### Key Features

- 🧠 **Semantic Search** - Find relevant information using meaning, not just keywords
- 📥 **Content Ingestion** - Add content from URLs and plain text
- 🔍 **Vector Embeddings** - Uses BGE-M3 model for high-quality embeddings
- 📚 **Multi-Collection Support** - Organize knowledge by topic or domain
- 📊 **Source Tracking** - Full metadata and provenance for all content
- ⚡ **Production Ready** - Persistent storage with ChromaDB

## How It Works

### Architecture

```
Content → Chunking → Embeddings → Vector Database → Semantic Search
    ↓         ↓          ↓             ↓               ↓
  URLs     1000-char   BGE-M3      ChromaDB       Ranked Results
  Text     chunks      vectors     Collections    with Sources
```

### Technical Stack

- **Vector Database:** ChromaDB (persistent local storage)
- **Embedding Model:** BGE-M3 (multilingual, 8192 context, state-of-the-art)
- **Text Chunking:** LangChain RecursiveCharacterTextSplitter
- **Storage Location:** `./knowledge_base/chroma_db`
- **Configuration:** `kb_config.json`

## Available Tools

### 🔧 Infrastructure Tools

#### `setup_knowledge_base()`
Initialize the RAG system and test all components.

```python
result = await setup_knowledge_base()
# Returns: status, config info, component status, test results
```

#### `get_kb_health()`
Check system health and component status.

```python
health = await get_kb_health()
# Returns: system status, component health, database info
```

### 📥 Content Ingestion Tools

#### `add_url_to_kb(url, collection_name="default", metadata=None)`
Scrape and add webpage content to knowledge base.

```python
result = await add_url_to_kb(
    url="https://example.com/article",
    collection_name="research",
    metadata={"topic": "AI", "priority": "high"}
)
# Returns: status, chunks added, source info
```

#### `add_text_to_kb(text, source_name, collection_name="default", metadata=None)`
Add plain text content directly to knowledge base.

```python
result = await add_text_to_kb(
    text="Your content here...",
    source_name="meeting_notes_2024",
    collection_name="internal",
    metadata={"meeting": "Q4_planning", "date": "2024-12-15"}
)
# Returns: status, chunks added, processing info
```

### 🔍 Search & Retrieval Tools

#### `search_kb(query, collection_name="default", limit=5, include_metadata=True)`
Search knowledge base for relevant content.

```python
results = await search_kb(
    query="machine learning best practices",
    collection_name="research",
    limit=10
)
# Returns: ranked results with similarity scores and sources
```

#### `list_kb_sources(collection_name="default")`
List all sources in a collection with statistics.

```python
sources = await list_kb_sources("research")
# Returns: source list, chunk counts, timestamps, metadata
```

#### `get_kb_stats()`
Get comprehensive knowledge base statistics.

```python
stats = await get_kb_stats()
# Returns: collections, sources, chunks, performance metrics
```

## Using with Chat Agents

### Basic RAG Workflow

1. **Build Knowledge Base**
   ```python
   # Add company documentation
   await add_url_to_kb("https://company.com/docs", "company_docs")
   
   # Add meeting notes
   await add_text_to_kb(meeting_transcript, "meeting_2024_12", "internal")
   ```

2. **Search for Context**
   ```python
   # Find relevant information for user query
   context = await search_kb("project timeline", "company_docs", limit=3)
   relevant_chunks = [r["content"] for r in context["results"]]
   ```

3. **Use in Agent Response**
   ```python
   # Combine retrieved context with user query
   system_prompt = f"""
   Answer the user's question using the following context:
   
   {chr(10).join(relevant_chunks)}
   
   Cite sources when providing information.
   """
   ```

### Advanced Integration Patterns

#### Multi-Collection Search
```python
# Search across multiple knowledge domains
research_results = await search_kb(query, "research_papers")
internal_results = await search_kb(query, "company_docs") 
combined_context = research_results["results"] + internal_results["results"]
```

#### Dynamic Collection Selection
```python
# Choose collection based on query type
if "company" in query.lower() or "internal" in query.lower():
    collection = "company_docs"
elif "research" in query.lower() or "paper" in query.lower():
    collection = "research_papers"
else:
    collection = "general"

results = await search_kb(query, collection)
```

#### Source Attribution
```python
results = await search_kb(query, collection_name)
for result in results["results"]:
    content = result["content"]
    source = result["metadata"]["source"]
    similarity = result["similarity_score"]
    
    response += f"{content}\n\n*Source: {source} (confidence: {similarity:.2f})*\n\n"
```

## Configuration

### Default Settings (`kb_config.json`)

```json
{
    "embedding": {
        "model_name": "BAAI/bge-m3",
        "embedding_dimension": 1024,
        "normalize_embeddings": true
    },
    "chunking": {
        "chunk_size": 1000,
        "chunk_overlap": 100
    },
    "storage": {
        "database_path": "./knowledge_base/chroma_db",
        "default_collection": "default"
    }
}
```

### Customization Options

- **Chunk Size:** Adjust `chunk_size` for longer/shorter contexts
- **Overlap:** Modify `chunk_overlap` to preserve context across chunks
- **Embedding Model:** Change `model_name` to different sentence-transformers models
- **Collections:** Use different collections for different knowledge domains

## Best Practices

### Content Organization

```python
# Organize by domain/topic
await add_url_to_kb(url, "customer_support")  # Support docs
await add_url_to_kb(url, "product_specs")     # Technical specs  
await add_url_to_kb(url, "company_policies")  # Internal policies
```

### Metadata Strategy

```python
# Rich metadata for better filtering and tracking
metadata = {
    "department": "engineering",
    "document_type": "specification",
    "version": "v2.1",
    "last_updated": "2024-12-15",
    "classification": "internal"
}
await add_text_to_kb(content, source_name, collection, metadata)
```

### Search Optimization

```python
# Use specific, detailed queries
results = await search_kb(
    "How to deploy machine learning models in production with monitoring",
    collection_name="ml_docs",
    limit=5
)

# Filter results by similarity threshold
relevant_results = [
    r for r in results["results"] 
    if r["similarity_score"] > 0.7
]
```

## Common Use Cases

### 1. Customer Support Agent
```python
# Add support documentation
await add_url_to_kb("https://docs.company.com/faq", "support")
await add_url_to_kb("https://docs.company.com/troubleshooting", "support")

# Search for relevant help articles
async def get_support_context(user_question):
    results = await search_kb(user_question, "support", limit=3)
    return [r["content"] for r in results["results"] if r["similarity_score"] > 0.6]
```

### 2. Research Assistant
```python
# Build research knowledge base
await add_url_to_kb("https://arxiv.org/paper1", "research", {"field": "AI"})
await add_url_to_kb("https://arxiv.org/paper2", "research", {"field": "ML"})

# Find relevant research for queries
async def research_query(question, field=None):
    results = await search_kb(question, "research", limit=10)
    if field:
        # Filter by field if specified
        results["results"] = [
            r for r in results["results"] 
            if r["metadata"]["custom"].get("field") == field
        ]
    return results
```

### 3. Company Knowledge Bot
```python
# Comprehensive company knowledge base
collections = {
    "policies": "Company policies and procedures",
    "projects": "Project documentation and status",
    "processes": "Workflow and process documentation",
    "people": "Team information and contacts"
}

# Search across all relevant collections
async def company_search(query):
    all_results = []
    for collection in collections.keys():
        results = await search_kb(query, collection, limit=2)
        all_results.extend(results["results"])
    
    # Sort by similarity and return top results
    return sorted(all_results, key=lambda x: x["similarity_score"], reverse=True)[:5]
```

## Performance & Scalability

### Storage Requirements
- **Embeddings:** ~1KB per chunk (1024-dimensional vectors)
- **Text:** Original chunk size (typically 500-1500 characters)
- **Metadata:** ~200 bytes per chunk
- **Total:** ~2KB per chunk on average

### Performance Metrics
- **Search Speed:** ~10-50ms for collections under 10K chunks
- **Ingestion Speed:** ~2-5 chunks per second (limited by embedding generation)
- **Memory Usage:** ~500MB for BGE-M3 model + minimal per chunk

### Scaling Recommendations
- **Small Scale:** < 1K chunks - Single collection approach
- **Medium Scale:** 1K-10K chunks - Multiple collections by topic
- **Large Scale:** > 10K chunks - Consider collection sharding and caching

## Troubleshooting

### Common Issues

**"Model not found" Error**
```bash
# BGE-M3 model will download automatically on first use (~2.27GB)
# Ensure stable internet connection for initial download
```

**"Collection not found" Error**
```python
# Check available collections
stats = await get_kb_stats()
print("Available collections:", list(stats["collections"].keys()))
```

**Poor Search Results**
```python
# Check similarity scores
results = await search_kb(query, collection_name, limit=10)
for r in results["results"]:
    print(f"Score: {r['similarity_score']:.3f} - {r['content'][:100]}")

# Scores > 0.7 = Very relevant
# Scores 0.4-0.7 = Somewhat relevant  
# Scores < 0.4 = May not be relevant
```

### Maintenance Commands

```python
# Check system health
health = await get_kb_health()

# View all collections and sources
stats = await get_kb_stats()

# List sources in specific collection
sources = await list_kb_sources("collection_name")
```

## Integration with Existing Tools

### Web Search + RAG Pipeline
```python
# 1. Use brave_search to find relevant URLs
search_results = await brave_web_search("machine learning deployment")

# 2. Add top results to knowledge base
for result in search_results["results"][:5]:
    await add_url_to_kb(result["url"], "ml_research")

# 3. Search your curated knowledge base
rag_results = await search_kb("ML deployment best practices", "ml_research")
```

### File System Integration
```python
# Read local files and add to knowledge base
content = await read_file("important_document.md")
await add_text_to_kb(content, "important_document.md", "documents")

# Search and save results
results = await search_kb("project status", "documents")
context = "\n\n".join([r["content"] for r in results["results"][:3]])
await write_file("search_results.md", f"# Search Results\n\n{context}")
```

## Future Enhancements

- **Multi-modal Support:** Images, PDFs, audio transcripts
- **Advanced Chunking:** Semantic chunking, document structure awareness
- **Reranking:** Secondary ranking models for improved relevance
- **Caching:** Query result caching for repeated searches
- **Analytics:** Search analytics and knowledge base usage metrics

## Testing with Chat Models

### Recommended Test Phrases

Use these natural language phrases to test your RAG Knowledge Base with chat models:

#### **Initial Setup & Health Checks**
- *"Set up the RAG knowledge base system"*
- *"Check if the knowledge base is healthy and working"*
- *"What's the current status of our knowledge base?"*
- *"Initialize the RAG system and run diagnostics"*

#### **Building Your Knowledge Base**
- *"Add this webpage to our knowledge base: https://example.com/article"*
- *"Scrape and store this documentation: https://docs.company.com/api"*
- *"Add this text to our internal knowledge collection: [paste your text]"*
- *"Build a knowledge base from these company policy documents"*
- *"Create a research collection and add these URLs to it"*

#### **Searching and Retrieving Information**
- *"What does our knowledge base say about machine learning deployment?"*
- *"Search for information about vector databases in our research collection"*
- *"Find relevant content about project timelines from our company docs"*
- *"What are the best practices for API security according to our knowledge base?"*
- *"Search our support documentation for troubleshooting steps"*

#### **Knowledge Base Management**
- *"Show me all the sources in our knowledge base"*
- *"List what's in our research collection"*
- *"What are the statistics for our knowledge base?"*
- *"How many documents do we have stored?"*
- *"Which sources have the most content chunks?"*

#### **Advanced RAG Workflows**
- *"First search the web for machine learning best practices, then add the top 3 results to our ML collection, then search our knowledge base for deployment strategies"*
- *"Build a comprehensive knowledge base about vector databases by searching for recent articles and academic papers"*
- *"Add our company handbook to the knowledge base, then search for vacation policies"*
- *"Create a customer support knowledge base from our FAQ pages, then test it by asking common customer questions"*

### **Multi-Step Conversation Examples**

#### **Building Domain Expertise**
```
User: "I need to become an expert on RAG systems. Help me build a knowledge base."

Agent: "I'll help you build a comprehensive RAG knowledge base. Let me start by searching for authoritative sources..."
[Uses brave_web_search + add_url_to_kb + search_kb workflow]

User: "Now search our knowledge base for the key components of RAG"

Agent: "Based on our knowledge base..." 
[Uses search_kb with specific query]
```

#### **Company Knowledge Management**
```
User: "Add our company documentation to a knowledge base"

Agent: "I'll create a company knowledge collection..."
[Uses add_url_to_kb with collection_name="company_docs"]

User: "What does our documentation say about the deployment process?"

Agent: "Let me search our company knowledge base..."
[Uses search_kb on company_docs collection]
```

#### **Research Assistant Workflow**
```
User: "I'm researching vector databases. Build me a research knowledge base."

Agent: "I'll create a comprehensive vector database research collection..."
[Uses web search → add multiple URLs → organize by collection]

User: "Compare Pinecone vs Chroma based on our research"

Agent: "Based on our research knowledge base..."
[Uses search_kb with specific queries for each database]
```

### **Testing Different Chat Model Integrations**

#### **For Claude Desktop Integration**
Test phrases that leverage MCP tool calling:
- *"Use the RAG tools to search for information about X"*
- *"Call the knowledge base search function to find Y"*
- *"Execute a search_kb query for Z"*

#### **For n8n Workflows**
Test phrases that trigger automated workflows:
- *"Trigger the knowledge base build workflow for this URL"*
- *"Run the RAG search automation for customer support"*
- *"Execute the research knowledge collection pipeline"*

#### **For Custom Chat Applications**
Test natural conversation flows:
- *"I need help with [topic]. What does our knowledge base contain about this?"*
- *"Based on what we know, what are the recommendations for [scenario]?"*
- *"Search our internal docs and give me a summary of [policy/process]"*

### **Error Handling Test Phrases**

Test how the system handles edge cases:
- *"Search for something that doesn't exist in our knowledge base"*
- *"Add an invalid URL to the knowledge base"*
- *"Search an empty collection"*
- *"Try to add very short text content"*

### **Performance Testing Phrases**

Test system performance and limits:
- *"Add 5 long articles to our knowledge base and time the process"*
- *"Search for very specific technical terms"*
- *"Compare search results across different collections"*
- *"Show detailed statistics after adding substantial content"*

### **Integration Testing with Other Tools**

#### **With Web Search**
- *"Search the web for X, add top results to knowledge base, then query what we learned"*
- *"Find recent news about Y, store it, then ask for a summary"*

#### **With File System**
- *"Read our local documentation files and add them to the knowledge base"*
- *"Search knowledge base for Z, then save results to a summary file"*

#### **With Screen Capture**
- *"[CAPTURE] Add information about what's shown on screen, then search for related content"*
- *"Take a screenshot of this error, then search knowledge base for solutions"*

### **Conversation Starters for Different Use Cases**

#### **Customer Support Agent**
- *"A customer is asking about [issue]. Search our support knowledge base for solutions."*
- *"Build a support knowledge base from our FAQ and troubleshooting guides."*

#### **Research Assistant**
- *"I'm writing a paper on [topic]. Help me build a research knowledge base and find key insights."*
- *"Compare different approaches to [problem] based on our research collection."*

#### **Internal Knowledge Bot**
- *"What do our company policies say about [topic]?"*
- *"Search our internal documentation for procedures related to [process]."*

#### **Technical Documentation Assistant**
- *"Find code examples and best practices for [technology] in our knowledge base."*
- *"Add technical documentation from [source] and help me understand [concept]."*

These phrases will help you thoroughly test the RAG Knowledge Base system and demonstrate its capabilities across different chat model integrations and use cases.