import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User } from 'lucide-react';

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hi there! I am the Smart Payment Recovery AI Assistant. You can ask me questions about this project, the data, or how the recovery process works.' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const history = messages.filter(m => m.role !== 'assistant' || m.content !== messages[0].content);
      const res = await axios.post('http://localhost:8000/chat', {
        message: userMessage.content,
        history: history.map(m => ({ role: m.role, content: m.content }))
      });
      
      setMessages(prev => [...prev, { role: 'assistant', content: res.data.reply }]);
    } catch (err) {
      setMessages(prev => [...prev, { role: 'assistant', content: 'Error: Could not connect to the assistant backend.' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="chatbot-window glass-panel"
      style={{
        display: 'flex',
        flexDirection: 'column',
        height: '600px',
        overflow: 'hidden',
        animation: 'fadeInUp 0.5s ease-out forwards'
      }}
    >
      {/* Header */}
      <div className="chatbot-header" style={{
        padding: '16px 24px',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        alignItems: 'center',
        background: 'rgba(108, 99, 255, 0.2)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Bot size={24} color="#6c63ff" />
          <h3 style={{ margin: 0, fontSize: '1.2rem', fontWeight: 600 }}>AI Assistant</h3>
        </div>
      </div>

      {/* Messages */}
      <div className="chatbot-messages" style={{
        flex: 1,
        padding: '24px',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {messages.map((msg, idx) => (
          <div 
            key={idx} 
            style={{
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '85%',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.85rem',
              color: 'rgba(255,255,255,0.5)',
              flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
            }}>
              {msg.role === 'user' ? <User size={14} /> : <Bot size={14} />}
              {msg.role === 'user' ? 'You' : 'Assistant'}
            </div>
            <div style={{
              background: msg.role === 'user' ? '#6c63ff' : 'rgba(255,255,255,0.1)',
              padding: '12px 18px',
              borderRadius: '20px',
              borderTopRightRadius: msg.role === 'user' ? '4px' : '20px',
              borderTopLeftRadius: msg.role === 'assistant' ? '4px' : '20px',
              fontSize: '1rem',
              lineHeight: '1.5'
            }}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div style={{
            alignSelf: 'flex-start',
            background: 'rgba(255,255,255,0.1)',
            padding: '12px 18px',
            borderRadius: '20px',
            borderTopLeftRadius: '4px',
            fontSize: '1rem'
          }}>
            <span className="dot-typing">...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="chatbot-input" style={{
        padding: '16px 24px',
        borderTop: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        gap: '12px'
      }}>
        <input 
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask a question..."
          style={{
            flex: 1,
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.2)',
            borderRadius: '24px',
            padding: '12px 20px',
            color: 'white',
            outline: 'none',
            fontSize: '1rem'
          }}
        />
        <button 
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          style={{
            background: '#6c63ff',
            border: 'none',
            borderRadius: '50%',
            width: '48px',
            height: '48px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            cursor: (isLoading || !input.trim()) ? 'not-allowed' : 'pointer',
            opacity: (isLoading || !input.trim()) ? 0.5 : 1,
            transition: 'background 0.2s'
          }}
        >
          <Send size={20} style={{ marginLeft: '2px' }} />
        </button>
      </div>
    </div>
  );
};

export default Chatbot;
