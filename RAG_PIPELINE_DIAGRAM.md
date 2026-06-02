# RAG Pipeline Architecture - Visual Documentation

## 1. High-Level System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          USER INTERFACE                                  │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Web Frontend (Port 5173)                                         │  │
│  │  • Answer Length Selector (Brief/Medium/Detailed)                 │  │
│  │  • Chat Interface                                                 │  │
│  │  • Real-time Status Display                                       │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────────────────┘
                            │ HTTP REST API
┌───────────────────────────▼─────────────────────────────────────────────┐
│                        API LAYER (FastAPI)                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  API Server (Port 8000)                                           │  │
│  │  • /api/health  - Health check                                    │  │
│  │  • /api/chat    - Main chat endpoint                              │  │
│  │  • Request validation & CORS                                      │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
└───────────────────────────┼─────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────────────┐
│                      CORE AGENT LAYER                                    │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  FeynmanTwin Agent (main.py)                                      │  │
│  │  • Query orchestration                                            │  │
│  │  • Context preparation (with length preference)                   │  │
│  │  • Response synthesis                                             │  │
│  │  • Personality verification                                       │  │
│  └───────┬────────────────────┬─────────────────────┬───────────────┘  │
└─────────┼────────────────────┼─────────────────────┼───────────────────┘
          │                    │                     │
          │                    │                     │
┌─────────▼────────┐  ┌────────▼──────────┐  ┌──────▼────────────┐
│   RAG SYSTEM     │  │  MEMORY MANAGER   │  │    PERSONALITY    │
│  (rag_system.py) │  │ (memory_system.py)│  │  (personality.py) │
│                  │  │                   │  │                   │
│ • Query embed    │  │ • Session memory  │  │ • Style scoring   │
│ • Vector search  │  │ • Persistent mem  │  │ • Socratic method │
│ • Context build  │  │ • Insights        │  │ • Analogies       │
└─────────┬────────┘  └───────────────────┘  └───────────────────┘
          │
          │
┌─────────▼─────────────────────────────────────────────────────────┐
│                     DATA STORAGE LAYER                             │
│  ┌─────────────────────┐  ┌────────────────────┐                  │
│  │   ChromaDB          │  │   Local Files      │                  │
│  │   (Vector Store)    │  │                    │                  │
│  │                     │  │ • Processed chunks │                  │
│  │ • 2,657 embeddings  │  │ • Memory JSON      │                  │
│  │ • HNSW index        │  │ • Conversations    │                  │
│  │ • Metadata          │  │                    │                  │
│  └─────────────────────┘  └────────────────────┘                  │
└───────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DATA INGESTION PHASE                              │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐
    │   PDF Documents      │
    │                      │
    │ • Vol 1: 125 pages   │
    │ • Vol 2: 140 pages   │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │   OCR Processing     │
    │   (PyMuPDF/PyPDF2)   │
    │                      │
    │ • Text extraction    │
    │ • Page preservation  │
    │ • Format cleanup     │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Markdown Conversion │
    │                      │
    │ • 2 full documents   │
    │ • ~3.2 MB text       │
    │ • Structured format  │
    └──────────┬───────────┘
               │
               ▼

┌─────────────────────────────────────────────────────────────────────┐
│                    CHUNKING PHASE                                    │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐
    │  Semantic Chunking   │
    │                      │
    │ Parameters:          │
    │ • Size: 1000 chars   │
    │ • Overlap: 200 chars │
    │ • Boundary: semantic │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │   Chunk Processing   │
    │                      │
    │ Results:             │
    │ • 2,657 chunks       │
    │ • Avg: 1200 chars    │
    │ • 140 chunk files    │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Metadata Tagging    │
    │                      │
    │ • Source document    │
    │ • Page number        │
    │ • Chunk ID           │
    │ • Title              │
    └──────────┬───────────┘
               │
               ▼

┌─────────────────────────────────────────────────────────────────────┐
│                  EMBEDDING PHASE                                     │
└─────────────────────────────────────────────────────────────────────┘

    ┌──────────────────────┐
    │  Embedding Model     │
    │  (Local)             │
    │                      │
    │ Model:               │
    │ all-MiniLM-L6-v2     │
    │                      │
    │ Specs:               │
    │ • Dimensions: 384    │
    │ • Inference: ~50ms   │
    │ • Normalized: L2     │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Batch Processing    │
    │                      │
    │ • Batch size: 10     │
    │ • Total: 266 batches │
    │ • Parallel: No       │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │  Vector Storage      │
    │  (ChromaDB)          │
    │                      │
    │ Collection:          │
    │ "feynman_knowledge"  │
    │                      │
    │ Index: HNSW          │
    │ Distance: Cosine     │
    └──────────┬───────────┘
               │
               ▼
    ┌──────────────────────┐
    │   Ready for Queries  │
    │                      │
    │ • 2,657 vectors      │
    │ • ~150 MB storage    │
    │ • Fast retrieval     │
    └──────────────────────┘
```

---

## 3. Query Processing Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    QUERY LIFECYCLE                                   │
└─────────────────────────────────────────────────────────────────────┘

1. USER INPUT
   ┌────────────────────────────────────┐
   │ Question: "What is quantum         │
   │            entanglement?"          │
   │                                    │
   │ Length: "medium"                   │
   └────────────┬───────────────────────┘
                │
                ▼
2. QUERY EMBEDDING
   ┌────────────────────────────────────┐
   │ sentence-transformers encode       │
   │                                    │
   │ Input: "What is quantum..."        │
   │ Output: [0.12, -0.45, 0.89, ...]  │
   │         (384 dimensions)           │
   └────────────┬───────────────────────┘
                │
                ▼
3. VECTOR SEARCH
   ┌────────────────────────────────────┐
   │ ChromaDB.query()                   │
   │                                    │
   │ Query embedding: [...]             │
   │ n_results: 5                       │
   │ Metric: cosine similarity          │
   └────────────┬───────────────────────┘
                │
                ▼
4. RESULTS RETRIEVAL
   ┌────────────────────────────────────┐
   │ Top 5 matching chunks:             │
   │                                    │
   │ 1. "Quantum entanglement occurs... │
   │    (similarity: 0.89)              │
   │ 2. "In quantum mechanics, two...   │
   │    (similarity: 0.85)              │
   │ 3. "The EPR paradox demonstrates...│
   │    (similarity: 0.82)              │
   │ 4. "Bell's theorem shows that...   │
   │    (similarity: 0.78)              │
   │ 5. "Measurement collapse is...     │
   │    (similarity: 0.75)              │
   └────────────┬───────────────────────┘
                │
                ▼
5. CONTEXT BUILDING
   ┌────────────────────────────────────┐
   │ Aggregate relevant chunks          │
   │                                    │
   │ • Deduplicate overlaps             │
   │ • Preserve order                   │
   │ • Add metadata                     │
   │ • Truncate to token limit          │
   └────────────┬───────────────────────┘
                │
                ▼
6. PROMPT CONSTRUCTION
   ┌────────────────────────────────────┐
   │ System Prompt:                     │
   │ "You are Richard Feynman..."       │
   │                                    │
   │ Length Instruction:                │
   │ "Provide balanced 3-5 paragraphs..." │
   │                                    │
   │ Context:                           │
   │ [Retrieved chunks]                 │
   │                                    │
   │ Question:                          │
   │ "What is quantum entanglement?"    │
   └────────────┬───────────────────────┘
                │
                ▼
7. LLM GENERATION
   ┌────────────────────────────────────┐
   │ Google Gemini 2.5 Flash            │
   │                                    │
   │ Temperature: 0.7                   │
   │ Max tokens: ~800 (medium)          │
   │                                    │
   │ Generates response...              │
   └────────────┬───────────────────────┘
                │
                ▼
8. POST-PROCESSING
   ┌────────────────────────────────────┐
   │ • Personality scoring (87%)        │
   │ • Teaching style enhancement       │
   │ • Socratic elements check          │
   │ • Memory recording                 │
   └────────────┬───────────────────────┘
                │
                ▼
9. RESPONSE DELIVERY
   ┌────────────────────────────────────┐
   │ {                                  │
   │   "answer": "Well, let me explain...│
   │   "metadata": {                    │
   │     "retrieved_docs": 5,           │
   │     "personality_score": 0.87,     │
   │     "processing_time": 2.3s        │
   │   }                                │
   │ }                                  │
   └────────────────────────────────────┘
```

---

## 4. Dataset Structure

```
feynman_twin/
│
├── data/
│   ├── raw/                          [Empty - PDFs processed]
│   │
│   ├── markdown/                     [Converted documents]
│   │   ├── .chunks/                  [140 chunk files]
│   │   │   ├── Vol_1/
│   │   │   │   ├── pages_0001_0005.md
│   │   │   │   ├── pages_0006_0010.md
│   │   │   │   └── ... (70 files)
│   │   │   └── Vol_2/
│   │   │       ├── pages_0001_0005.md
│   │   │       └── ... (70 files)
│   │   │
│   │   ├── Vol_1_Exercises.md        [Full document 1]
│   │   └── Vol_2_EM.md               [Full document 2]
│   │
│   └── processed/
│       └── feynman_processed_chunks.json  [2,657 chunks]
│
├── embeddings/                       [Vector database]
│   ├── chroma.sqlite3                [SQLite backend]
│   ├── [UUID].bin                    [Vector files]
│   └── ... (~150 MB total)
│
└── memory/                           [Persistent storage]
    ├── persistent_memory.json
    ├── session_memory.json
    └── conversations/
        └── [timestamp].json
```

**Chunk File Structure:**
```json
{
  "source": "feynman_lectures",
  "title": "Vol_1_Chapter_3_Mechanics",
  "text": "Newton's laws of motion state that...",
  "chunk_id": 42,
  "page_number": 15,
  "metadata": {
    "topic": "Classical Mechanics",
    "difficulty": "intermediate"
  }
}
```

---

## 5. Embedding Space Visualization

```
High-dimensional vector space (384 dimensions)
Visualized in 2D using t-SNE:

                    Quantum Mechanics
                          ●
                    ●   ●   ●
                  ●   ●   ●   ●
        
    
Electromagnetism              Mathematics
    ●●●                             ●●
  ●●●●●●                          ●●●●
    ●●●                             ●●
    

    ●●●                         ●●●●●
  ●●●●●●                      ●●●●●●●
    ●●●                         ●●●●●
Classical Mechanics        Thermodynamics


Legend:
● = Document chunk (vector)
Proximity = Semantic similarity
Clusters = Related topics
```

**Query Example:**
```
User Query: "uncertainty principle"
         ↓
Query Vector: [0.12, -0.45, 0.89, ...]
         ↓
Search in space
         ↓
Find nearest 5 neighbors in "Quantum Mechanics" cluster
         ↓
Return most similar chunks
```

---

## 6. Answer Length Control Flow

```
┌─────────────────────────────────────────────────────────────┐
│                 USER SELECTS LENGTH                          │
└─────────────────────────────────────────────────────────────┘

    Brief                Medium               Detailed
      │                    │                     │
      ├────────────────────┼─────────────────────┤
      │                    │                     │
      ▼                    ▼                     ▼
┌──────────┐         ┌──────────┐         ┌──────────┐
│  Target  │         │  Target  │         │  Target  │
│ 2-3 para │         │ 3-5 para │         │ 5-8 para │
│          │         │          │         │          │
│ 200-400  │         │ 400-800  │         │ 800-1500 │
│  tokens  │         │  tokens  │         │  tokens  │
└─────┬────┘         └─────┬────┘         └─────┬────┘
      │                    │                     │
      ▼                    ▼                     ▼
┌──────────────────────────────────────────────────────┐
│         SYSTEM PROMPT MODIFICATION                    │
│                                                       │
│  Brief: "Be concise. Focus on core concepts only.    │
│          Limit to 2-3 paragraphs."                    │
│                                                       │
│  Medium: "Provide balanced explanation with some     │
│           examples. Use 3-5 paragraphs."             │
│                                                       │
│  Detailed: "Comprehensive deep dive with multiple    │
│             examples and analogies. 5-8+ paragraphs."│
└──────────────────────────┬───────────────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  LLM follows   │
                  │  instructions  │
                  └────────┬───────┘
                           │
                           ▼
                ┌──────────────────────┐
                │  Response generated  │
                │  matching target     │
                │  length              │
                └──────────────────────┘
```

---

## 7. Error Handling & Fallbacks

```
┌─────────────────────────────────────────────────────────┐
│              ROBUSTNESS ARCHITECTURE                     │
└─────────────────────────────────────────────────────────┘

Query Processing
      │
      ▼
┌──────────────┐
│ Try Primary  │
│ Gemini 2.5   │
│   Flash      │
└──────┬───────┘
       │
       ├─ Success ──────────────────────────────┐
       │                                        │
       └─ API Error                             │
          │                                     │
          ▼                                     │
     ┌──────────────┐                          │
     │ Try Fallback │                          │
     │ Gemini 1.5   │                          │
     │   Flash      │                          │
     └──────┬───────┘                          │
            │                                   │
            ├─ Success ─────────────────────┐  │
            │                                │  │
            └─ Still fails                   │  │
               │                             │  │
               ▼                             │  │
          ┌──────────────┐                  │  │
          │ Return error │                  │  │
          │  message     │                  │  │
          └──────────────┘                  │  │
                                            │  │
                                            ▼  ▼
                                  ┌──────────────────┐
                                  │ Format response  │
                                  │ Add metadata     │
                                  │ Log metrics      │
                                  └────────┬─────────┘
                                           │
                                           ▼
                                  ┌──────────────────┐
                                  │ Return to user   │
                                  └──────────────────┘

Embedding Generation
      │
      ▼
┌──────────────┐
│ Check config │
└──────┬───────┘
       │
       ├─ "local" ──────▶ Sentence-Transformers (no quota)
       │
       └─ "api" ────────▶ Gemini Embedding API
                            │
                            ├─ Success
                            │
                            └─ Quota exceeded ──▶ Retry with backoff
                                                   (up to 4 attempts)
```

---

**Document Version**: 1.0  
**Last Updated**: June 2, 2026  
**Project**: Feynman Digital Twin
