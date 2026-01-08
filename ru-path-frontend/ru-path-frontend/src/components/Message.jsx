import React from 'react';

// Function to safely render text including **bold** and newlines \n
const renderText = (text) => {
    if (!text) return null;
    
    // 1. Convert **bold** to <strong>bold</strong> 
    let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // 2. Convert newlines \n to HTML <br/> tags 
    html = html.replace(/\n/g, '<br/>'); 
    
    // Using dangerouslySetInnerHTML to render the formatted HTML text from a trusted source (our backend)
    return <div dangerouslySetInnerHTML={{ __html: html }} />;
};

const Message = ({ sender, text, isLoading }) => {
  return (
    <div className={`message ${sender}`}>
      {/* Show loading dots if the message is in the processing state */}
      {isLoading ? (
        <div className="loading-dots">
            <span className="dot"></span>
            <span className="dot"></span>
            <span className="dot"></span>
        </div>
      ) : (
        // Render the formatted text
        renderText(text)
      )}
    </div>
  );
};

export default Message;