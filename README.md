# 🍽️ ML-Enabled Calorie Chatbot

A full-stack calorie calculation chatbot powered by machine learning, featuring FastAPI backend, PostgreSQL database with fuzzy search, Redis caching, and Angular frontend.

## 📋 Features

- **USDA Food Database**: 6M+ food items with nutritional information
- **Dish Recognition**: Pre-configured dish recipes with ingredients
- **ML Intent Classification**: Distinguishes calorie queries from other requests
- **NER (Named Entity Recognition)**: Extracts dishes and ingredients from natural language
- **Fuzzy Matching**: PostgreSQL pg_trgm for typo-tolerant search
- **Redis Caching**: Fast response times for repeated queries
- **Multi-language Support**: English, Arabic, and Franco-Arabic
- **Unit Conversions**: Handles g, kg, tbsp, tsp, pieces, and Arabic units
- **Modifier Parsing**: Add/remove/replace ingredients dynamically
- **Session Persistence**: Maintains conversation context

## 🏗️ Architecture

```
├── backend/          # FastAPI + SQLAlchemy + Redis
│   ├── data/         # USDA JSON and dishes Excel
│   ├── models/       # Trained ML models (intent, NER)
│   ├── scripts/      # Training and ingestion scripts
│   └── services/     # Business logic services
├── frontend/         # Angular chat UI
└── docker-compose.yml # Full stack orchestration
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for training models)
- Node.js 18+ (for frontend development)
- Make (optional, for convenience commands)

### 1. Clone and Setup

```bash
git clone https://github.com/AA-Fatima/599_cal.git
cd 599_cal

# Copy environment template
cp .env.example .env

# (Optional) Add LLM API key for ingredient suggestions
nano .env  # Set LLM_API_KEY=your_key_here
```

### 2. Start with Docker Compose

**Using Make (recommended):**
```bash
make build  # Build images
make up     # Start services
make logs   # View logs
```

**Or using docker-compose directly:**
```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

Services will be available at:
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Ingest Data

The first time you run the stack, ingest the USDA and dishes data:

**Using Make:**
```bash
make ingest
```

**Or using docker-compose:**
```bash
docker-compose exec backend python scripts/ingest_data.py
```

This will:
- Create database tables with pg_trgm indexes
- Load ~6,300 USDA food items
- Load dish recipes from Excel
- Enable fuzzy search on all name fields

**Expected output:**
```
============================================================
USDA & Dishes Data Ingestion
============================================================
✓ pg_trgm extension enabled
✓ Existing data cleared
✓ Inserted 6,342 foundation items
✓ Inserted 24 dishes with ingredients
✓ Created indexes
============================================================
INGESTION COMPLETE
============================================================
USDA Items:        6,342
Dishes:            24
Dish Ingredients:  87
============================================================
```

## 📊 Training ML Models

The system works with fallback behavior when models are absent. To train custom models:

### Intent Classification

Classify queries as calorie-related or not.

**1. Prepare labeled data** (`backend/data/intent_labeled.jsonl`):
```json
{"text": "How many calories in fajita?", "label": "calorie_query"}
{"text": "What's the weather today?", "label": "other"}
{"text": "كم سعرة في التبولة", "label": "calorie_query"}
```

**2. Train model:**
```bash
cd backend
python scripts/train_intent.py --data data/intent_labeled.jsonl --output models/intent.joblib
```

### NER (CRF-based)

Extract dishes and ingredients using Conditional Random Fields.

**1. Prepare labeled data** (`backend/data/ner_labeled.jsonl`):
```json
{"tokens": ["I", "want", "fajita", "with", "tomato"], "labels": ["O", "O", "B-DISH", "O", "B-ING"]}
{"tokens": ["How", "many", "calories", "in", "tabbouleh"], "labels": ["O", "O", "O", "O", "B-DISH"]}
```

**2. Train model:**
```bash
cd backend
python scripts/train_ner_crf.py --data data/ner_labeled.jsonl --output models/ner_crf.joblib
```

### NER (Hugging Face Transformers)

Fine-tune a transformer model for better accuracy.

**1. Prepare labeled data** (`backend/data/ner_labeled.jsonl`):
```json
{"text": "I want fajita with extra tomatoes", "entities": [{"start": 7, "end": 13, "label": "DISH"}, {"start": 25, "end": 33, "label": "ING"}]}
```

**2. Train model:**
```bash
cd backend
python scripts/train_ner_hf.py \
  --data data/ner_labeled.jsonl \
  --output models/ner_hf \
  --base-model distilbert-base-uncased \
  --epochs 3
```

**3. Update .env:**
```bash
HF_NER_MODEL=models/ner_hf
```

## 🛠️ Development

### Makefile Commands

For convenience, a Makefile is provided with common commands:

```bash
make help          # Show all available commands
make up            # Start all services
make down          # Stop all services
make build         # Build Docker images
make logs          # View all logs
make logs-backend  # View backend logs only
make ingest        # Run data ingestion
make shell-backend # Open shell in backend
make shell-db      # Open PostgreSQL shell
make clean         # Stop and remove volumes
make restart       # Restart all services
make rebuild       # Rebuild and restart
```

### Backend Development

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run locally (requires Postgres and Redis)
export $(cat ../.env | xargs)
uvicorn main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Run dev server
ng serve --port 4200
```

### Running Tests

```bash
# Backend tests (if added)
cd backend
pytest

# Frontend tests
cd frontend
ng test
```

## 📖 API Documentation

### POST /api/calculate

Calculate calories for a query.

**Request:**
```json
{
  "query": "fajita without cheese and add 2 tbsp olive oil",
  "session_id": "uuid-optional"
}
```

**Response:**
```json
{
  "session_id": "abc-123",
  "needs_clarification": false,
  "dish": "fajita",
  "ingredients": [
    {"name": "chicken", "weight_g": 150, "calories": 165},
    {"name": "peppers", "weight_g": 100, "calories": 26},
    {"name": "olive oil", "weight_g": 27, "calories": 239, "added": true}
  ],
  "total_calories": 430,
  "notes": ["Removed cheese", "Added 27g olive oil"]
}
```

### GET /api/missing

Get log of queries that couldn't be resolved.

**Response:**
```json
[
  {
    "user_query": "unknown dish xyz",
    "payload": {"needs_clarification": true, "message": "..."},
    "created_at": "2024-01-15T10:30:00"
  }
]
```

## 🗄️ Database Schema

### usda_items
- `fdc_id` (PK): USDA Food Data Central ID
- `name`: Lowercase food name (pg_trgm indexed)
- `alt_names`: JSON array of alternative names
- `per_100g_calories`: Calories per 100g
- `macros`: JSON object with protein, fat, carbs

### dishes
- `dish_id` (PK): Unique dish identifier
- `dish_name`: Lowercase dish name (pg_trgm indexed)
- `country`: Country of origin
- `date_accessed`: When data was collected

### dish_ingredients
- `id` (PK): Auto-increment
- `dish_id` (FK): References dishes
- `usda_fdc_id`: Link to USDA item
- `ingredient_name`: Name (pg_trgm indexed)
- `default_weight_g`: Default quantity in grams

## 🌍 Environment Variables

See `.env.example` for all variables. Key ones:

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_*` | Database connection | See .env.example |
| `REDIS_URL` | Redis cache connection | redis://redis:6379/0 |
| `HF_NER_MODEL` | Hugging Face NER model path | models/ner_hf |
| `INTENT_MODEL_PATH` | Intent classifier path | models/intent.joblib |
| `LLM_API_KEY` | Optional LLM for suggestions | (empty) |

## 🔒 Security

- **No secrets committed**: Use `.env` for all credentials
- **CORS configured**: Update `allow_origins` in production
- **LLM API key**: Set via environment variable only
- **Input validation**: Pydantic models validate all requests

## 🧪 Testing Queries

Try these sample queries:

**English:**
- "How many calories in fajita?"
- "fajita without cheese"
- "tabbouleh with extra olive oil"
- "200g chicken breast"

**Arabic:**
- "كم سعرة في فاهيتا"
- "تبولة بدون زيت"
- "بطاطا مقلية"

**Franco-Arabic:**
- "fahita ma3 tomato"
- "taboule bala zeit"

## 🛠️ Troubleshooting

### Database connection error
```bash
# Check if Postgres is running
docker-compose ps postgres

# View logs
docker-compose logs postgres
```

### Redis not available
The system degrades gracefully without Redis. Check logs:
```bash
docker-compose logs redis
```

### ML models not loading
Models are optional. The system uses fallbacks when absent:
- **Intent**: Assumes all queries are calorie-related
- **NER**: Returns empty entities (uses fallback parsing)

### Frontend can't connect to backend
Check CORS settings in `backend/main.py` and ensure backend is running:
```bash
curl http://localhost:8000/api/missing
```

## 📝 Data Sources

- **USDA Food Data Central**: [fdc.nal.usda.gov](https://fdc.nal.usda.gov)
- **Dishes**: Manually curated from various sources
- **Training data**: User-labeled examples (not included, must be provided)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## 📄 License

See LICENSE file for details.

## 👥 Authors

AA-Fatima - Initial implementation

## 🙏 Acknowledgments

- USDA for comprehensive food database
- Hugging Face for transformer models
- FastAPI and SQLAlchemy communities
