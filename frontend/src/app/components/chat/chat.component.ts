import { Component, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { ChatService } from '../../services/chat.service';

interface Message {
  from: 'user' | 'bot';
  text: string;
  breakdown?: any;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent implements AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  
  messages: Message[] = [];
  input = '';
  sessionId: string | undefined;
  loading = false;
  private shouldScroll = false;

  constructor(private chat: ChatService) {
    // Load session from localStorage
    const savedSession = localStorage.getItem('chatbot_session_id');
    if (savedSession) {
      this.sessionId = savedSession;
    }
  }

  ngAfterViewChecked() {
    if (this.shouldScroll) {
      this.scrollToBottom();
      this.shouldScroll = false;
    }
  }

  send() {
    const text = this.input.trim();
    if (!text || this.loading) return;
    
    this.messages.push({ from: 'user', text });
    this.input = '';
    this.loading = true;
    this.shouldScroll = true;
    
    this.chat.calculate(text, this.sessionId).subscribe({
      next: (res) => {
        this.sessionId = res.session_id;
        // Save session to localStorage
        localStorage.setItem('chatbot_session_id', res.session_id);
        
        if (res.needs_clarification) {
          this.messages.push({ 
            from: 'bot', 
            text: res.message + (res.suggested_ingredients ? '\nSuggested: ' + JSON.stringify(res.suggested_ingredients) : '')
          });
        } else {
          this.messages.push({ 
            from: 'bot', 
            text: '', 
            breakdown: res 
          });
        }
        this.loading = false;
        this.shouldScroll = true;
      },
      error: (err) => {
        this.messages.push({ 
          from: 'bot', 
          text: 'Error: ' + (err.error?.detail || 'Could not connect to server') 
        });
        this.loading = false;
        this.shouldScroll = true;
      }
    });
  }

  private scrollToBottom(): void {
    try {
      this.messagesContainer.nativeElement.scrollTop = 
        this.messagesContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }
}