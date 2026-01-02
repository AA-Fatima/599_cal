# Architecture Overview - Backend Chatbot

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INPUT                              │
│           "chicken shawarma without french fries"               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Angular)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ Chat View    │  │ Admin Panel  │  │ USDA Search  │         │
│  │ (existing)   │  │ (NEW)        │  │ (NEW)        │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP POST /api/chat
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND CHATBOT (Port 8001)                        │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Main                         │   │
│  │    POST /api/chat                                       │   │
│  │    GET  /api/dishes                                     │   │
│  │    POST /api/dishes                                     │   │
│  │    GET  /api/missing-dishes                             │   │
│  │    GET  /api/usda/search                                │   │
│  └─────────────────┬──────────────────────────────────────┘   │
│                     │                                           │
│  ┌─────────────────┴──────────────────────────────────────┐   │
│  │                SERVICE LAYER                             │   │
│  │                                                          │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  OpenAI Service                                   │  │   │
│  │  │  - Parse natural language query                   │  │   │
│  │  │  - Extract food item, modifications, ingredients │  │   │
│  │  │  - Return structured JSON                         │  │   │
│  │  └──────────────────┬───────────────────────────────┘  │   │
│  │                     │ Success                            │   │
│  │                     ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Dish Service                                     │  │   │
│  │  │  - Find dish in database (449 dishes)            │  │   │
│  │  │  - Get pre-defined ingredients                    │  │   │
│  │  │  - OR use GPT-suggested ingredients              │  │   │
│  │  │  - Apply modifications (add/remove)              │  │   │
│  │  └──────────────────┬───────────────────────────────┘  │   │
│  │                     │                                     │   │
│  │                     ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  USDA Lookup Service                              │  │   │
│  │  │  - Search by ingredient name (97 items)          │  │   │
│  │  │  - Fuzzy matching (80% threshold)                │  │   │
│  │  │  - Return nutritional data                        │  │   │
│  │  │    • Calories, Protein, Fat, Carbs               │  │   │
│  │  └──────────────────┬───────────────────────────────┘  │   │
│  │                     │                                     │   │
│  │                     ▼                                     │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Calculation Engine                               │  │   │
│  │  │  - Calculate per ingredient (weight × per 100g)  │  │   │
│  │  │  - Sum totals                                     │  │   │
│  │  │  - Generate notes                                 │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                          │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Fallback Service (if OpenAI fails)               │  │   │
│  │  │  1. Fuzzy string matching on dish names          │  │   │
│  │  │  2. Simple keyword extraction                     │  │   │
│  │  │  3. Helpful error message                         │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │                                                          │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Missing Logger                                   │  │   │
│  │  │  - Log dishes not found                           │  │   │
│  │  │  - Track timestamp, query, GPT suggestions       │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
│  ┌──────────────────┐  ┌──────────────────┐                   │
│  │ USDA Foundation  │  │ Dishes Database  │                   │
│  │ JSON (97 items)  │  │ Excel (449)      │                   │
│  └──────────────────┘  └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

## Request Flow Example

### Query: "chicken shawarma without french fries"

```
1. USER → Frontend
   Query: "chicken shawarma without french fries"

2. Frontend → Backend Chatbot
   POST /api/chat
   {
     "query": "chicken shawarma without french fries"
   }

3. Backend → OpenAI Service
   GPT-3.5-turbo parsing
   ↓
   Result: {
     "food_item": "Chicken Shawarma Wrap",
     "modifications": {
       "remove": ["French fries"]
     },
     "ingredients": []
   }

4. Backend → Dish Service
   Find "Chicken Shawarma Wrap" in database
   ↓
   Found! Use pre-defined ingredients:
   - Chicken breast, grilled
   - Pita bread
   - Mayonnaise
   - Pickles
   - French fries (REMOVE THIS)

5. Backend → USDA Lookup
   For each ingredient (except removed):
   - Chicken breast → 325.4 cal, 61.5g protein
   - Pita bread → 3.6 cal, 0.1g protein
   - etc.

6. Backend → Calculation
   Total: 329.0 cal, 63.0g protein, 6.5g fat, 0.6g carbs

7. Backend → Frontend
   {
     "food_item": "Chicken Shawarma Wrap",
     "ingredients": [...],
     "totals": {
       "calories": 329.0,
       "protein_g": 63.0,
       ...
     },
     "notes": [
       "Found 'Chicken Shawarma Wrap' in database",
       "Removed: French fries"
     ]
   }

8. Frontend → User
   Display: "Chicken Shawarma Wrap: 329 calories"
```

## Component Interaction

```
┌─────────────────┐
│  OpenAI GPT API │
└────────┬────────┘
         │ parse query
         ▼
┌─────────────────┐       ┌──────────────┐
│ OpenAI Service  │──────▶│ Dish Service │
└─────────────────┘       └──────┬───────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │ USDA Lookup  │
                          └──────┬───────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │ Calculation  │
                          └──────┬───────┘
                                  │
                                  ▼
                          ┌──────────────┐
                          │   Response   │
                          └──────────────┘

If OpenAI fails:
                    ┌─────────────────┐
                    │ Fallback Service│
                    └────────┬────────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
            ┌──────────┐      ┌──────────┐
            │  Fuzzy   │      │ Simple   │
            │ Matching │      │ Extract  │
            └──────────┘      └──────────┘
```

## Data Models

### Request Flow
```
ChatRequest
├── query: str
└── session_id?: str

↓ OpenAI Processing

GPTResponse
├── food_item: str
├── modifications
│   ├── remove: str[]
│   └── add: str[]
└── ingredients: str[]

↓ Dish Lookup + USDA Lookup

ChatResponse
├── food_item: str
├── ingredients: IngredientDetail[]
│   ├── usda_fdc_id: int
│   ├── name: str
│   ├── weight_g: float
│   ├── calories: float
│   ├── protein_g: float
│   ├── fat_g: float
│   └── carbs_g: float
├── totals: NutritionTotals
│   ├── weight_g: float
│   ├── calories: float
│   ├── protein_g: float
│   ├── fat_g: float
│   └── carbs_g: float
└── notes: str[]
```

## Deployment Architecture

```
┌──────────────────────────────────────────────────────┐
│                  Docker Compose                      │
│                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │ PostgreSQL │  │   Redis    │  │  Frontend  │   │
│  │ (port 5432)│  │ (port 6379)│  │ (port 4200)│   │
│  └────────────┘  └────────────┘  └────────────┘   │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │      Backend (Original)                     │    │
│  │      Port 8000                              │    │
│  │      ML-based parsing                       │    │
│  └────────────────────────────────────────────┘    │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │      Backend Chatbot (NEW)                  │    │
│  │      Port 8001                              │    │
│  │      OpenAI GPT-based parsing              │    │
│  └────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.110.0
- **Python**: 3.11+
- **AI**: OpenAI GPT-3.5-turbo
- **Data Processing**: Pandas, RapidFuzz
- **API**: RESTful with Pydantic validation

### Frontend
- **Framework**: Angular
- **Language**: TypeScript
- **HTTP Client**: HttpClient (RxJS)
- **Styling**: Custom CSS

### Infrastructure
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Database**: PostgreSQL 15
- **Cache**: Redis 7

### Data
- **USDA**: Foundation Foods (97 items, JSON)
- **Dishes**: 449 dishes (Excel/XLSX)
- **Format**: JSON responses

## Key Design Decisions

1. **Separate Backend**: Independent service on different port (8001)
   - Allows parallel operation with original backend
   - Easy to disable/enable
   - Clear separation of concerns

2. **3-Tier Fallback**: Never fails completely
   - Primary: OpenAI GPT
   - Secondary: Fuzzy matching
   - Tertiary: Simple extraction
   - Always returns useful response

3. **USDA Naming**: Exact format required
   - GPT trained to return proper format
   - "Grape leaves, raw" not "grape leaves"
   - Ensures accurate lookups

4. **Stateless API**: No session management
   - Simple, scalable
   - Can add sessions later if needed

5. **JSON Logging**: Simple file-based
   - Easy to implement
   - Can migrate to DB later
   - Good for MVP

## Performance Characteristics

- **USDA Lookup**: O(1) exact match, O(n) fuzzy
- **Dish Lookup**: O(1) with hash map
- **OpenAI Latency**: ~1-3 seconds
- **Fallback Latency**: <100ms
- **Total Response Time**: 1-3 seconds typical

## Security Features

- ✅ Environment variable for API key
- ✅ CORS configuration
- ✅ Pydantic input validation
- ✅ No SQL injection (NoSQL/JSON)
- ✅ Error messages don't leak secrets
- ✅ CodeQL security scan passed

## Scalability

Current: Single instance
- Handles ~10 req/sec
- No persistent state
- Stateless design

Future scaling:
- Add load balancer
- Multiple backend instances
- Cache OpenAI responses
- Rate limiting per user
