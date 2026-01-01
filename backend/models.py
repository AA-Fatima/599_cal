from sqlalchemy import Column, Integer, String, Float, JSON
from db import Base

class UsdaItem(Base):
    __tablename__ = "usda_items"
    fdc_id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    alt_names = Column(JSON)
    per_100g_calories = Column(Float)
    macros = Column(JSON)

class Dish(Base):
    __tablename__ = "dishes"
    dish_id = Column(Integer, primary_key=True)
    dish_name = Column(String, index=True)
    country = Column(String)
    date_accessed = Column(String)

class DishIngredient(Base):
    __tablename__ = "dish_ingredients"
    id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, index=True)
    usda_fdc_id = Column(Integer)
    ingredient_name = Column(String)
    default_weight_g = Column(Float)