import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, Trash2 } from 'lucide-react';
import './App.css';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  taskType?: string;
  model?: string;
  streaming?: boolean;
}

const HINTS = [
  'Explain how neural networks learn',
  'Write a Python script to organize files',
  'Plan a weekly meal prep schedule',
  'What are the best practices for REST APIs?',
];

const BACKEND_URL = 'http://localhost:8000';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [connected, setConnected] = useState<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected');
  const [ollamaStatus, setOllamaStatus] = useState<'unknown' | 'ok' | 'down'>('unknown');
  const [activeModel, setActiveModel] = useState('general');
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Health check
  const checkHealth = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/health`);
      const data = await res.json();
      if (data.status === 'healthy') {
        setConnected('connected');
        setOllamaStatus(data.ollama === 'connected' ? 'ok' : 'down');
      } else {
        setConnected('error');
        setOllamaStatus('down');
      }
    } catch {
      setConnected('disconnected');
      setOllamaStatus('unknown');
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  // Cleanup
  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  const showError = (msg: string) => {
    setError(msg);
    setTimeout(() => setError(null), 4000);
  };

  // Send via regular POST (fallback)
  const sendViaHttp = useCallback(async (message: string) => {
    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');

    const assistantId = Date.now() + 1;
    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      streaming: true,
    };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      const res = await fetch(`${BACKEND_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, mode: activeModel }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data = await res.json();
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantId
            ? { ...m, content: data.reply, taskType: data.task_type, model: data.model, streaming: false }
            : m
        )
      );
    } catch (err) {
      setMessages(prev =>
        prev.map(m =>
          m.id === assistantId
            ? { ...m, content: 'Sorry, I encountered an error. Is the backend running?', streaming: false }
            : m
        )
      );
      showError('Failed to reach DELIAH backend');
    }
  }, [activeModel]);

  // Send via WebSocket (streaming)
  const sendViaWebSocket = useCallback((message: string) => {
    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: message,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setStreaming(true);

    const assistantId = Date.now() + 1;
    let fullContent = '';

    const assistantMessage: Message = {
      id: assistantId,
      role: 'assistant',
      content: '',
      timestamp: new Date(),
      streaming: true,
    };
    setMessages(prev => [...prev, assistantMessage]);

    try {
      const ws = new WebSocket(`ws://${new URL(BACKEND_URL).host}/ws/chat`);
      wsRef.current = ws;

      ws.onopen = () => {
        ws.send(JSON.stringify({ message }));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'chunk') {
          fullContent += data.content;
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantId
                ? { ...m, content: fullContent }
                : m
            )
          );
        } else if (data.type === 'done') {
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantId
                ? { ...m, streaming: false, taskType: data.task_type, model: data.model }
                : m
            )
          );
          setStreaming(false);
          ws.close();
        }
      };

      ws.onerror = () => {
        ws.close();
        // Fall back to HTTP
        setMessages(prev => prev.filter(m => m.id !== assistantId));
        setStreaming(false);
        sendViaHttp(message);
      };

      ws.onclose = () => {
        setStreaming(false);
        if (fullContent) {
          setMessages(prev =>
            prev.map(m =>
              m.id === assistantId
                ? { ...m, streaming: false }
                : m
            )
          );
        }
      };
    } catch {
      // Fall back to HTTP
      setMessages(prev => prev.filter(m => m.id !== assistantId));
      setStreaming(false);
      sendViaHttp(message);
    }
  }, [sendViaHttp]);

  const sendMessage = useCallback(() => {
    const trimmed = input.trim();
    if (!trimmed || streaming) return;

    if (connected === 'connected' || connected === 'error') {
      sendViaWebSocket(trimmed);
    } else {
      showError('Backend not connected. Please start the DELIAH server.');
    }
  }, [input, streaming, connected, sendViaWebSocket]);

  const clearChat = useCallback(async () => {
    try {
      await fetch(`${BACKEND_URL}/chat/clear`, { method: 'POST' });
    } catch {
      // Ignore
    }
    setMessages([]);
  }, []);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleHint = (hint: string) => {
    setInput(hint);
    inputRef.current?.focus();
  };

  const statusLabel =
    connected === 'connected'
      ? ollamaStatus === 'ok'
        ? 'Connected'
        : 'Backend OK, Ollama down'
      : connected === 'connecting'
      ? 'Connecting...'
      : connected === 'error'
      ? 'Backend error'
      : 'Offline';

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <div className="logo-icon">D</div>
          <h1>DELIAH</h1>
          <span className={`status ${connected === 'connected' ? 'connected' : connected === 'connecting' ? 'connecting' : 'disconnected'}`}>
            {statusLabel}
          </span>
        </div>
        <div className="header-actions">
          <div className="model-selector">
            {['general', 'coding', 'planning'].map(model => (
              <button
                key={model}
                className={`model-btn ${activeModel === model ? 'active' : ''}`}
                onClick={() => setActiveModel(model)}
              >
                {model}
              </button>
            ))}
          </div>
          <button className="header-btn" onClick={clearChat} title="Clear conversation">
            <Trash2 size={14} />
          </button>
        </div>
      </header>

      <main className="chat-container">
        <div className="messages">
          {messages.length === 0 ? (
            <div className="welcome">
              <div className="welcome-icon">D</div>
              <h2>DELIAH</h2>
              <p className="tagline">Your personal local intelligence assistant</p>
              <div className="welcome-hints">
                {HINTS.map((hint, i) => (
                  <button key={i} className="hint-btn" onClick={() => handleHint(hint)}>
                    {hint}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="messages-inner">
              {messages.map(msg => (
                <div key={msg.id} className={`message ${msg.role}`}>
                  <div className="message-avatar">
                    {msg.role === 'user' ? 'Y' : 'D'}
                  </div>
                  <div className="message-body">
                    <div className="message-header">
                      <span className="sender">
                        {msg.role === 'user' ? 'You' : 'DELIAH'}
                      </span>
                      {msg.taskType && (
                        <span className="task-badge">{msg.taskType}</span>
                      )}
                    </div>
                    <div className="message-content">
                      {msg.content || (msg.streaming ? (
                        <div className="typing-indicator">
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                          <span className="typing-dot" />
                        </div>
                      ) : null)}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              ref={inputRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={connected === 'connected' ? 'Ask DELIAH anything...' : 'Start the backend server to begin...'}
              rows={1}
              disabled={streaming}
            />
            <button
              className="send-btn"
              onClick={sendMessage}
              disabled={!input.trim() || streaming}
              title="Send message"
            >
              <Send size={16} />
            </button>
          </div>
          <div className="input-footer">
            <span className="input-hint">Enter to send, Shift+Enter for new line</span>
            <span className="model-info">
              Mode: {activeModel}
            </span>
          </div>
        </div>
      </main>

      {error && <div className="error-toast">{error}</div>}
    </div>
  );
}

export default App;
