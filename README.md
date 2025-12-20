
# IIRAF – Intelligent Incident Resolution & Automation Framework (PoC)

This repository contains a complete starter setup for the IIRAF Proof of Concept.
It is designed to be opened directly in Google Antigravity IDE.

## Scope (PoC)
- Semantic search over incidents & KB articles
- Pattern detection for recurring incidents
- AI-powered solution generation using LLM
- Simulated auto-heal recommendations
- FastAPI backend
- React frontend (skeleton)
- MLOps intentionally excluded

## AI/ML Libraries Used

### 1. **Sentence Transformers** (`sentence-transformers`)
- **Purpose**: Generate semantic embeddings for incident descriptions and KB articles
- **Model Used**: `all-MiniLM-L6-v2`
- **Use Case**: Converts text into 384-dimensional dense vectors for semantic similarity search
- **Location**: `src/build_index.py`, `src/query_retrieval.py`
- **Key Features**:
  - Lightweight and fast (6-layer MiniLM model)
  - Pre-trained on large text corpus
  - Optimized for semantic similarity tasks

### 2. **FAISS** (`faiss-cpu`)
- **Purpose**: Fast similarity search and clustering of dense vectors
- **Index Type**: `IndexFlatIP` (Inner Product for cosine similarity)
- **Use Case**: Efficient retrieval of similar incidents and KB articles
- **Location**: `src/build_index.py`, `src/query_retrieval.py`
- **Key Features**:
  - Handles large-scale vector similarity search
  - L2 normalization for cosine similarity
  - In-memory index for fast retrieval

### 3. **Google Generative AI** (`google-generativeai`)
- **Purpose**: AI-powered solution generation using Large Language Model
- **Model Used**: `gemini-pro`
- **Use Case**: Synthesize incident resolutions and KB articles into coherent step-by-step solutions
- **Location**: `src/solution_generator.py`
- **Key Features**:
  - Natural language understanding and generation
  - Context-aware solution recommendations
  - Fallback mechanism when API unavailable
  - Requires `GEMINI_API_KEY` in `.env` file

### 4. **Scikit-learn** (`scikit-learn`)
- **Purpose**: Machine learning utilities and preprocessing
- **Use Case**: Data preprocessing, feature engineering, and ML utilities
- **Location**: Various preprocessing and analysis scripts
- **Key Features**:
  - Standard ML algorithms and utilities
  - Data preprocessing tools
  - Model evaluation metrics

### 5. **HDBSCAN** (`hdbscan`)
- **Purpose**: Hierarchical Density-Based Spatial Clustering
- **Use Case**: Detect patterns and clusters in incident data
- **Location**: Pattern detection and clustering analysis
- **Key Features**:
  - Automatic cluster detection
  - Handles noise and outliers
  - No need to specify number of clusters

### 6. **UMAP** (`umap-learn`)
- **Purpose**: Uniform Manifold Approximation and Projection for dimensionality reduction
- **Use Case**: Visualize high-dimensional embeddings and reduce dimensionality
- **Location**: Data analysis and visualization scripts
- **Key Features**:
  - Preserves both local and global structure
  - Faster than t-SNE
  - Useful for embedding visualization

### 7. **XGBoost** (`xgboost`)
- **Purpose**: Gradient boosting framework for predictive modeling
- **Use Case**: Incident severity prediction and classification tasks
- **Location**: Predictive analytics and classification
- **Key Features**:
  - High performance and accuracy
  - Handles missing values
  - Built-in regularization

## Supporting Libraries

### Data Processing
- **Pandas** (`pandas`): Data manipulation and CSV handling
- **NumPy** (`numpy`): Numerical computing and array operations

### Environment & Configuration
- **Python-dotenv** (`python-dotenv`): Load environment variables from `.env` file

### Backend Framework
- **FastAPI** (`fastapi`): Modern web framework for building APIs
- **Uvicorn** (`uvicorn`): ASGI server for FastAPI

## How to Start

### 1. Setup Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_api_key_here
```

### 3. Generate Dataset
```bash
python src/generate_dataset.py
```

### 4. Build FAISS Index
```bash
python src/build_index.py
```

### 5. Run Backend Server
```bash
python -m uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
```

### 6. Access Application
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Architecture Overview

```
User Query → Sentence Transformer (Embedding) → FAISS (Similarity Search) 
→ Retrieved Results → Gemini AI (Solution Generation) → Structured Response
```

## Key Features

- **Semantic Search**: Uses sentence transformers to understand meaning, not just keywords
- **AI-Powered Solutions**: Gemini LLM synthesizes multiple sources into actionable steps
- **Pattern Detection**: Identifies recurring issues using clustering algorithms
- **Auto-Heal Simulation**: Recommends automated remediation actions
- **Real-time Index**: Detects stale data and supports manual refresh

## Project Structure

```
IIRAF_PoC_Starter/
├── src/
│   ├── app.py                    # FastAPI application
│   ├── build_index.py            # FAISS index builder
│   ├── query_retrieval.py        # Semantic search engine
│   ├── solution_generator.py     # AI solution generator (Gemini)
│   ├── pattern_engine.py         # Pattern detection
│   ├── autoheal_simulator.py     # Auto-heal recommendations
│   ├── data_loader.py            # Data loading utilities
│   └── generate_dataset.py       # Dataset generation
├── data/                         # CSV data files
├── frontend/                     # React frontend
├── index_store/                  # FAISS index storage
├── requirements.txt              # Python dependencies
└── .env                          # Environment variables (API keys)
```

## API Endpoints

- `GET /health` - Health check with index status
- `POST /api/search` - Semantic search for incidents and KB articles
- `POST /api/generate-solution` - AI-powered solution generation
- `GET /api/patterns` - Pattern detection results
- `POST /api/heal` - Trigger auto-heal actions
- `GET /api/index/status` - FAISS index status
- `POST /api/index/refresh` - Manually rebuild FAISS index

See individual scripts in `/src` for implementation details.
