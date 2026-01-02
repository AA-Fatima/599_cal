# 599_cal - Calorie Calculator Chatbot

A comprehensive calorie calculation system with two backend implementations: a traditional ML-based approach and a modern OpenAI GPT-powered chatbot.

## Project Structure

```
599_cal/
├── backend/              # Original ML-based backend (Port 8000)
│   ├── services/        # NER, Intent detection, NLP services
│   ├── models.py        # Database models
│   ├── main.py          # FastAPI application
│   └── data/            # USDA & dish datasets
├── backend_chatbot/     # NEW: OpenAI GPT-powered backend (Port 8001)
│   ├── services/        # OpenAI, USDA lookup, dish services
│   ├── models/          # Pydantic schemas
│   ├── main.py          # FastAPI application
│   └── README.md        # Detailed documentation
├── frontend/            # Angular frontend (Port 4200)
│   └── src/app/
│       ├── components/  # Chat and Admin components
│       └── services/    # API services
└── docker-compose.yml   # Multi-container setup
```

## Two Backend Implementations

### Original Backend (`backend/`)
- **Port**: 8000
- **Approach**: Custom ML models (NER, Intent classification)
- **Features**: 
  - Intent detection
  - Named Entity Recognition
  - Rule-based parsing
  - Single nutrient (calories)

### Backend Chatbot (`backend_chatbot/`)
- **Port**: 8001
- **Approach**: OpenAI GPT-4o-mini
- **Features**:
  - Natural language understanding via GPT
  - Multi-level fallback system
  - Full macro breakdown (calories, protein, fat, carbs)
  - Missing dish logging
  - Admin API for dish management
  - USDA ingredient search

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for frontend development)
- OpenAI API key (for backend_chatbot)

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

### Running with Docker

Start all services:
```bash
docker-compose up
```

Services will be available at:
- Original Backend: http://localhost:8000
- Backend Chatbot: http://localhost:8001
- Frontend: http://localhost:4200
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### Running Locally

#### Backend Chatbot
```bash
cd backend_chatbot
pip install -r requirements.txt
python main.py
```

#### Original Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --port 8000
```

#### Frontend
```bash
cd frontend
# Setup and run based on your framework
```

## API Documentation

### Backend Chatbot Endpoints

#### Chat
```http
POST http://localhost:8001/api/chat
Content-Type: application/json

{
  "query": "chicken shawarma wrap without french fries",
  "session_id": "optional-session-id"
}
```

#### Dishes
```http
GET  http://localhost:8001/api/dishes              # List all dishes
GET  http://localhost:8001/api/dishes/Fajita       # Get specific dish
POST http://localhost:8001/api/dishes              # Add new dish
GET  http://localhost:8001/api/missing-dishes      # Get missing dishes
GET  http://localhost:8001/api/usda/search?q=chicken  # Search USDA
```

### Original Backend Endpoints

```http
POST http://localhost:8000/api/calculate
GET  http://localhost:8000/api/missing
```

## Features

### 🤖 OpenAI GPT Integration
- Parses natural language queries
- Understands modifications (add/remove ingredients)
- Returns USDA-standardized ingredient names

### 🔄 Intelligent Fallback System
1. **Primary**: OpenAI GPT parsing
2. **Fallback 1**: Fuzzy string matching against dish database
3. **Fallback 2**: Simple keyword-based entity extraction
4. **Final**: Helpful error message

### 📊 Nutritional Calculation
Returns complete macro breakdown:
- Calories (kcal)
- Protein (g)
- Fat (g)
- Carbohydrates (g)
- Weight (g)

### 📝 Missing Dish Logging
Automatically logs when dishes aren't found:
- Dish name
- User query
- GPT-suggested ingredients
- Timestamp

### 👨‍💼 Admin Panel
- View all dishes in database
- View missing dish requests
- Add new dishes with USDA autocomplete
- Use GPT suggestions for missing dishes

## Data Sources

### USDA Dataset
- **File**: `backend/data/USDA_foundation.json`
- **Items**: 300+ food items with nutritional data
- **Nutrients**: Calories, Protein, Fat, Carbohydrates

### Dishes Dataset
- **File**: `backend/data/dishes.xlsx`
- **Dishes**: 449 dishes
- **Fields**: dish_id, dish name, weight, calories, ingredients, country

## Development

### Testing Backend Chatbot

Run the test suite:
```bash
cd backend_chatbot
python test_services.py
```

Tests cover:
- USDA lookup and search
- Dish service and lookup
- Fallback mechanisms
- Nutritional calculations

### Adding New Dishes

Via API:
```bash
curl -X POST http://localhost:8001/api/dishes \
  -H "Content-Type: application/json" \
  -d '{
    "dish_name": "Greek Salad",
    "country": "Greece",
    "ingredients": [
      {"usda_name": "Tomatoes, grape, raw", "weight_g": 100},
      {"usda_name": "Oil, olive, salad or cooking", "weight_g": 15}
    ]
  }'
```

Via Admin Panel:
1. Navigate to http://localhost:4200/admin
2. Click "Add New Dish"
3. Fill in dish details
4. Search and select USDA ingredients
5. Submit

## Configuration

### Environment Variables

```env
# Database
POSTGRES_HOST=postgres
POSTGRES_DB=calories
POSTGRES_USER=calories
POSTGRES_PASSWORD=supersecret

# Redis
REDIS_URL=redis://redis:6379/0

# OpenAI (for backend_chatbot)
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4o-mini

# Data paths
USDA_FOUND_PATH=data/USDA_foundation.json
DISHES_XLSX_PATH=data/dishes.xlsx

# ML Models (for original backend)
HF_NER_MODEL=models/ner_hf
INTENT_MODEL_PATH=models/intent.joblib
```

## Architecture

### Request Flow (Backend Chatbot)

```
User Query
    ↓
OpenAI GPT (Parse query)
    ↓ (if fails)
Fuzzy Matching
    ↓ (if fails)
Keyword Extraction
    ↓
Dish Service (Lookup in database)
    ↓
USDA Lookup (Get nutritional data)
    ↓
Calculate Totals
    ↓
Return Response with Macros
```

## Docker Services

```yaml
services:
  postgres:       # Database (Port 5432)
  redis:          # Cache (Port 6379)
  backend:        # Original ML backend (Port 8000)
  backend_chatbot:# OpenAI GPT backend (Port 8001)
  frontend:       # Angular frontend (Port 4200)
```

## Known Limitations

1. **USDA Dataset Coverage**: Only ~300 items in foundation dataset. Some ingredients may not be found.
2. **Exact Name Matching**: USDA lookup requires close name matches. GPT helps by using standard USDA names.
3. **OpenAI Dependency**: Backend chatbot requires valid OpenAI API key. Fallbacks help when unavailable.
4. **Dish Addition**: Currently only in-memory. Needs persistence to Excel/database for permanent storage.

## Future Improvements

- [ ] Persist new dishes to Excel file
- [ ] Expand USDA dataset (include SR Legacy dataset)
- [ ] Add user authentication
- [ ] Support for meal planning
- [ ] Calorie tracking over time
- [ ] Multi-language support
- [ ] Recipe suggestions
- [ ] Barcode scanning integration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

[Add your license here]

## Support

For issues or questions:
- GitHub Issues: [Create an issue]
- Documentation: See `backend_chatbot/README.md` for detailed API docs

## Authors

[Add authors/contributors here]
