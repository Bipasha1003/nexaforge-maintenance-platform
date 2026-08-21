import { useState, useRef, useEffect } from "react";
import "./ChatWidget.css";
import { API_BASE } from "../config";

const API_URL = `${API_BASE}/query`;
const HISTORY_URL = `${API_BASE}/chat/history`;

const DEFAULT_GREETING = {
  role: "bot",
  text: "Ask me anything about any equipment on the floor — error codes, maintenance schedules, or troubleshooting steps.",
  sources: [],
  tool: null,
  image_url: null,
};

const TOOL_LABELS = {
  search_manual: "ASSISTANT",
  check_schedule: "CHECK_SCHEDULE",
  log_issue: "LOG_ISSUE",
  escalate: "ESCALATE",
  machine_info: "FLEET_STATUS",
};

export default function ChatWidget({ openSignal }) {
  const [open, setOpen] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);
  const sendingRef = useRef(false);

  const isAdminPage = window.location.pathname.startsWith("/admin");
  
  const displayName = isAdminPage 
    ? (localStorage.getItem("admin_name") || "Admin")
    : (localStorage.getItem("worker_username") || "worker-guest");

  useEffect(() => {
    if (openSignal) setOpen(true);
  }, [openSignal]);

  useEffect(() => {
    fetch(`${HISTORY_URL}?user_id=${displayName}`)
      .then((r) => r.json())
      .then((data) => {
        if (data && data.length > 0) {
          setMessages(data);
        } else {
          setMessages([DEFAULT_GREETING]);
        }
      })
      .catch(() => setMessages([DEFAULT_GREETING]));
  }, [displayName]);

  useEffect(() => {
    if (open) {
      scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [messages, loading, open]);

  async function sendMessage(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || sendingRef.current) return;
    sendingRef.current = true;

    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, user_id: displayName, is_admin: isAdminPage }),
      });

      if (!res.ok) throw new Error(`Server responded ${res.status}`);
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        { 
          role: "bot", 
          text: data.answer, 
          sources: data.sources || [], 
          tool: data.tool_used || null,
          image_url: data.image_url || null  
        },
      ]);
    } catch (err) {
      setError("Couldn't reach the agent backend. Make sure the FastAPI server is running.");
    } finally {
      setLoading(false);
      sendingRef.current = false;
    }
  }

  async function clearChat() {
    await fetch(`${HISTORY_URL}?user_id=${displayName}`, { method: "DELETE" });
    setMessages([DEFAULT_GREETING]);
  }

  return (
    <div className="widget-root">
      {open && (
        <div className={`widget-panel ${expanded ? "widget-panel-expanded" : ""}`}>
          <div className="widget-header">
            <div>
              {/* Updated Title */}
              <div className="widget-title">🤖 AI Assistant</div>
              <div className="widget-subtitle">
                User: {displayName} · <span className="widget-clear-link" onClick={clearChat}>Clear chat</span>
              </div>
            </div>
            <div className="widget-header-actions">
              <button className="widget-expand" onClick={() => setExpanded((v) => !v)}
                aria-label={expanded ? "Shrink chat" : "Expand chat"} title={expanded ? "Shrink" : "Expand"}>
                {expanded ? "⤡" : "⤢"}
              </button>
              <button className="widget-close" onClick={() => setOpen(false)} aria-label="Close chat">×</button>
            </div>
          </div>

          <div className="widget-scroll" ref={scrollRef}>
            {messages.map((m, i) => (
              <div key={i} className={`msg-row msg-row-${m.role}`}>
                {m.role === "bot" && m.tool && (
                  <div className="tool-badge">{TOOL_LABELS[m.tool] || m.tool}</div>
                )}
                
                <div className={`bubble bubble-${m.role} ${m.role === "bot" && m.tool === "escalate" ? "bubble-red-alert" : ""}`}>
                  {m.text}
                </div>

                {m.role === "bot" && m.image_url && (
                  <div className="attached-image-wrapper">
                    <img 
                      src={m.image_url} 
                      alt="Manual Diagram" 
                      className="attached-manual-img" 
                    />
                  </div>
                )}

                {m.role === "bot" && m.sources && m.sources.length > 0 && (
                  <div className="tabs">
                    {m.sources.map((s, j) => (
                      <span className="tab" key={j}>{s.source} <b>p.{s.page}</b></span>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {loading && (
              <div className="msg-row msg-row-bot">
                <div className="bubble bubble-bot bubble-loading">
                  <span className="pulse" /><span className="pulse" /><span className="pulse" />
                </div>
              </div>
            )}

            {error && <div className="error-banner">{error}</div>}
          </div>

          <form className="widget-composer" onSubmit={sendMessage}>
            <input className="widget-input" placeholder="Ask a question about any machine…" value={input}
              onChange={(e) => setInput(e.target.value)} disabled={loading} />
            <button className="widget-send" type="submit" disabled={loading || !input.trim()}>Send</button>
          </form>
        </div>
      )}

      {/* Replaced 'MX' text with Robot Emoji */}
      <button className="widget-fab" onClick={() => setOpen((v) => !v)} aria-label={open ? "Close chat" : "Open chat"}>
        {open ? "×" : "🤖"}
      </button>
    </div>
  );
}