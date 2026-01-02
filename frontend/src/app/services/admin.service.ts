import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

export interface Ingredient {
  name: string;
  usda_fdc_id?: number;
  weight_g: number;
}

export interface Dish {
  dish_id: number;
  dish_name: string;
  country: string;
  ingredients: Ingredient[];
}

export interface MissingDish {
  dish_name: string;
  timestamp: string;
  user_query: string;
  gpt_suggested_ingredients: string[];
}

export interface UsdaSearchResult {
  fdc_id: number;
  name: string;
  score: number;
}

@Injectable({ providedIn: 'root' })
export class AdminService {
  private baseUrl = 'http://localhost:8001/api';

  constructor(private http: HttpClient) {}

  getDishes(): Observable<{ total: number; dishes: Dish[] }> {
    return this.http.get<{ total: number; dishes: Dish[] }>(`${this.baseUrl}/dishes`);
  }

  getDish(name: string): Observable<Dish> {
    return this.http.get<Dish>(`${this.baseUrl}/dishes/${encodeURIComponent(name)}`);
  }

  createDish(dish: { dish_name: string; country: string; ingredients: any[] }): Observable<any> {
    return this.http.post(`${this.baseUrl}/dishes`, dish);
  }

  getMissingDishes(): Observable<{ total: number; missing_dishes: MissingDish[] }> {
    return this.http.get<{ total: number; missing_dishes: MissingDish[] }>(`${this.baseUrl}/missing-dishes`);
  }

  searchUsda(query: string): Observable<{ query: string; count: number; results: UsdaSearchResult[] }> {
    return this.http.get<{ query: string; count: number; results: UsdaSearchResult[] }>(
      `${this.baseUrl}/usda/search?q=${encodeURIComponent(query)}`
    );
  }
}
