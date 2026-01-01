import { Component, OnInit } from '@angular/core';
import { ChatService } from '../../services/chat.service';

interface Message {
  from: 'user' | 'bot';
  text: string;
  timestamp: Date;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements OnInit {
  messages: Message[] = [];
  input = '';
  sessionId: string | undefined;
  loading = false;

  constructor(private chat: ChatService) {}

  ngOnInit() {
    // Restore session from localStorage
    const savedSession = localStorage.getItem('chatSessionId');
    if (savedSession) {
      this.sessionId = savedSession;
    }
    
    // Show welcome message
    this.messages.push({
      from: 'bot',
      text: 'Welcome! I can help you calculate calories for dishes and ingredients. Try asking: "How many calories in fajita?" or "200g rice"',
      timestamp: new Date()
    });
  }

  send() {
    const text = this.input.trim();
    if (!text || this.loading) return;
    
    // Add user message
    this.messages.push({ 
      from: 'user', 
      text,
      timestamp: new Date()
    });
    this.input = '';
    this.loading = true;
    
    // Call backend
    this.chat.calculate(text, this.sessionId).subscribe({
      next: (res) => {
        this.loading = false;
        this.sessionId = res.session_id;
        
        // Persist session
        if (this.sessionId) {
          localStorage.setItem('chatSessionId', this.sessionId);
        }
        
        // Format bot response
        let reply = '';
        if (res.needs_clarification) {
          reply = res.message || 'I need more information.';
          if (res.suggested_ingredients) {
            reply += '\n\nSuggested ingredients: ' + JSON.stringify(res.suggested_ingredients);
          }
        } else {
          reply = `🍽️ Dish: ${res.dish}\n\n`;
          
          if (res.ingredients && res.ingredients.length > 0) {
            reply += '📊 Breakdown:\n';
            res.ingredients.forEach((ing: any) => {
              const badge = ing.added ? ' 🆕' : ing.removed ? ' ❌' : '';
              reply += `  • ${ing.name}: ${ing.weight_g}g → ${ing.calories} kcal${badge}\n`;
            });
          }
          
          reply += `\n🔥 Total: ${res.total_calories} kcal`;
          
          if (res.notes && res.notes.length > 0) {
            reply += '\n\nℹ️ Notes:\n';
            res.notes.forEach((note: string) => {
              reply += `  • ${note}\n`;
            });
          }
        }
        
        this.messages.push({ 
          from: 'bot', 
          text: reply,
          timestamp: new Date()
        });
      },
      error: (err) => {
        this.loading = false;
        console.error('Error:', err);
        this.messages.push({ 
          from: 'bot', 
          text: '⚠️ Sorry, an error occurred. Please try again.',
          timestamp: new Date()
        });
      }
    });
  }
  
  clearChat() {
    if (confirm('Clear chat history?')) {
      this.messages = [];
      this.sessionId = undefined;
      localStorage.removeItem('chatSessionId');
      this.ngOnInit();
    }
  }
}