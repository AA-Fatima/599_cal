# 599 Calorie Calculator - AI-Powered Food Tracking

A comprehensive calorie calculation system with two backend implementations and an Angular frontend.

## Architecture Overview

```
599_cal/
├── backend/             # Original backend with ML-based parsing
├── backend_chatbot/     # NEW: OpenAI GPT-powered backend
├── frontend/            # Angular frontend with admin panel
└── docker-compose.yml   # Full stack deployment
```

## Features

### Backend Chatbot (NEW Implementation)

The new `backend_chatbot` uses OpenAI GPT for intelligent food query parsing:

- **Natural Language Processing**: GPT parses queries like "chicken shawarma without tahini"
- **USDA Dataset Integration**: Exact nutritional data from USDA Foundation Foods
- **Smart Modifications**: Add/remove ingredients with automatic calorie adjustment
- **3-Tier Fallback System**: GPT → Fuzzy Matching → Simple Extraction
- **Missing Dish Logging**: Automatically tracks dishes to add
- **Admin API**: Full CRUD operations for dish management

### Original Backend

The original backend uses ML models (NER + Intent Classification) for food parsing.

### Frontend

Angular-based UI with:
- Chat interface for calorie queries
- Admin dashboard for dish management
- USDA ingredient autocomplete
- Missing dishes tracking

## Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API Key (for backend_chatbot)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/AA-Fatima/599_cal.git
   cd 599_cal
   ```

2. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

3. **Start services**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Original Backend: http://localhost:8000
   - Backend Chatbot: http://localhost:8001
   - Frontend: http://localhost:4200

## API Documentation

### Backend Chatbot (Port 8001)

#### POST /api/chat
Calculate calories from natural language query.

**Request:**
```json
{
  "query": "chicken shawarma without french fries, add extra tomato"
}
```

**Response:**
```json
{
  "food_item": "Chicken Shawarma Wrap",
  "ingredients": [
    {
      "usda_fdc_id": 171477,
      "name": "Chicken, broiler or fryers, breast, skinless, boneless, meat only, cooked, braised",
      "weight_g": 196.0,
      "calories": 325.4,
      "protein_g": 61.5,
      "fat_g": 6.5,
      "carbs_g": 0.0
    }
  ],
  "totals": {
    "weight_g": 196.0,
    "calories": 325.4,
    "protein_g": 61.5,
    "fat_g": 6.5,
    "carbs_g": 0.0
  },
  "notes": [
    "Found 'Chicken Shawarma Wrap' in database",
    "Removed: French fries",
    "Added: Tomatoes, grape, raw"
  ]
}
```

#### GET /api/dishes
List all dishes in database.

#### GET /api/dishes/{name}
Get specific dish details.

#### POST /api/dishes
Add new dish (admin).

#### GET /api/missing-dishes
Get logged missing dishes.

#### GET /api/usda/search?q={query}
Search USDA ingredients (autocomplete).

### Original Backend (Port 8000)

#### POST /api/calculate
Calculate calories using ML-based parsing.

#### GET /api/missing
Get missing dishes log.

## Development

### Backend Chatbot

```bash
cd backend_chatbot

# Install dependencies
pip install -r requirements.txt

# Run tests
python test_api.py
python integration_test.py

# Start server
uvicorn main:app --reload --port 8001
```

### Original Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
ng serve
```

## Testing

### Backend Chatbot Tests

```bash
cd backend_chatbot

# Run all tests
python test_api.py         # Service layer tests
python integration_test.py # Full integration tests

# Test endpoints (requires running server)
./test_endpoints.sh
```

### Test Results

All tests pass with:
- 97 USDA items loaded
- 449 dishes in database
- All API endpoints functional
- Fallback mechanisms working
- Exact response format validated

## Data

### USDA Foundation Foods
- 97 foundation food items
- Complete nutritional data (calories, protein, fat, carbs)
- Searchable by exact name with fuzzy matching fallback

### Dishes Database
- 449 pre-defined dishes
- Each with ingredients and weights
- Stored in Excel format for easy management

## Configuration

### Environment Variables

```env
# OpenAI (required for backend_chatbot)
OPENAI_API_KEY=your_api_key_here

# Database
POSTGRES_HOST=postgres
POSTGRES_DB=calories
POSTGRES_USER=calories
POSTGRES_PASSWORD=supersecret

# Data Paths
USDA_FOUND_PATH=data/USDA_foundation.json
DISHES_XLSX_PATH=data/dishes.xlsx

# Redis (for original backend)
REDIS_URL=redis://redis:6379/0

# ML Models (for original backend)
HF_NER_MODEL=models/ner_hf
INTENT_MODEL_PATH=models/intent.joblib
```

## How It Works

### Backend Chatbot Flow

1. **User Query** → "chicken shawarma without french fries"
2. **OpenAI GPT** → Parses into structured JSON with USDA-exact ingredient names
3. **Dish Lookup** → Searches local database by full name
4. **Ingredient Processing** → Applies modifications (add/remove)
5. **USDA Lookup** → Gets nutritional data for each ingredient
6. **Calculation** → Computes totals based on weights
7. **Response** → Returns structured JSON with full breakdown

### Fallback System

If OpenAI fails:
1. **Fuzzy Matching** → Searches dishes by similarity
2. **Simple Extraction** → Keyword-based food detection
3. **Error Message** → Helpful suggestions for user

## Admin Panel

Access at `/admin` (frontend integration required):

- **Dishes View**: Browse all 449 dishes
- **Missing Dishes**: See what users requested but wasn't found
- **Add Dish**: Create new dish with USDA ingredient search
- **USDA Autocomplete**: Real-time ingredient search

## Deployment

### Docker

```bash
# Build and run all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

### Individual Services

Each backend can run independently:
- Original backend: port 8000
- Backend chatbot: port 8001
- Frontend can connect to either

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Add license information]

## Authors

- AA-Fatima

## Acknowledgments

- USDA Foundation Foods Database
- OpenAI GPT API
- FastAPI Framework
- Angular Framework
