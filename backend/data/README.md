# Data Files

This directory contains the data files needed for the calorie chatbot.

## Required Files

### USDA_foundation.json
- **Size**: ~6.3 MB
- **Format**: JSON array
- **Source**: USDA Food Data Central - Foundation Foods
- **Structure**: 
  ```json
  [
    {
      "fdc_id": 12345,
      "description": "Chicken, broilers or fryers, breast, meat only, cooked, roasted",
      "foodNutrients": [
        {"nutrientId": 1008, "value": 165},
        {"nutrientId": 1003, "value": 31.02},
        ...
      ]
    }
  ]
  ```

### USDA_sr_legacy.json
- **Size**: Variable (can be empty array `[]`)
- **Format**: JSON array
- **Source**: USDA SR Legacy database (optional)
- **Structure**: Same as foundation

### dishes.xlsx
- **Size**: ~85 KB
- **Format**: Excel spreadsheet
- **Columns**:
  - `dish_id`: Unique integer ID
  - `dish name`: Name of the dish (e.g., "fajita", "tabbouleh")
  - `Country`: Country of origin
  - `date_accessed`: When data was collected
  - `ingredients`: JSON string with array of ingredients
    ```json
    [
      {"name": "chicken", "weight_g": 150, "usda_fdc_id": 171077},
      {"name": "peppers", "weight_g": 100}
    ]
    ```

## Data Sources

- **USDA FoodData Central**: https://fdc.nal.usda.gov/
  - Download Foundation Foods dataset
  - Export as JSON

- **Dishes**: Manually curated or scraped
  - Map ingredients to USDA FDC IDs for accuracy
  - Include default portions in grams

## Validation

To check if your data files are valid:

```bash
cd backend
python scripts/check_data.py
```
