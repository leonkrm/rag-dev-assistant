export interface SourceRef {
  document_path: string;
  snippet: string;
  score: number;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceRef[];
  pending?: boolean;
}

export interface ChatRequest {
  conversation_id?: string | null;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  sources: SourceRef[];
}
