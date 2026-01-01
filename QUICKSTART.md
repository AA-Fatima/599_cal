# Quick Start Guide

## Option 1: Docker Compose (Recommended)

### 1. Prerequisites
- Docker and Docker Compose installed
- Git

### 2. Clone and Setup
```bash
git clone <repository-url>
cd 599_cal
cp .env.example .env
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### 4. Initialize Database
```bash
# Run all initialization and ingestion in one command
docker-compose exec backend python scripts/ingest_all.py
```

This will:
- Create database schema with pg_trgm extension
- Ingest USDA food data
- Ingest dishes and ingredients
- Populate synonyms and unit conversions

### 5. Access Application
- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 6. Test the Chatbot
Try these example queries:
- "How many calories in fajita?"
- "200g rice"
- "fajita without fries"
- "tabbouleh with 2 tbsp olive oil"

---

## Option 2: Local Development

### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
export POSTGRES_HOST=localhost
export POSTGRES_DB=calories
export POSTGRES_USER=calories
export POSTGRES_PASSWORD=supersecret
export REDIS_URL=redis://localhost:6379/0
export HF_NER_MODEL=models/ner_hf
export INTENT_MODEL_PATH=models/intent.joblib
export USDA_FOUND_PATH=data/USDA_foundation.json
export USDA_LEGACY_PATH=data/USDA_sr_legacy.json
export DISHES_XLSX_PATH=data/dishes.xlsx
export LLM_API_KEY=

# Start PostgreSQL and Redis (via Docker)
docker-compose up -d postgres redis

# Verify setup
python verify_setup.py

# Initialize and ingest data
python scripts/ingest_all.py

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Access at http://localhost:4200
```

---

## Troubleshooting

### "Module not found" errors
```bash
# Backend: Install dependencies
cd backend && pip install -r requirements.txt

# Frontend: Install dependencies
cd frontend && npm install
```

### Database connection errors
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart services
docker-compose restart postgres backend
```

### pg_trgm extension error
```bash
# Manually create extension
docker-compose exec postgres psql -U calories -d calories -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

### Frontend can't reach backend
1. Check CORS settings in `backend/main.py`
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check network in docker-compose: `docker-compose exec frontend ping backend`

### Models not loading (Expected)
The system will show warnings like:
```
Warning: Intent model not found at models/intent.joblib, using fallback
Warning: NER model not found at models/ner_hf, using fallback
```

This is normal - train models as described in main README or use fallback mode.

---

## Stopping Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (WARNING: deletes database)
docker-compose down -v
```

---

## Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Train ML models (optional but recommended)
3. Customize synonyms and unit conversions via database
4. Set up LLM API key for ingredient suggestions
5. Configure production deployment
