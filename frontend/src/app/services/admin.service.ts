import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Dish {
  dish_id: number;
  dish_name: string;
  country: string;
  weight_g: number;
  calories: number;
  ingredients: any[];
}

export interface MissingDish {
  dish_name: string;
  user_query: string;
  gpt_suggested_ingredients: string[];
  timestamp: string;
}

export interface UsdaIngredient {
  fdc_id: number;
  name: string;
  score: number;
}

export interface AddDishRequest {
  dish_name: string;
  country: string;
  ingredients: {
    usda_name: string;
    weight_g: number;
  }[];
}

@Injectable({ providedIn: 'root' })
export class AdminService {
  private baseUrl = 'http://localhost:8001/api';

  constructor(private http: HttpClient) {}

  getDishes(): Observable<Dish[]> {
    return this.http.get<Dish[]>(`${this.baseUrl}/dishes`);
  }

  getMissingDishes(): Observable<MissingDish[]> {
    return this.http.get<MissingDish[]>(`${this.baseUrl}/missing-dishes`);
  }

  searchUsda(query: string): Observable<UsdaIngredient[]> {
    return this.http.get<UsdaIngredient[]>(`${this.baseUrl}/usda/search?q=${encodeURIComponent(query)}`);
  }

  addDish(dish: AddDishRequest): Observable<Dish> {
    return this.http.post<Dish>(`${this.baseUrl}/dishes`, dish);
  }
}
