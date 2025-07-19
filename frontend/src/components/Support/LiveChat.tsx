import React, { useState, useEffect, useRef } from 'react';

interface ChatMessage {
  id: string;
  message: string;
  sender: 'user' | 'support';
  timestamp: Date;
  isRead: boolean;
  type?: 'text' | 'file' | 'system';
}

interface LiveChatProps {
  isOpen: boolean;
  onClose: () => void;
}

interface QuickAction {
  id: string;
  title: string;
  action: string;
  icon: string;
}

const LiveChat: React.FC<LiveChatProps> = ({ isOpen, onClose }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [chatStatus, setChatStatus] = useState<'connecting' | 'connected' | 'disconnected'>('connecting');
  const [supportAgent] = useState({ name: 'Alex Johnson', status: 'online' });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const quickActions: QuickAction[] = [
    { id: '1', title: 'Connection Issues', action: 'I\'m having trouble connecting my MT5 account', icon: '🔗' },
    { id: '2', title: 'Algorithm Not Working', action: 'My algorithm is not working properly', icon: '🤖' },
    { id: '3', title: 'Risk Management Help', action: 'I need help setting up risk management', icon: '🛡️' },
    { id: '4', title: 'Performance Questions', action: 'I have questions about my trading performance', icon: '📊' }
  ];

  useEffect(() => {
    if (isOpen) {
      // Simulate connecting to chat
      setTimeout(() => {
        setChatStatus('connected');
        addSystemMessage('Connected to support. How can we help you today?');
      }, 1500);
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const addSystemMessage = (text: string) => {
    const systemMessage: ChatMessage = {
      id: Date.now().toString(),
      message: text,
      sender: 'support',
      timestamp: new Date(),
      isRead: true,
      type: 'system'
    };
    setMessages(prev => [...prev, systemMessage]);
  };

  const addSupportMessage = (text: string) => {
    setIsTyping(true);
    setTimeout(() => {
      const supportMessage: ChatMessage = {
        id: Date.now().toString(),
        message: text,
        sender: 'support',
        timestamp: new Date(),
        isRead: false,
        type: 'text'
      };
      setMessages(prev => [...prev, supportMessage]);
      setIsTyping(false);
    }, 1000 + Math.random() * 2000); // Random delay to simulate real typing
  };

  const sendMessage = (messageText: string = newMessage) => {
    if (!messageText.trim()) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      message: messageText,
      sender: 'user',
      timestamp: new Date(),
      isRead: true,
      type: 'text'
    };

    setMessages(prev => [...prev, userMessage]);
    setNewMessage('');

    // Simulate support responses
    setTimeout(() => {
      const responses = getContextualResponse(messageText);
      responses.forEach((response, index) => {
        setTimeout(() => addSupportMessage(response), index * 2000);
      });
    }, 500);
  };

  const getContextualResponse = (userMessage: string): string[] => {
    const message = userMessage.toLowerCase();
    
    if (message.includes('connection') || message.includes('connect') || message.includes('mt5')) {
      return [
        'I can help you with MT5 connection issues. Let me check a few things first.',
        'Can you tell me which broker you\'re trying to connect to? Also, please verify that your MT5 platform is running and logged in.',
        'Common solutions include: 1) Restarting MT5, 2) Checking internet connection, 3) Verifying broker allows API access. Would you like me to walk you through these steps?'
      ];
    } else if (message.includes('algorithm') || message.includes('trading') || message.includes('bot')) {
      return [
        'I\'d be happy to help with your algorithm issues. Can you provide more details about what specific problem you\'re experiencing?',
        'Is the algorithm failing to deploy, showing poor performance, or encountering errors? The more information you can provide, the better I can assist you.'
      ];
    } else if (message.includes('risk') || message.includes('loss') || message.includes('management')) {
      return [
        'Risk management is crucial for successful algorithmic trading. I can help you optimize your settings.',
        'For beginners, I recommend: Max Loss Per Trade: 1-2%, Daily Loss Limit: 3-5%, Position Size: 1-2% of account balance. Would you like me to explain how to configure these settings?'
      ];
    } else if (message.includes('performance') || message.includes('profit') || message.includes('loss')) {
      return [
        'Let me help you analyze your trading performance. Are you looking at specific metrics like ROI, win rate, or profit factor?',
        'I can also help you understand what constitutes good performance: Win Rate >60%, Profit Factor >1.5, and controlled drawdown <20%.'
      ];
    } else {
      return [
        'Thank you for your message. I\'m here to help with any questions about our trading platform.',
        'You can ask me about MT5 connections, algorithm setup, risk management, or performance analysis. What would you like to know more about?'
      ];
    }
  };

  const handleQuickAction = (action: string) => {
    sendMessage(action);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="chat-modal-enhanced" onClick={(e) => e.stopPropagation()}>
        <div className="chat-header-enhanced">
          <div className="support-agent-info">
            <div className="agent-avatar">
              <img src="/api/placeholder/40/40" alt={supportAgent.name} />
              <div className={`status-indicator ${supportAgent.status}`}></div>
            </div>
            <div className="agent-details">
              <h3>{supportAgent.name}</h3>
              <span className="agent-status">Support Specialist • {supportAgent.status}</span>
            </div>
          </div>
          <div className="chat-actions">
            <div className={`connection-status ${chatStatus}`}>
              <span className="status-dot"></span>
              {chatStatus === 'connecting' && 'Connecting...'}
              {chatStatus === 'connected' && 'Connected'}
              {chatStatus === 'disconnected' && 'Disconnected'}
            </div>
            <button onClick={onClose} className="close-chat-btn">✕</button>
          </div>
        </div>
        
        <div className="chat-messages-enhanced">
          {messages.length === 0 && (
            <div className="chat-welcome">
              <div className="welcome-avatar">
                <span>👋</span>
              </div>
              <h4>Welcome to Support Chat!</h4>
              <p>Hi there! I'm {supportAgent.name}, your support specialist. How can I help you today?</p>
              
              <div className="quick-actions">
                <h5>Quick Actions:</h5>
                <div className="quick-actions-grid">
                  {quickActions.map(action => (
                    <button
                      key={action.id}
                      className="quick-action-btn"
                      onClick={() => handleQuickAction(action.action)}
                    >
                      <span className="action-icon">{action.icon}</span>
                      <span className="action-title">{action.title}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {messages.map(msg => (
            <div key={msg.id} className={`chat-message-enhanced ${msg.sender} ${msg.type || 'text'}`}>
              {msg.sender === 'support' && (
                <div className="message-avatar">
                  <img src="/api/placeholder/32/32" alt="Support" />
                </div>
              )}
              <div className="message-content-enhanced">
                <div className="message-bubble">
                  {msg.message}
                </div>
                <div className="message-time-enhanced">
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  {msg.sender === 'user' && (
                    <span className="message-status">
                      {msg.isRead ? '✓✓' : '✓'}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="chat-message-enhanced support">
              <div className="message-avatar">
                <img src="/api/placeholder/32/32" alt="Support" />
              </div>
              <div className="typing-indicator">
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="typing-text">{supportAgent.name} is typing...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="chat-input-enhanced">
          <div className="input-container">
            <textarea
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message... (Enter to send, Shift+Enter for new line)"
              className="message-input"
              rows={1}
              disabled={chatStatus !== 'connected'}
            />
            <div className="input-actions">
              <button className="attachment-btn" title="Attach file">
                📎
              </button>
              <button 
                className="send-btn"
                onClick={() => sendMessage()}
                disabled={!newMessage.trim() || chatStatus !== 'connected'}
              >
                <span className="send-icon">📤</span>
              </button>
            </div>
          </div>
          <div className="chat-footer">
            <span className="footer-text">
              Our team typically responds within 2-3 minutes • Available 24/7
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveChat;
