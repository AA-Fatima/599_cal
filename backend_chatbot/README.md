# Backend Chatbot - AI-Powered Calorie Calculator

This is a new backend implementation that uses OpenAI GPT API for parsing user food queries and calculating calories from the USDA dataset.

## Features

- **OpenAI GPT Integration**: Parses natural language food queries into structured data
- **USDA Dataset**: Comprehensive nutritional information with exact USDA naming conventions
- **Dish Management**: Pre-defined dishes with ingredients
- **Modification Handling**: Support for adding/removing ingredients
- **Fallback Mechanisms**: Fuzzy matching and simple extraction when OpenAI fails
- **Missing Dish Logging**: Track dishes not found in the database
- **Admin API**: Full CRUD operations for dish management

## API Endpoints

### Main Endpoints

- `POST /api/chat` - Parse query and calculate calories
- `GET /api/dishes` - List all dishes
- `GET /api/dishes/{name}` - Get specific dish
- `POST /api/dishes` - Add new dish (admin)
- `GET /api/missing-dishes` - Get logged missing dishes
- `GET /api/usda/search?q=` - Search USDA ingredients (autocomplete)

### Request/Response Format

#### POST /api/chat

**Request:**
```json
{
  "query": "Calculate calories for chicken shawarma without tahini",
  "session_id": "optional-session-id"
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
    "Removed: Tahini"
  ]
}
```

## Setup

### Environment Variables

Create a `.env` file with:

```env
OPENAI_API_KEY=your_openai_api_key_here
USDA_FOUND_PATH=data/USDA_foundation.json
DISHES_XLSX_PATH=data/dishes.xlsx
POSTGRES_HOST=postgres
POSTGRES_DB=calories
POSTGRES_USER=calories
POSTGRES_PASSWORD=supersecret
```

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### Docker

```bash
# Build
docker build -t backend_chatbot .

# Run
docker run -p 8001:8001 --env-file .env backend_chatbot
```

## Testing

```bash
# Run the test script
python test_api.py
```

This will test:
- USDA lookup service
- Dish service
- Calorie calculation
- Fallback mechanisms
- USDA autocomplete
- Modification handling

## Architecture

```
backend_chatbot/
├── main.py                  # FastAPI app with all endpoints
├── config.py               # Settings and environment variables
├── services/
│   ├── openai_service.py   # OpenAI GPT integration
│   ├── dish_service.py     # Dish lookup and calculation
│   ├── usda_lookup.py      # USDA dataset search by name
│   ├── fallback_service.py # Fallback when GPT fails
│   └── missing_logger.py   # Log missing dishes
├── models/
│   └── schemas.py          # Pydantic models for requests/responses
└── data/                   # Symlink to ../backend/data
```

## How It Works

1. **User Query**: User sends a natural language query (e.g., "chicken shawarma without tahini")

2. **OpenAI Processing**: Query is sent to GPT which returns:
   - Food item name
   - Modifications (add/remove)
   - Suggested ingredients (with USDA-exact names)

3. **Dish Lookup**: 
   - First, search for dish in local database by full name
   - If found, use pre-defined ingredients
   - If not found, use GPT-suggested ingredients

4. **Ingredient Lookup**:
   - For each ingredient, search USDA dataset by full name
   - Get nutritional data (calories, protein, fat, carbs)
   - Calculate based on weight

5. **Modification Handling**:
   - Remove ingredients from modifications.remove array
   - Add ingredients from modifications.add array

6. **Fallback Mechanisms**:
   - If OpenAI fails, use fuzzy string matching on dish names
   - If that fails, use simple keyword extraction
   - If all fails, return helpful error message

7. **Response**: Return structured JSON with exact format including all nutritional data

## USDA Naming Conventions

The system instructs GPT to use exact USDA naming conventions:

- Include descriptors: "raw", "cooked", "fresh"
- Use proper capitalization
- Include preparation methods
- Use commas for structure

Examples:
- ✓ "Grape leaves, raw"
- ✓ "Rice, white, long-grain, regular, raw, enriched"
- ✓ "Oil, olive, salad or cooking"
- ✗ "grape leaves"
- ✗ "olive oil"

## Admin Features

The admin API allows:
- Viewing all dishes
- Viewing missing dishes (logged when not found)
- Adding new dishes with ingredients
- Searching USDA ingredients for autocomplete

## Future Enhancements

- Database persistence for dishes (currently in-memory after adding)
- User authentication for admin endpoints
- Rate limiting for OpenAI API
- Caching for frequently requested dishes
- Support for custom portion sizes
- Multi-language support
