from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
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
    id = Column(Integer, primary_key=True, autoincrement=True)
    dish_id = Column(Integer, ForeignKey("dishes.dish_id"), index=True)
    usda_fdc_id = Column(Integer, nullable=True)
    ingredient_name = Column(String)
    default_weight_g = Column(Float)

class Synonym(Base):
    __tablename__ = "synonyms"
    id = Column(Integer, primary_key=True, autoincrement=True)
    term = Column(String, unique=True, index=True)
    canonical = Column(String, index=True)

class UnitConversion(Base):
    __tablename__ = "unit_conversions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    ingredient_group = Column(String, index=True)
    unit = Column(String)
    grams = Column(Float)

class MissingDish(Base):
    __tablename__ = "missing_dishes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_query = Column(Text)
    parsed = Column(JSON)
    suggested_ingredients = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now())