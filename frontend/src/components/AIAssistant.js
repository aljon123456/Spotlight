import React, { useState, useEffect } from 'react';
import './AIAssistant.css';

const AIAssistant = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [assignment, setAssignment] = useState(null);
  const [showExplanation, setShowExplanation] = useState(false);
  const [loadingAssignment, setLoadingAssignment] = useState(false);
  const [assignmentError, setAssignmentError] = useState(null);

  // Load current assignment explanation on mount
  useEffect(() => {
    if (isOpen && !assignment && !loadingAssignment) {
      loadAssignmentExplanation();
    }
  }, [isOpen, assignment, loadingAssignment]);

  const loadAssignmentExplanation = async () => {
    setLoadingAssignment(true);
    setAssignmentError(null);
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/ai-assistant/my_assignment/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      if (!response.ok) {
        throw new Error('No active assignment found');
      }
      
      const data = await response.json();
      setAssignment(data);
      
      // Add initial message
      if (data && data.parking_slot && data.parking_slot.slot_number) {
        setMessages([{
          type: 'assistant',
          content: `You are currently assigned to parking slot ${data.parking_slot.slot_number}. ${data.summary || ''}`
        }]);
      }
    } catch (error) {
      console.error('Failed to load assignment:', error);
      setAssignmentError('No active parking assignment found.');
      setMessages([{
        type: 'assistant',
        content: 'I can help answer questions about parking! However, you don\'t currently have an active assignment.'
      }]);
    } finally {
      setLoadingAssignment(false);
    }
  };

  const sendQuery = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    const userMessage = input;
    setInput('');
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);

    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/ai-assistant/query/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ query: userMessage })
      });

      const data = await response.json();
      
      let assistantMessage = data.response;
      if (data.alternatives && data.alternatives.length > 0) {
        assistantMessage += '\n\nAlternative slots: ' + 
          data.alternatives.map(a => `${a.slot_number} (${a.slot_type}, ${a.distance}m away)`).join(', ');
      }

      setMessages(prev => [...prev, { type: 'assistant', content: assistantMessage }]);
    } catch (error) {
      console.error('Query failed:', error);
      setMessages(prev => [...prev, { type: 'error', content: 'Failed to process query. Please try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="ai-assistant">
      {/* Chat Bubble Button */}
      <button 
        className="ai-assistant-toggle"
        onClick={() => setIsOpen(!isOpen)}
        title="Ask Parking Assistant"
      >
        🤖 Parking AI
      </button>

      {/* Chat Window */}
      {isOpen && (
        <div className="ai-assistant-window">
          <div className="ai-assistant-header">
            <h3>Parking Assistant</h3>
            <button className="close-btn" onClick={() => setIsOpen(false)}>✕</button>
          </div>

          {/* Loading State */}
          {loadingAssignment && (
            <div className="loading-state">
              <p>Loading your assignment...</p>
            </div>
          )}

          {/* Assignment Info */}
          {!loadingAssignment && assignment && !showExplanation && (
            <div className="assignment-summary">
              <h4>Current Assignment</h4>
              {assignment.parking_slot && (
                <>
                  <p><strong>Slot:</strong> {assignment.parking_slot.slot_number} ({assignment.parking_slot.slot_type})</p>
                  <p><strong>Distance:</strong> {assignment.assignment_factors?.distance_to_building || 'N/A'}</p>
                  <p><strong>Confidence:</strong> {assignment.assignment_factors?.confidence_score || 'N/A'}%</p>
                  <button 
                    className="expand-btn"
                    onClick={() => setShowExplanation(true)}
                  >
                    See Full Explanation
                  </button>
                </>
              )}
            </div>
          )}

          {/* Full Explanation View */}
          {assignment && showExplanation && (
            <div className="assignment-explanation">
              <button 
                className="back-btn"
                onClick={() => setShowExplanation(false)}
              >
                ← Back to Chat
              </button>
              
              {assignment.summary && <h4>{assignment.summary}</h4>}
              
              <div className="explanation-details">
                {assignment.parking_slot && (
                  <div className="detail-section">
                    <h5>Parking Slot Details</h5>
                    <ul>
                      <li>Slot Number: {assignment.parking_slot.slot_number}</li>
                      <li>Type: {assignment.parking_slot.slot_type}</li>
                      <li>Building: {assignment.parking_slot.building}</li>
                      <li>Status: {assignment.parking_slot.status}</li>
                    </ul>
                  </div>
                )}

                {assignment.assignment_factors && (
                  <div className="detail-section">
                    <h5>Why This Slot</h5>
                    <ul>
                      <li>{assignment.assignment_factors.slot_type_priority}</li>
                      <li>Distance: {assignment.assignment_factors.distance_to_building}</li>
                      <li>Availability: {assignment.assignment_factors.availability_status}</li>
                      <li>Confidence Score: {assignment.assignment_factors.confidence_score}%</li>
                    </ul>
                  </div>
                )}

                {assignment.alternatives && assignment.alternatives.length > 0 && (
                  <div className="detail-section">
                    <h5>Alternative Options</h5>
                    <ul>
                      {assignment.alternatives.map((alt, idx) => (
                        <li key={idx}>
                          {alt.slot_number} ({alt.slot_type}) - {alt.distance}m away
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Chat Messages */}
          <div className="ai-assistant-messages">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message ${msg.type}`}>
                <div className="message-content">
                  {msg.type === 'assistant' && '🤖 '}
                  {msg.type === 'user' && '👤 '}
                  {msg.type === 'error' && '⚠️ '}
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && <div className="message assistant"><div className="message-content">Thinking...</div></div>}
          </div>

          {/* Suggested Questions */}
          {messages.length === 1 && (
            <div className="suggested-questions">
              <p>Suggested questions:</p>
              <button onClick={() => setInput('Why was I assigned this slot?')} className="suggestion">
                Why was I assigned this slot?
              </button>
              <button onClick={() => setInput('Can I get a closer slot?')} className="suggestion">
                Can I get a closer slot?
              </button>
              <button onClick={() => setInput('What are the subscription benefits?')} className="suggestion">
                What are the subscription benefits?
              </button>
            </div>
          )}

          {/* Input Form */}
          <form onSubmit={sendQuery} className="ai-assistant-input">
            <input
              type="text"
              placeholder="Ask about your parking assignment..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <button type="submit" disabled={loading}>Send</button>
          </form>
        </div>
      )}
    </div>
  );
};

export default AIAssistant;
