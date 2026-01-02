# Backend Chatbot with OpenAI GPT Integration

This is a new backend service that uses OpenAI GPT API for parsing user food queries and calculating calories from the USDA dataset.

## Features

- **OpenAI GPT Integration**: Parses natural language food queries using GPT-4o-mini
- **Intelligent Fallbacks**: 
  1. OpenAI GPT parsing
  2. Fuzzy string matching against dish database
  3. Simple keyword-based entity extraction
- **Nutritional Calculation**: Returns detailed macro breakdown (calories, protein, fat, carbs)
- **Modification Handling**: Supports adding/removing ingredients
- **Missing Dish Logging**: Logs dishes not found in database for admin review
- **Admin API**: Endpoints for managing dishes and viewing missing requests

## API Endpoints

### Chat Endpoint
```
POST /api/chat
```
Main endpoint to parse food queries and calculate nutrition.

Request:
```json
{
  "query": "chicken shawarma wrap without french fries",
  "session_id": "optional-session-id"
}
```

Response:
```json
{
  "food_item": "Chicken Shawarma Wrap",
  "ingredients": [
    {
      "name": "Chicken, broiler, breast, meat only, raw",
      "weight_g": 150,
      "calories": 165,
      "protein_g": 31.0,
      "fat_g": 3.6,
      "carbs_g": 0.0
    }
  ],
  "totals": {
    "weight_g": 297,
    "calories": 515,
    "protein_g": 35,
    "fat_g": 18,
    "carbs_g": 65
  },
  "notes": [
    "Found 'Chicken Shawarma Wrap' in database",
    "Removed: french fries"
  ]
}
```

### Dish Management
```
GET  /api/dishes              - List all dishes
GET  /api/dishes/{name}       - Get specific dish
POST /api/dishes              - Add new dish (admin)
GET  /api/missing-dishes      - Get logged missing dishes
```

### USDA Search
```
GET /api/usda/search?q={query} - Search USDA ingredients (autocomplete)
```

## Environment Variables

Add these to your `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
USDA_FOUND_PATH=data/USDA_foundation.json
DISHES_XLSX_PATH=data/dishes.xlsx
```

## Running Locally

```bash
cd backend_chatbot
pip install -r requirements.txt
python main.py
```

The API will be available at `http://localhost:8001`

## Running with Docker

```bash
docker-compose up backend_chatbot
```

## Architecture

```
backend_chatbot/
├── main.py                 # FastAPI app with all endpoints
├── config.py              # Settings and env vars
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container definition
├── models/
│   └── schemas.py        # Pydantic models
├── services/
│   ├── openai_service.py  # OpenAI GPT integration
│   ├── dish_service.py    # Dish lookup and calculation
│   ├── usda_lookup.py     # USDA dataset search
│   ├── fallback_service.py # ML fallback when GPT fails
│   └── missing_logger.py  # Log missing dishes
└── data/                  # Symlinks to USDA and dishes data
```

## How It Works

1. **User Query**: User sends a natural language query like "fajita without french fries"
2. **GPT Parsing**: OpenAI GPT parses the query into structured format:
   - Food item name
   - Modifications (add/remove ingredients)
   - Suggested ingredients with USDA names
3. **Dish Lookup**: System searches for dish in local database by name
4. **Fallback**: If GPT fails, uses fuzzy matching or simple keyword extraction
5. **Calculation**: 
   - Uses dish ingredients if found
   - Otherwise uses GPT-suggested ingredients
   - Applies modifications (remove/add items)
   - Looks up nutritional data from USDA dataset
6. **Response**: Returns detailed breakdown with macros

## Missing Dish Logging

When a dish is not found in the database, the system logs:
- Dish name
- User's original query
- GPT-suggested ingredients
- Timestamp

Admins can review these logs and add missing dishes via the admin panel.

## GPT Prompt Design

The GPT system prompt instructs the model to:
- Use EXACT USDA naming conventions (e.g., "Chicken, broiler, breast, meat only, raw")
- Return structured JSON with food item, modifications, and ingredients
- Parse removal keywords: "without", "no", "bala", "بدون"
- Parse addition keywords: "add", "with extra"

## Differences from Original Backend

| Feature | Original Backend | Backend Chatbot |
|---------|-----------------|-----------------|
| NLP | Custom NER + Intent models | OpenAI GPT |
| Dish Lookup | By ID | By Name |
| Fallback | Rule-based | Multi-level (GPT → Fuzzy → Keywords) |
| API Port | 8000 | 8001 |
| Macros | Calories only | Calories + Protein + Fat + Carbs |

## Admin Panel

The frontend admin panel allows:
- View all dishes in database
- View missing dish requests
- Add new dishes with USDA ingredient search (autocomplete)
- Use suggested ingredients from missing dish logs

Access at: `http://localhost:4200/admin` (after implementing routing)
