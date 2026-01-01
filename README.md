# Calorie Chatbot - Full Stack Application

A comprehensive calorie calculation chatbot with NLP/ML capabilities, supporting Arabic, Franco-Arabic, and English queries.

## Features

- 🍔 **Calorie Calculation**: Calculate calories for dishes and ingredients
- 🔍 **Fuzzy Search**: PostgreSQL pg_trgm-based fuzzy matching with rapidfuzz fallback
- 🗣️ **Multi-language**: Support for Arabic, Franco-Arabic, and English
- 🤖 **ML Integration**: Optional intent classification and NER models
- 📊 **Comprehensive Database**: USDA food database with macronutrients
- 🔄 **Session Management**: Persistent chat sessions
- 📝 **Missing Dish Logging**: Track and analyze queries for unknown dishes
- 🚀 **Containerized**: Full Docker Compose setup

## Architecture

```
├── backend/          # FastAPI Python backend
│   ├── data/        # USDA and dishes data files
│   ├── models/      # ML models (user-trained)
│   ├── scripts/     # Database initialization and ingestion scripts
│   └── services/    # Business logic services
├── frontend/        # Angular chat UI
└── docker-compose.yml
```

## Prerequisites

- Docker and Docker Compose
- (Optional) Python 3.11+ for local development
- (Optional) Node.js 18+ for frontend development

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd 599_cal

# Copy environment file
cp .env.example .env

# Edit .env if needed (default values should work for docker-compose)
```

### 2. Start Services

```bash
# Start all services (PostgreSQL, Redis, Backend, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f
```

### 3. Initialize Database and Ingest Data

```bash
# Initialize database schema and enable pg_trgm
docker-compose exec backend python scripts/init_db.py

# Ingest USDA data (foundation + legacy if available)
docker-compose exec backend python scripts/ingest_usda.py

# Ingest dishes data
docker-compose exec backend python scripts/ingest_dishes.py

# Populate reference data (synonyms and unit conversions)
docker-compose exec backend python scripts/populate_reference_data.py
```

### 4. Access the Application

- **Frontend**: http://localhost:4200
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432 (user: calories, pass: supersecret, db: calories)
- **Redis**: localhost:6379

## Data Files

The application expects the following data files in `backend/data/`:

- ✅ `USDA_foundation.json` - USDA Foundation Foods (included)
- ⚠️ `USDA_sr_legacy.json` - USDA SR Legacy Foods (optional, not included - large file)
- ✅ `dishes.xlsx` - Dish recipes with ingredients (included)

### USDA Legacy Data (Optional)

If you have the USDA SR Legacy file, place it in `backend/data/USDA_sr_legacy.json` before running ingestion. The system will work without it but with a smaller food database.

## Machine Learning Models

The application supports optional ML models for better intent classification and named entity recognition:

### Models Directory Structure

```
backend/models/
├── intent.joblib           # Intent classification model (optional)
└── ner_hf/                 # HuggingFace NER model (optional)
    ├── config.json
    ├── pytorch_model.bin
    └── ...
```

### Training Models

**Note**: Models are NOT included in the repository. Users must train them with their own labeled data.

#### 1. Intent Classification

```bash
# Create labeled data: backend/data/intent_labeled.jsonl
# Format: {"text": "how many calories in rice?", "label": "calorie_query"}

# Train model
docker-compose exec backend python scripts/train_intent.py

# Output: models/intent.joblib
```

#### 2. Named Entity Recognition (CRF)

```bash
# Create labeled data: backend/data/ner_labeled.jsonl
# Format: {"tokens": ["how", "many", "calories"], "labels": ["O", "O", "O"]}

# Train model
docker-compose exec backend python scripts/train_ner_crf.py

# Output: models/ner_crf.joblib
```

#### 3. HuggingFace NER (Advanced)

For better NER, you can fine-tune a transformer model:

```bash
# Use your own training script or HuggingFace trainer
# Save model to backend/models/ner_hf/

# Or use a pre-trained model from HuggingFace Hub
# Set HF_NER_MODEL in .env to the model ID
```

### Safe Fallbacks

The application gracefully handles missing models:
- **No Intent Model**: Assumes all queries are calorie queries
- **No NER Model**: Returns empty entity lists (relies on fuzzy matching)
- System continues to function with reduced accuracy

## LLM Integration (Optional)

To enable ingredient suggestions for missing dishes:

1. Get an API key from your LLM provider (e.g., OpenAI)
2. Set in `.env`:
   ```bash
   LLM_API_KEY=your_actual_api_key_here  # add key here
   ```
3. The LLM will ONLY suggest ingredient names, never calories
4. Calories are always calculated from the USDA database

**Security Note**: Never commit API keys to the repository!

## API Endpoints

### Calculate Calories

```bash
POST /api/calculate
Content-Type: application/json

{
  "query": "fajita with extra olive oil",
  "session_id": "optional-session-id"
}

Response:
{
  "session_id": "uuid",
  "needs_clarification": false,
  "dish": "fajita",
  "ingredients": [
    {"name": "chicken", "weight_g": 150, "calories": 247.5},
    {"name": "olive oil", "weight_g": 13.5, "calories": 119.5, "added": true}
  ],
  "total_calories": 367.0,
  "notes": ["Added 13.5g olive oil"]
}
```

### Get Missing Dishes Log

```bash
GET /api/missing

Response: [
  {
    "user_query": "mansaf",
    "payload": {...},
    "suggested_ingredients": [...],
    "created_at": "2024-01-01T12:00:00"
  }
]
```

## Development

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export POSTGRES_HOST=localhost
export POSTGRES_DB=calories
export POSTGRES_USER=calories
export POSTGRES_PASSWORD=supersecret
export REDIS_URL=redis://localhost:6379/0
# ... other vars from .env.example

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## Database Schema

### Tables

- **usda_items**: USDA food items with calories and macros
- **dishes**: Named dishes with metadata
- **dish_ingredients**: Ingredients for each dish with default weights
- **synonyms**: Term normalization (Arabic/Franco/English)
- **unit_conversions**: Unit to grams conversions (generic + per-ingredient)
- **missing_dishes**: Log of queries for unknown dishes

### Indexes

- GIN trigram indexes on `usda_items.name`, `dishes.dish_name`, `dish_ingredients.ingredient_name`
- Standard B-tree indexes on foreign keys and frequently queried columns

## Configuration

### Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `POSTGRES_*`: Database connection
- `REDIS_URL`: Redis cache connection
- `HF_NER_MODEL`: Path or HuggingFace Hub ID for NER model
- `INTENT_MODEL_PATH`: Path to intent classification model
- `LLM_API_KEY`: Optional LLM API key for ingredient suggestions

### Unit Conversions

Unit conversions are stored in the database and can be customized:

```python
# Generic: 1 tbsp = 15g
# Olive oil specific: 1 tbsp = 13.5g
# Tomato: 1 piece = 123g
```

Add more conversions via the database or by editing `scripts/populate_reference_data.py`.

## Observability

### Logging

Structured logging is enabled in the backend:

```python
logger.info(f"Processing query: {query}")
logger.error(f"Error occurred: {error}", exc_info=True)
```

### Metrics (Placeholder)

Metrics hooks are present in the code but not connected to external services:

```python
# TODO: Add metrics collection here
# metrics.increment("queries.total")
# metrics.histogram("queries.calories", total_calories)
```

To enable metrics:
1. Choose a metrics backend (Prometheus, StatsD, etc.)
2. Install the client library
3. Uncomment and implement metrics calls in `main.py`

## Troubleshooting

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Verify connection from backend
docker-compose exec backend python -c "from db import engine; print(engine.connect())"
```

### Frontend Can't Connect to Backend

1. Check CORS settings in `backend/main.py`
2. Verify backend is running: `curl http://localhost:8000/health`
3. Check frontend environment: `frontend/src/environments/environment.ts`

### Models Not Loading

This is expected if models are not trained. The system will use fallbacks:

```
Warning: Intent model not found at models/intent.joblib, using fallback
Warning: NER model not found at models/ner_hf, using fallback
```

Train models as described in the "Machine Learning Models" section.

### pg_trgm Extension Error

If you see errors about pg_trgm:

```bash
# Manually enable in PostgreSQL
docker-compose exec postgres psql -U calories -d calories -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

## Testing

```bash
# Backend tests (add pytest configuration as needed)
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Security Notes

- ✅ No secrets committed to repository
- ✅ Environment variables used for configuration
- ✅ LLM API key with placeholder comment
- ✅ CORS configured for specific origins
- ✅ Input validation in API endpoints
- ⚠️ Change default passwords in production
- ⚠️ Use HTTPS in production
- ⚠️ Restrict CORS to specific domains in production

## Production Deployment

### Recommendations

1. **Database**: Use managed PostgreSQL service (AWS RDS, Azure Database, etc.)
2. **Redis**: Use managed Redis service
3. **Backend**: Deploy to Kubernetes, AWS ECS, or similar
4. **Frontend**: Deploy to CDN (CloudFront, Netlify, Vercel)
5. **Secrets**: Use secrets management (AWS Secrets Manager, Vault)
6. **Monitoring**: Add Prometheus + Grafana for metrics
7. **Logging**: Use centralized logging (ELK, CloudWatch)
8. **SSL/TLS**: Terminate at load balancer

### Docker Compose Production Mode

```bash
# Update docker-compose.yml for production
# - Use production images
# - Add resource limits
# - Configure restart policies
# - Use secrets instead of env vars
# - Add health checks

docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- GitHub Issues: [Add link]
- Email: [Add email]
- Documentation: [Add docs link]
