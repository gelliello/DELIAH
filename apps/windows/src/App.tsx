import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, Settings, Cpu, Database, Brain } from 'lucide-react';
import './App.css';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  taskType?: string;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [connected, setConnected] = useState(false);
  const [activeModel, setActiveModel] = useState('general');
  const [showSettings, setShowSettings] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      const data = await response.json();
      setConnected(data.status === 'healthy');
    } catch {
      setConnected(false);
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          mode: activeModel,
        }),
      });

      const data = await response.json();

      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: data.reply,
        timestamp: new Date(),
        taskType: data.task_type,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">
          <Brain size={24} />
          <h1>DELIAH</h1>
          <span className={`status ${connected ? 'connected' : 'disconnected'}`}>
            {connected ? 'Online' : 'Offline'}
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
          <button onClick={() => setShowSettings(!showSettings)}>
            <Settings size={20} />
          </button>
        </div>
      </header>

      <main className="chat-container">
        <div className="messages">
          {messages.length === 0 && (
            <div className="welcome">
              <Brain size={48} />
              <h2>DELIAH</h2>
              <p>Your personal AI assistant</p>
              <p className="subtitle">How can I help you today?</p>
            </div>
          )}
          <AnimatePresence>
            {messages.map(msg => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className={`message ${msg.role}`}
              >
                <div className="message-avatar">
                  {msg.role === 'user' ? 'You' : 'D'}
                </div>
                <div className="message-content">
                  <div className="message-header">
                    <span className="sender">
                      {msg.role === 'user' ? 'You' : 'DELIAH'}
                    </span>
                    {msg.taskType && (
                      <span className="task-type">{msg.taskType}</span>
                    )}
                  </div>
                  <p>{msg.content}</p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
          <div ref={messagesEndRef} />
        </div>

        <div className="input-area">
          <div className="input-wrapper">
            <textarea
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="Ask DELIAH anything..."
              rows={1}
            />
            <div className="input-actions">
              <button className="send-btn" onClick={sendMessage} disabled={!input.trim()}>
                <Send size={18} />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
