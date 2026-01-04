import React, { useState, useRef, useEffect } from 'react';

const ChatInterface = () => {
    const [messages, setMessages] = useState([
        { role: 'system', content: 'Hello! I am your Data Analyst AI. Ask me anything about your sales data.' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const sendMessage = async () => {
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        // TODO: Connect to backend WebSocket
        setTimeout(() => {
            setMessages(prev => [...prev, { role: 'system', content: 'I am processing your request... (WebSocket not connected)' }]);
            setIsLoading(false);
        }, 1000);
    };

    return (
        <div className="flex flex-col h-full">
            <div className="flex-1 overflow-y-auto space-y-4 p-2">
                {messages.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${msg.role === 'user'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-secondary text-secondary-foreground'
                            }`}>
                            {msg.content}
                        </div>
                    </div>
                ))}
                {isLoading && <div className="text-xs text-muted-foreground animate-pulse">AI is thinking...</div>}
            </div>

            <div className="mt-4 flex gap-2">
                <input
                    className="flex-1 bg-background border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    placeholder="Ask a question..."
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
                />
                <button
                    onClick={sendMessage}
                    className="bg-primary text-primary-foreground hover:bg-primary/90 px-4 py-2 rounded-md text-sm font-medium"
                >
                    Send
                </button>
            </div>
        </div>
    );
};

export default ChatInterface;
