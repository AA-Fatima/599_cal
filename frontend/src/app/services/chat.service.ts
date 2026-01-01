import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private baseUrl = environment.apiUrl || 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  calculate(query: string, sessionId?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/calculate`, { query, session_id: sessionId });
  }
  
  getMissing(): Observable<any[]> {
    return this.http.get<any[]>(`${this.baseUrl}/missing`);
  }
}