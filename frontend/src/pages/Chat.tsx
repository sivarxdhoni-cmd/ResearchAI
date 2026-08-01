import React, { useState, useEffect, useRef } from "react";
import { api } from "../services/api";
import { MessageSquare, Send, Sparkles, AlertCircle, FileText, User } from "lucide-react";

interface Source {
  paper_id: number;
  title: string;
  section: string;
  text: string;
  relevance_score: number;
}

interface Message {
  id?: number;
  isBot: boolean;
  text: string;
  sources?: Source[];
  timestamp: string;
}

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeSource, setActiveSource] = useState<Source | null>(null);
  
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const loadHistory = async () => {
    try {
      const history = await api.getChatHistory();
      const formatted: Message[] = [];
      
      history.forEach((h: any) => {
        formatted.push({
          isBot: false,
          text: h.message,
          timestamp: h.timestamp
        });
        formatted.push({
          isBot: true,
          text: h.response,
          sources: h.sources || [],
          timestamp: h.timestamp
        });
      });
      
      setMessages(formatted);
    } catch (err) {
      console.error("Failed to load chat history:", err);
    }
  };

  useEffect(() => {
    loadHistory();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (textToSend?: string) => {
    const text = textToSend || input;
    if (!text.trim()) return;
    
    setInput("");
    setError("");
    setLoading(true);

    // Append user message
    const userMsg: Message = {
      isBot: false,
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    
    setMessages(prev => [...prev, userMsg]);

    try {
      const data = await api.askAssistant(text);
      
      const botMsg: Message = {
        isBot: true,
        text: data.response,
        sources: data.sources || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      setMessages(prev => [...prev, botMsg]);
    } catch (err: any) {
      setError(err.message || "Failed to generate AI response.");
    } finally {
      setLoading(false);
    }
  };

  const recommendedPrompts = [
    "Explain Retrieval-Augmented Generation limitations",
    "Compare Gemma and RAG methodologies",
    "What are some future scope ideas for local LLMs?",
    "Suggest SIH hackathon ideas based on local papers"
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-140px)]">
      {/* Chat Area */}
      <div className="lg:col-span-3 glass-panel rounded-2xl flex flex-col h-full overflow-hidden">
        {/* Header */}
        <div className="p-4 border-b border-slate-200/50 dark:border-slate-800/50 flex items-center justify-between bg-white/40 dark:bg-panel-dark/40 backdrop-blur">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-indigo-500 rounded-lg flex items-center justify-center shadow animate-pulse-slow">
              <MessageSquare className="w-4 h-4 text-white" />
            </div>
            <div>
              <h3 className="text-xs font-bold leading-tight">RAG AI Research Assistant</h3>
              <p className="text-[9px] text-slate-400 font-medium">Answering questions with exact PDF citations</p>
            </div>
          </div>
          <button
            onClick={() => setMessages([])}
            className="text-[10px] text-slate-400 hover:text-slate-200 border border-slate-200/50 dark:border-slate-800/80 px-2.5 py-1 rounded-lg"
          >
            Clear Thread
          </button>
        </div>

        {/* Message Log */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 glow-bg scrollbar">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col justify-center items-center max-w-lg mx-auto space-y-6 pt-10">
              <div className="text-center space-y-2">
                <Sparkles className="w-10 h-10 mx-auto text-indigo-500 animate-float" />
                <h4 className="text-sm font-bold">Ask ResearchMind AI</h4>
                <p className="text-xs text-slate-400">Ask about methodologies, missing datasets, or suggest novel publications based on your local vector indexes.</p>
              </div>

              <div className="grid grid-cols-2 gap-3 w-full">
                {recommendedPrompts.map((prompt, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(prompt)}
                    className="p-3 text-left text-xs bg-white/50 dark:bg-[#151d30]/50 border border-slate-200/40 dark:border-slate-800/40 hover:border-indigo-500 rounded-xl transition-all shadow-sm"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((msg, i) => (
              <div key={i} className={`flex gap-3 max-w-[85%] ${msg.isBot ? "mr-auto" : "ml-auto flex-row-reverse"}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center shadow text-xs shrink-0 ${
                  msg.isBot ? "bg-indigo-500 text-white" : "bg-slate-200 dark:bg-slate-800 text-slate-500"
                }`}>
                  {msg.isBot ? <Sparkles className="w-4.5 h-4.5" /> : <User className="w-4.5 h-4.5" />}
                </div>

                <div className="space-y-2">
                  <div className={`p-4 rounded-2xl text-xs leading-relaxed shadow-sm border ${
                    msg.isBot
                      ? "bg-white dark:bg-panel-dark text-slate-700 dark:text-slate-200 border-slate-200/20 dark:border-slate-800/40"
                      : "bg-indigo-500 text-white border-indigo-600"
                  }`}>
                    <p className="whitespace-pre-line">{msg.text}</p>
                  </div>

                  {/* Sources display */}
                  {msg.isBot && msg.sources && msg.sources.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-1">
                      <span className="text-[8px] uppercase tracking-wider text-slate-400 font-bold block self-center mr-1">
                        Sources:
                      </span>
                      {msg.sources.map((src, idx) => (
                        <button
                          key={idx}
                          onClick={() => setActiveSource(src)}
                          className="px-2 py-1 bg-slate-100/80 dark:bg-slate-800/80 hover:bg-indigo-500/10 border border-slate-200/50 dark:border-slate-800/80 rounded-lg text-[9px] font-semibold flex items-center gap-1 cursor-pointer transition-colors max-w-[150px] truncate"
                        >
                          <FileText className="w-3 h-3 text-indigo-400" />
                          <span className="truncate">{src.title}</span>
                          <span className="text-[8px] opacity-50">({src.section})</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-500 text-xs px-4 py-2.5 rounded-xl flex items-center gap-2 w-fit mx-auto">
              <AlertCircle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          )}

          {loading && (
            <div className="flex gap-3 mr-auto">
              <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center shadow text-white shrink-0 animate-spin">
                <LoaderCircle />
              </div>
              <div className="bg-white dark:bg-panel-dark text-slate-400 text-xs px-4 py-3 rounded-2xl border border-slate-200/20 dark:border-slate-800/40">
                Searching vector spaces and compiling literature references...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input Form */}
        <div className="p-4 border-t border-slate-200/50 dark:border-slate-800/50 bg-white/40 dark:bg-panel-dark/40 backdrop-blur">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="Ask a question about the uploaded papers (e.g. 'What datasets did Pat Lewis use?')"
              className="flex-1 px-4 py-3 text-xs bg-slate-100/50 dark:bg-[#0b101c]/50 border border-slate-200/50 dark:border-slate-800/80 rounded-xl outline-none focus:border-indigo-500 transition-all font-medium"
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="px-4 py-3 bg-indigo-500 hover:bg-indigo-600 disabled:bg-slate-200 dark:disabled:bg-slate-800 disabled:text-slate-400 text-white rounded-xl shadow cursor-pointer transition-all duration-300"
            >
              <Send className="w-4.5 h-4.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Citation Inspector Side panel */}
      <div className="glass-panel rounded-2xl p-5 flex flex-col justify-between h-full">
        <div>
          <h3 className="text-md font-bold border-b border-slate-200/50 dark:border-slate-800/50 pb-3 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-500" />
            Citation Inspector
          </h3>

          {activeSource ? (
            <div className="mt-5 space-y-4 overflow-y-auto max-h-[380px] pr-1">
              <div>
                <span className="text-[9px] tracking-wider uppercase font-bold text-slate-400">Article Title</span>
                <h4 className="text-xs font-bold text-slate-700 dark:text-slate-100 mt-1 leading-snug">
                  {activeSource.title}
                </h4>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div>
                  <span className="text-[9px] tracking-wider uppercase font-bold text-slate-400">PDF Section</span>
                  <span className="block text-[10px] font-semibold text-indigo-400 mt-0.5">{activeSource.section}</span>
                </div>
                <div>
                  <span className="text-[9px] tracking-wider uppercase font-bold text-slate-400">Relevance Score</span>
                  <span className="block text-[10px] font-semibold text-emerald-400 mt-0.5">{activeSource.relevance_score}</span>
                </div>
              </div>

              <div className="pt-3 border-t border-slate-200/50 dark:border-slate-800/50">
                <span className="text-[9px] tracking-wider uppercase font-bold text-slate-400 block mb-1.5">Context Passage</span>
                <div className="bg-slate-100/50 dark:bg-black/20 p-3 rounded-xl border border-slate-200/20 dark:border-slate-800/40 text-[11px] leading-relaxed italic text-slate-600 dark:text-slate-300">
                  "... {activeSource.text} ..."
                </div>
              </div>
            </div>
          ) : (
            <div className="mt-24 text-center space-y-3 opacity-60">
              <AlertCircle className="w-9 h-9 mx-auto text-slate-400" />
              <p className="text-[11px]">Click a citation source pill in the chat to inspect context quotes.</p>
            </div>
          )}
        </div>

        <div className="text-[10px] text-center opacity-40 pt-4 border-t border-slate-200/50 dark:border-slate-800/50">
          Clicking sources reveals exact layout snippets matching high-dimensional vector similarities.
        </div>
      </div>
    </div>
  );
};

const LoaderCircle = () => (
  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
  </svg>
);
