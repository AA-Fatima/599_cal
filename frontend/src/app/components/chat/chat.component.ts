import { Component } from '@angular/core';
import { ChatService } from '../../services/chat.service';

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.css']
})
export class ChatComponent {
  messages: { from: 'user'|'bot', text: string }[] = [];
  input = '';
  sessionId: string | undefined;

  constructor(private chat: ChatService) {}

  send() {
    const text = this.input.trim();
    if (!text) return;
    this.messages.push({ from: 'user', text });
    this.input = '';
    this.chat.calculate(text, this.sessionId).subscribe(res => {
      this.sessionId = res.session_id;
      if (res.needs_clarification) {
        this.messages.push({ from: 'bot', text: res.message });
      } else {
        const breakdown = (res.ingredients || []).map((i:any) =>
          `${i.name}: ${i.weight_g}g → ${i.calories} kcal${i.added?' (added)':''}${i.removed?' (removed)':''}`
        ).join('\n');
        const reply = `Dish: ${res.dish}\nTotal: ${res.total_calories} kcal\n${breakdown}`;
        this.messages.push({ from: 'bot', text: reply });
      }
    });
  }
}