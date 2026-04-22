import React, { useState, useRef, useEffect } from "react";
import { Send, Loader2, FileText, Bot, User, Sparkles, ChevronDown, ChevronUp } from "lucide-react";
import { askQuestion } from "../api";
import "./ChatPanel.css";

function ChatPanel({ documents }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput("");

    setMessages((prev) => [...prev, { type: "user", content: question }]);
    setLoading(true);

    try {
      const result = await askQuestion(question);
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          content: result.answer,
          sources: result.sources,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          type: "error",
          content: err.message || "Something went wrong. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  const hasDocuments = documents.length > 0;

  return (
    <div className="chat">
      <div className="chat__header">
        <div className="chat__header-info">
          <Sparkles size={18} className="chat__header-icon" />
          <span>ThinkDocs AI</span>
        </div>
        <span className="chat__header-status">
          {hasDocuments
            ? `${documents.length} document${documents.length !== 1 ? "s" : ""} loaded`
            : "No documents loaded"}
        </span>
      </div>

      <div className="chat__messages">
        {messages.length === 0 ? (
          <div className="chat__welcome">
            <div className="chat__welcome-icon">
              <Sparkles size={40} strokeWidth={1.5} />
            </div>
            <h2>Ask your documents anything</h2>
            <p>
              Upload PDFs in the sidebar, then ask questions here.
              ThinkDocs will find answers from your documents and cite the sources.
            </p>
            {hasDocuments && (
              <div className="chat__suggestions">
                <p className="chat__suggestions-label">Try asking:</p>
                <button onClick={() => setInput("What are the main topics covered in the documents?")} className="chat__suggestion-btn">
                  What are the main topics covered?
                </button>
                <button onClick={() => setInput("Summarize the key points from the documents")} className="chat__suggestion-btn">
                  Summarize the key points
                </button>
              </div>
            )}
          </div>
        ) : (
          messages.map((msg, i) => (
            <MessageBubble key={i} message={msg} />
          ))
        )}

        {loading && (
          <div className="chat__loading">
            <div className="chat__loading-avatar">
              <Bot size={18} />
            </div>
            <div className="chat__loading-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat__input-area">
        <form onSubmit={handleSubmit} className="chat__form">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={hasDocuments ? "Ask a question about your documents..." : "Upload a document first to start asking questions"}
            disabled={loading || !hasDocuments}
            className="chat__input"
          />
          <button
            type="submit"
            disabled={loading || !input.trim() || !hasDocuments}
            className="chat__send-btn"
          >
            {loading ? <Loader2 size={18} className="spin" /> : <Send size={18} />}
          </button>
        </form>
        <p className="chat__disclaimer">
          ThinkDocs answers are based only on your uploaded documents. Always verify important information.
        </p>
      </div>
    </div>
  );
}

function MessageBubble({ message }) {
  const [sourcesOpen, setSourcesOpen] = useState(false);

  if (message.type === "user") {
    return (
      <div className="message message--user">
        <div className="message__avatar message__avatar--user">
          <User size={16} />
        </div>
        <div className="message__content message__content--user">
          {message.content}
        </div>
      </div>
    );
  }

  if (message.type === "error") {
    return (
      <div className="message message--error">
        <div className="message__avatar message__avatar--bot">
          <Bot size={16} />
        </div>
        <div className="message__content message__content--error">
          {message.content}
        </div>
      </div>
    );
  }

  return (
    <div className="message message--assistant">
      <div className="message__avatar message__avatar--bot">
        <Bot size={16} />
      </div>
      <div className="message__body">
        <div className="message__content message__content--assistant">
          {message.content}
        </div>

        {message.sources && message.sources.length > 0 && (
          <div className="message__sources">
            <button
              className="message__sources-toggle"
              onClick={() => setSourcesOpen(!sourcesOpen)}
            >
              <FileText size={14} />
              <span>{message.sources.length} source{message.sources.length !== 1 ? "s" : ""}</span>
              {sourcesOpen ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>

            {sourcesOpen && (
              <div className="message__sources-list">
                {message.sources.map((source, i) => (
                  <div key={i} className="message__source-card">
                    <div className="message__source-header">
                      <span className="message__source-name">
                        <FileText size={12} />
                        {source.document_name}
                      </span>
                      <span className="message__source-meta">
                        Page {source.page_number} · {Math.round(source.similarity * 100)}% match
                      </span>
                    </div>
                    <p className="message__source-content">
                      {source.content.length > 200
                        ? source.content.substring(0, 200) + "..."
                        : source.content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatPanel;