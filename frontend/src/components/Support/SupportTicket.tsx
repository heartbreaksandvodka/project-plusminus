import React from 'react';
import './SupportTicket.css';

interface SupportTicketData {
  subject: string;
  description: string;
  category: 'technical' | 'trading' | 'account' | 'billing';
  priority: 'low' | 'medium' | 'high' | 'urgent';
}

interface SupportTicketProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (ticket: SupportTicketData) => void;
}

const SupportTicket: React.FC<SupportTicketProps> = ({ isOpen, onClose, onSubmit }) => {
  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    
    const ticketData: SupportTicketData = {
      subject: formData.get('subject') as string,
      description: formData.get('description') as string,
      category: formData.get('category') as any,
      priority: formData.get('priority') as any
    };
    
    onSubmit(ticketData);
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="ticket-modal" onClick={(e) => e.stopPropagation()}>
        <div className="ticket-header">
          <h3>🎫 Create Support Ticket</h3>
          <button onClick={onClose} className="close-btn">✕</button>
        </div>
        
        <form className="ticket-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="subject">Subject</label>
            <input 
              type="text" 
              id="subject"
              name="subject" 
              required 
              placeholder="Briefly describe your issue"
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="category">Category</label>
              <select id="category" name="category" required>
                <option value="">Select Category</option>
                <option value="technical">Technical Issue</option>
                <option value="trading">Trading Support</option>
                <option value="account">Account Management</option>
                <option value="billing">Billing</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="priority">Priority</label>
              <select id="priority" name="priority" required>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="urgent">Urgent</option>
              </select>
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="description">Description</label>
            <textarea 
              id="description"
              name="description" 
              rows={5} 
              required
              placeholder="Please provide detailed information about your issue, including steps to reproduce if applicable..."
            />
          </div>
          
          <div className="form-actions">
            <button type="button" onClick={onClose} className="cancel-btn">
              Cancel
            </button>
            <button type="submit" className="submit-btn">
              Create Ticket
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SupportTicket;
