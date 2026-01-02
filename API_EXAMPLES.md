# API Examples

This file contains example API calls for both backends using curl.

## Backend Chatbot (Port 8001)

### 1. Chat Endpoint - Parse Food Query

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how many calories in chicken shawarma wrap"
  }'
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
  "notes": ["Found 'Chicken Shawarma Wrap' in database"]
}
```

### 2. Chat with Modifications

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "query": "fajita without french fries"
  }'
```

### 3. List All Dishes

```bash
curl http://localhost:8001/api/dishes
```

### 4. Get Specific Dish

```bash
curl http://localhost:8001/api/dishes/Fajita
```

### 5. Search USDA Ingredients

```bash
curl "http://localhost:8001/api/usda/search?q=chicken&limit=10"
```

Response:
```json
[
  {
    "fdc_id": 171477,
    "name": "Chicken, broiler, breast, meat only, raw",
    "score": 95.5
  }
]
```

### 6. Add New Dish (Admin)

```bash
curl -X POST http://localhost:8001/api/dishes \
  -H "Content-Type: application/json" \
  -d '{
    "dish_name": "Greek Salad",
    "country": "Greece",
    "ingredients": [
      {
        "usda_name": "Tomatoes, grape, raw",
        "weight_g": 150
      },
      {
        "usda_name": "Oil, olive, salad or cooking",
        "weight_g": 15
      },
      {
        "usda_name": "Cheese, feta",
        "weight_g": 50
      }
    ]
  }'
```

### 7. Get Missing Dishes

```bash
curl http://localhost:8001/api/missing-dishes
```

Response:
```json
[
  {
    "dish_name": "Thai Green Curry",
    "user_query": "calories in thai green curry",
    "gpt_suggested_ingredients": [
      "Chicken, broiler, breast, meat only, raw",
      "Coconut milk, raw",
      "Peppers, hot chili, green, raw"
    ],
    "timestamp": "2024-01-02T14:30:00.000Z"
  }
]
```

## Original Backend (Port 8000)

### 1. Calculate Calories

```bash
curl -X POST http://localhost:8000/api/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how many calories in hummus",
    "session_id": "optional-session-id"
  }'
```

### 2. Get Missing Queries

```bash
curl http://localhost:8000/api/missing
```

## Testing with Python Requests

```python
import requests

# Chat endpoint
response = requests.post(
    "http://localhost:8001/api/chat",
    json={"query": "fajita without french fries"}
)
data = response.json()
print(f"Total calories: {data['totals']['calories']}")

# Search USDA
response = requests.get(
    "http://localhost:8001/api/usda/search",
    params={"q": "chicken", "limit": 5}
)
ingredients = response.json()
for ing in ingredients:
    print(f"{ing['name']} (score: {ing['score']})")

# Add dish
response = requests.post(
    "http://localhost:8001/api/dishes",
    json={
        "dish_name": "Caesar Salad",
        "country": "Italy",
        "ingredients": [
            {"usda_name": "Lettuce, romaine, raw", "weight_g": 100},
            {"usda_name": "Cheese, parmesan, grated", "weight_g": 20}
        ]
    }
)
dish = response.json()
print(f"Added dish: {dish['dish_name']} - {dish['calories']} kcal")
```

## Testing with JavaScript/Fetch

```javascript
// Chat endpoint
fetch('http://localhost:8001/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: 'how many calories in fajita'
  })
})
.then(res => res.json())
.then(data => {
  console.log(`Total calories: ${data.totals.calories}`);
  console.log(`Ingredients: ${data.ingredients.length}`);
});

// Search USDA
fetch('http://localhost:8001/api/usda/search?q=tomato&limit=5')
  .then(res => res.json())
  .then(results => {
    results.forEach(ing => {
      console.log(`${ing.name} (FDC: ${ing.fdc_id})`);
    });
  });
```

## Using with HTTPie

If you have HTTPie installed:

```bash
# Chat
http POST localhost:8001/api/chat query="fajita without french fries"

# Search USDA
http GET localhost:8001/api/usda/search q==chicken limit==10

# Add dish
http POST localhost:8001/api/dishes \
  dish_name="Mediterranean Bowl" \
  country="Mediterranean" \
  ingredients:='[
    {"usda_name": "Hummus, commercial", "weight_g": 100},
    {"usda_name": "Tomatoes, grape, raw", "weight_g": 80}
  ]'
```

## Response Status Codes

- `200 OK` - Successful request
- `400 Bad Request` - Invalid input (e.g., missing required fields)
- `404 Not Found` - Resource not found (e.g., dish doesn't exist)
- `500 Internal Server Error` - Server error

## Error Response Format

```json
{
  "detail": "Could not understand your query. Please try rephrasing with a specific food or dish name."
}
```

## Common Query Patterns

### Simple Queries
- "calories in fajita"
- "how many calories in hummus"
- "nutritional info for chicken shawarma"

### With Modifications
- "fajita without french fries"
- "shawarma wrap, no mayo"
- "add extra tomatoes to my salad"

### Specific Amounts
- "200 grams of chicken breast"
- "1 cup of rice"
- "2 tablespoons of olive oil"

## API Documentation

For interactive API documentation:
- Swagger UI: http://localhost:8001/docs
- ReDoc: http://localhost:8001/redoc
