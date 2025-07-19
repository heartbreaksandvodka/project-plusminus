import React, { useState } from 'react';
import LiveChat from './LiveChat';
import KnowledgeBase from './KnowledgeBase';
import { SupportTicket } from './index';
import './FloatingSupportWidget.css';
import './LiveChat.css';
import './KnowledgeBase.css';
import './SupportTicket.css';

interface SupportTicketData {
  id: string;
  subject: string;
  description: string;
  category: 'technical' | 'trading' | 'account' | 'billing';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'open' | 'in-progress' | 'resolved' | 'closed';
  createdAt: Date;
  updatedAt: Date;
}

const FloatingSupportWidget: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [activeModal, setActiveModal] = useState<'chat' | 'knowledge' | 'ticket' | null>(null);
  const [hasUnreadMessages, setHasUnreadMessages] = useState(true);

  const createSupportTicket = (ticket: Omit<SupportTicketData, 'id' | 'createdAt' | 'updatedAt' | 'status'>) => {
    const newTicket: SupportTicketData = {
      ...ticket,
      id: Date.now().toString(),
      status: 'open',
      createdAt: new Date(),
      updatedAt: new Date()
    };
    console.log('Support ticket created:', newTicket);
    setActiveModal(null);
  };

  const handleOptionClick = (option: 'chat' | 'knowledge' | 'ticket') => {
    setActiveModal(option);
    setIsExpanded(false);
    if (option === 'chat') {
      setHasUnreadMessages(false);
    }
  };

  const closeModal = () => {
    setActiveModal(null);
  };

  return (
    <>
      <div className="floating-support-widget">
        <div className={`support-options ${isExpanded ? 'expanded' : ''}`}>
          <button
            className="support-option knowledge-option"
            onClick={() => handleOptionClick('knowledge')}
            title="Knowledge Base"
          >
            <span className="option-icon">📚</span>
            <span className="option-label">Knowledge Base</span>
          </button>
          
          <button
            className="support-option ticket-option"
            onClick={() => handleOptionClick('ticket')}
            title="Create Ticket"
          >
            <span className="option-icon">🎫</span>
            <span className="option-label">Create Ticket</span>
          </button>
          
          <button
            className="support-option chat-option"
            onClick={() => handleOptionClick('chat')}
            title="Live Chat"
          >
            <span className="option-icon">💬</span>
            <span className="option-label">Live Chat</span>
            {hasUnreadMessages && <span className="unread-indicator"></span>}
          </button>
        </div>

        <button
          className={`support-trigger ${isExpanded ? 'expanded' : ''}`}
          onClick={() => setIsExpanded(!isExpanded)}
          title="Support"
        >
          <span className={`trigger-icon ${isExpanded ? 'rotated' : ''}`}>
            {isExpanded ? '✕' : '🛟'}
          </span>
          {hasUnreadMessages && !isExpanded && <span className="notification-dot"></span>}
        </button>
      </div>

      {/* Modals */}
      <LiveChat 
        isOpen={activeModal === 'chat'} 
        onClose={closeModal} 
      />
      
      <KnowledgeBase 
        isOpen={activeModal === 'knowledge'} 
        onClose={closeModal} 
      />
      
      <SupportTicket
        isOpen={activeModal === 'ticket'}
        onClose={closeModal}
        onSubmit={createSupportTicket}
      />
    </>
  );
};

export default FloatingSupportWidget;
