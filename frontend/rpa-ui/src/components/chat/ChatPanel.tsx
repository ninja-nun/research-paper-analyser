import React, { useEffect, useState, useRef } from 'react';
import { Send, Bot, User, FileText, Loader2 } from 'lucide-react';
import { usePaperStore } from '../../store/paperStore';
import { api } from '../../lib/api';
import { generateId, cn } from '../../lib/utils';
import { Button } from '../ui/Button';
interface ChatPanelProps {
  paperId: string;
}

const EMPTY_CHAT_HISTORY: never[] = [];

export function ChatPanel({ paperId }: ChatPanelProps) {
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatHistory = usePaperStore((state) => state.chatHistory[paperId] ?? EMPTY_CHAT_HISTORY);
  const addMessage = usePaperStore((state) => state.addChatMessage);
  // Initial greeting if empty
  useEffect(() => {
    if (chatHistory.length === 0) {
      addMessage(paperId, {
        id: generateId(),
        role: 'assistant',
        content:
        "Hello! I've read this paper. What would you like to know about it?",
        timestamp: Date.now()
      });
    }
  }, [paperId, chatHistory.length, addMessage]);
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({
      behavior: 'smooth'
    });
  };
  useEffect(() => {
    scrollToBottom();
  }, [chatHistory, isTyping]);
  const handleSend = async (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!input.trim() || isTyping) return;
    const userMsg = input.trim();
    setInput('');
    addMessage(paperId, {
      id: generateId(),
      role: 'user',
      content: userMsg,
      timestamp: Date.now()
    });
    setIsTyping(true);
    try {
      const response = await api.chat(paperId, userMsg);
      addMessage(paperId, {
        id: generateId(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        timestamp: Date.now()
      });
    } catch (error) {
      addMessage(paperId, {
        id: generateId(),
        role: 'assistant',
        content:
        "I'm sorry, I encountered an error while trying to answer that. Please try again.",
        timestamp: Date.now()
      });
    } finally {
      setIsTyping(false);
    }
  };
  return (
    <div className="flex flex-col h-[600px] bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Chat Header */}
      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50/50 flex items-center gap-3">
        <div className="p-2 bg-blue-100 text-blue-600 rounded-lg">
          <Bot className="w-5 h-5" />
        </div>
        <div>
          <h3 className="font-semibold text-slate-900">Paper Assistant</h3>
          <p className="text-xs text-slate-500">
            Ask questions about the methodology, results, or concepts
          </p>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {chatHistory.map((msg) =>
        <div
          key={msg.id}
          className={cn(
            'flex gap-4 max-w-[85%]',
            msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''
          )}>
          
            <div
            className={cn(
              'w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1',
              msg.role === 'user' ?
              'bg-slate-100 text-slate-600' :
              'bg-blue-600 text-white'
            )}>
            
              {msg.role === 'user' ?
            <User className="w-5 h-5" /> :

            <Bot className="w-5 h-5" />
            }
            </div>

            <div
            className={cn(
              'space-y-2',
              msg.role === 'user' ? 'items-end' : 'items-start'
            )}>
            
              <div
              className={cn(
                'px-4 py-3 rounded-2xl text-sm leading-relaxed',
                msg.role === 'user' ?
                'bg-blue-600 text-white rounded-tr-sm' :
                'bg-gray-100 text-slate-800 rounded-tl-sm'
              )}>
              
                {msg.content}
              </div>

              {/* Sources */}
              {msg.sources && msg.sources.length > 0 &&
            <div className="mt-2 space-y-2">
                  <p className="text-xs font-semibold text-slate-500 flex items-center gap-1">
                    <FileText className="w-3 h-3" /> Sources
                  </p>
                  {msg.sources.map((source, idx) =>
              <div
                key={idx}
                className="text-xs text-slate-600 bg-blue-50/50 border border-blue-100 p-2.5 rounded-lg leading-relaxed">
                
                      "{source}"
                    </div>
              )}
                </div>
            }
            </div>
          </div>
        )}

        {isTyping &&
        <div className="flex gap-4 max-w-[85%]">
            <div className="w-8 h-8 rounded-full bg-blue-600 text-white flex items-center justify-center shrink-0 mt-1">
              <Bot className="w-5 h-5" />
            </div>
            <div className="px-4 py-3 rounded-2xl bg-gray-100 rounded-tl-sm flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-slate-400 animate-spin" />
              <span className="text-sm text-slate-500">Analyzing paper...</span>
            </div>
          </div>
        }
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 bg-white border-t border-gray-100">
        <form
          onSubmit={handleSend}
          className="flex items-end gap-2 bg-gray-50 border border-gray-200 rounded-2xl p-2 focus-within:ring-2 focus-within:ring-blue-500/20 focus-within:border-blue-500 transition-all">
          
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Ask a question..."
            className="flex-1 max-h-32 min-h-[44px] bg-transparent border-none resize-none px-3 py-2.5 text-sm focus:outline-none text-slate-900 placeholder:text-slate-400"
            rows={1} />
          
          <Button
            type="submit"
            size="sm"
            disabled={!input.trim() || isTyping}
            className="rounded-xl h-10 w-10 p-0 shrink-0 mb-0.5">
            
            <Send className="w-4 h-4 ml-0.5" />
          </Button>
        </form>
        <div className="text-center mt-2">
          <span className="text-[10px] text-slate-400">
            AI can make mistakes. Verify important information with the original
            PDF.
          </span>
        </div>
      </div>
    </div>);

}
