import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ChatService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) {}

  calculate(query: string, sessionId?: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/calculate`, { query, session_id: sessionId });
  }
}