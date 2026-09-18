import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ChatService } from '../services/chat.service';
import { ChatMessage } from '../models/chat.models';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent {
  messages: ChatMessage[] = [];
  draft = '';
  conversationId: string | null = null;
  isSending = false;

  constructor(private chatService: ChatService) {}

  send(): void {
    const text = this.draft.trim();
    if (!text || this.isSending) {
      return;
    }

    this.messages.push({ role: 'user', content: text });
    this.messages.push({ role: 'assistant', content: '', pending: true });
    this.draft = '';
    this.isSending = true;

    this.chatService
      .sendMessage({ conversation_id: this.conversationId, message: text })
      .subscribe({
        next: (res) => {
          this.conversationId = res.conversation_id;
          const last = this.messages[this.messages.length - 1];
          last.content = res.answer;
          last.sources = res.sources;
          last.pending = false;
          this.isSending = false;
        },
        error: () => {
          const last = this.messages[this.messages.length - 1];
          last.content = 'Не удалось получить ответ от сервера. Попробуйте ещё раз.';
          last.pending = false;
          this.isSending = false;
        },
      });
  }
}
