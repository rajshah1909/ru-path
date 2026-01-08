import React, { useState } from "react";

const MAP_URL = process.env.PUBLIC_URL + "/background.png";
const API_URL = "http://localhost:5000/api/chat"; // Flask backend

function App() {
  const [showChat, setShowChat] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hi! Welcome to RU-PATH. Do you have a parking question, a bus question, or both?",
    },
  ]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);

  // send message to backend
  async function sendMessage() {
    const trimmed = input.trim();
    if (!trimmed) return;

    // show user message immediately
    setMessages((prev) => [...prev, { sender: "user", text: trimmed }]);
    setInput("");

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: trimmed,
          session_id: sessionId || undefined,
        }),
      });

      if (!res.ok) {
        throw new Error("Server error " + res.status);
      }

      const data = await res.json();
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      const botText =
        data.response || data.reply || "Sorry, I could not understand that.";

      setMessages((prev) => [...prev, { sender: "bot", text: botText }]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Oops, I couldn't reach the RU-PATH server. Make sure the backend is running on port 5000.",
        },
      ]);
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  // ---------- LANDING SCREEN (before chat) ----------
  if (!showChat) {
    return (
      <div
        style={{
          width: "100vw",
          height: "100vh",
          minHeight: "100vh",
          backgroundImage: `url('${MAP_URL}')`,
          backgroundSize: "cover",
          backgroundPosition: "center",
          position: "relative",
          fontFamily: "Inter, sans-serif",
          overflow: "auto",
        }}
      >
        <style>{`
          * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
          }

          .header-box {
            position: absolute;
            top: clamp(1rem, 3vh, 3rem);
            left: 50%;
            transform: translateX(-50%);
            background: #cc0033;
            color: white;
            border-radius: clamp(1.5rem, 2.1vw, 2.1rem);
            width: clamp(280px, 90vw, 780px);
            padding: clamp(0.8rem, 1.2rem, 1.2rem);
            font-size: clamp(1rem, 1.7vw, 1.7rem);
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 30;
          }

          .header-logo {
            background: white;
            color: #cc0033;
            border-radius: 0.7rem;
            padding: 0.37rem 1.18rem;
            margin-right: 1.5rem;
            font-size: clamp(1rem, 1.7vw, 1.7rem);
            font-family: serif;
          }

          .welcome-bubble {
            position: absolute;
            left: 50%;
            top: clamp(7rem, 15vh, 15vh);
            transform: translateX(-50%);
            font-size: clamp(0.9rem, 1.18vw, 1.18rem);
            background: white;
            color: #22304a;
            border-radius: 1.2rem;
            padding: clamp(0.9rem, 1.14rem, 1.14rem);
            width: clamp(280px, 90vw, 600px);
            text-align: center;
          }

          .chip-bar {
            position: absolute;
            left: 50%;
            top: clamp(14rem, 29vh, 29vh);
            transform: translateX(-50%);
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1rem;
            width: clamp(280px, 95vw, 800px);
          }

          .campus-chip {
            border-radius: 999px;
            padding: 0.6rem 1.2rem;
            font-weight: 600;
            font-size: clamp(0.85rem, 1.07vw, 1.07rem);
            box-shadow: 0 2px 8px rgba(80,60,80,0.12);
            cursor: pointer;
            opacity: 0.92;
          }

          .campus-chip.livingston { background:#ffd8b1; color:#9c5200; }
          .campus-chip.busch { background:#b1e2ff; color:#0073a7; }
          .campus-chip.college { background:#fff9b1; color:#b19e00; }
          .campus-chip.cook { background:#b1ffc6; color:#257a46; }

          .lots-relaxed-grid {
            position: absolute;
            left: 50%;
            top: clamp(22rem, 44vh, 44vh);
            transform: translateX(-50%);
            width: clamp(280px, 95vw, 655px);
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
          }

          .lot-card {
            background: rgba(255,255,255,0.97);
            border-radius: 1.12rem;
            padding: 1.2rem;
            box-shadow: 0 4px 18px rgba(150,70,40,0.09);
            border-left: 9px solid #ffd8b1;
          }

          .lot-card.lot53 { border-left-color:#b1e2ff; }
          .lot-card.college-ave { border-left-color:#fff9b1; }
          .lot-card.cook { border-left-color:#b1ffc6; }

          .lot-title {
            font-size: clamp(1rem, 1.17vw, 1.17rem);
            font-weight: 700;
          }

          .permit-line {
            font-size: clamp(0.85rem, 0.97vw, 0.97rem);
            color: #656e84;
            margin-bottom: 0.7rem;
          }

          .walk-row {
            display: flex;
            align-items: center;
            font-size: clamp(0.9rem, 1.05vw, 1.05rem);
            color: #209846;
            font-weight: 600;
          }

          .walk-icon {
            width: 28px;
            height: 28px;
            margin-right: 0.6rem;
            stroke: currentColor;
          }

          .suggest-bar {
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%);
            background: white;
            padding: 1rem 1.4rem;
            border-radius: 1rem;
            width: clamp(280px, 90vw, 600px);
            box-shadow: 0 2px 12px rgba(20,18,33,0.06);
            display: flex;
            gap: 1rem;
            align-items: center;
          }

          .next-btn {
            background: #cc0033;
            color: white;
            border: none;
            border-radius: 0.8rem;
            font-size: 1rem;
            padding: 0.6rem 1.4rem;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(204,0,51,0.20);
            transition: 0.2s;
          }

          .next-btn:hover {
            background: #a3002a;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(204,0,51,0.30);
          }
        `}</style>

        {/* HEADER */}
        <div className="header-box">
          <span className="header-logo">RU</span>
          RU-PATH: Parking Assistant
        </div>

        {/* WELCOME */}
        <div className="welcome-bubble">
          Hi! Welcome to RU Path.<br />
          Ask me anything about parking or buses!<br />
          <span className="bubble-subtext">
            E.g., "Where can I park with a student permit?"
          </span>
        </div>

        {/* CAMPUS CHIPS */}
        <div className="chip-bar">
          <button className="campus-chip livingston active">Livingston</button>
          <button className="campus-chip busch">Busch</button>
          <button className="campus-chip college">College Ave</button>
          <button className="campus-chip cook">Cook/Douglass</button>
        </div>

        {/* LOT CARDS (same as before) */}
        <div className="lots-relaxed-grid">
          <div className="lot-card lot51">
            <div className="lot-title">Lot 51 (Livingston Campus)</div>
            <div className="permit-line">
              <strong>Permits:</strong> Student B / Faculty / Staff
            </div>
            <div className="walk-row">
              <svg className="walk-icon" viewBox="0 0 24 24">
                <circle cx="12" cy="4" r="2" />
                <path d="M12 6 l0 4" />
                <path d="M12 10 l-3 4" />
                <path d="M12 10 l3 4" />
                <path d="M12 8 l-3 -2" />
                <path d="M12 8 l3 2" />
              </svg>
              Walking distance to Kilmer Library (7 min)
            </div>
          </div>

          <div className="lot-card lot53">
            <div className="lot-title">Lot 53 (Busch Campus)</div>
            <div className="permit-line">
              <strong>Permits:</strong> Student B / Faculty / Staff
            </div>
            <div className="walk-row">
              <svg className="walk-icon" viewBox="0 0 24 24">
                <circle cx="12" cy="4" r="2" />
                <path d="M12 6 l0 4" />
                <path d="M12 10 l-3 4" />
                <path d="M12 10 l3 4" />
                <path d="M12 8 l-3 -2" />
                <path d="M12 8 l3 2" />
              </svg>
              Walking distance to Center for Teaching and Learning (5 min)
            </div>
          </div>

          <div className="lot-card college-ave">
            <div className="lot-title">Lot 26 (College Ave Campus)</div>
            <div className="permit-line">
              <strong>Permits:</strong> Student A / Faculty / Staff
            </div>
            <div className="walk-row">
              <svg className="walk-icon" viewBox="0 0 24 24">
                <circle cx="12" cy="4" r="2" />
                <path d="M12 6 l0 4" />
                <path d="M12 10 l-3 4" />
                <path d="M12 10 l3 4" />
                <path d="M12 8 l-3 -2" />
                <path d="M12 8 l3 2" />
              </svg>
              Walking distance to Student Center (6 min)
            </div>
          </div>

          <div className="lot-card cook">
            <div className="lot-title">Lot 70 (Cook/Douglass Campus)</div>
            <div className="permit-line">
              <strong>Permits:</strong> Student C / Faculty / Staff
            </div>
            <div className="walk-row">
              <svg className="walk-icon" viewBox="0 0 24 24">
                <circle cx="12" cy="4" r="2" />
                <path d="M12 6 l0 4" />
                <path d="M12 10 l-3 4" />
                <path d="M12 10 l3 4" />
                <path d="M12 8 l-3 -2" />
                <path d="M12 8 l3 2" />
              </svg>
              Walking distance to Food Science Building (4 min)
            </div>
          </div>
        </div>

        {/* SUGGEST BAR */}
        <div className="suggest-bar">
          <span role="img" aria-label="bot">
            🤖
          </span>
          <span style={{ flex: 1 }}>
            Try asking me: "Where can I park with a Student B permit?" or "Which
            bus for Busch campus?"
          </span>
          <button className="next-btn" onClick={() => setShowChat(true)}>
            Next
          </button>
        </div>
      </div>
    );
  }

  // ---------- CHAT SCREEN ----------
  return (
    <div
      style={{
        height: "100vh",
        width: "100vw",
        backgroundColor: "#f5f5f7",
        display: "flex",
        flexDirection: "column",
        fontFamily: "Inter, sans-serif",
      }}
    >
      {/* Top bar */}
      <div
        style={{
          background: "#cc0033",
          color: "white",
          padding: "1rem 2rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ fontWeight: 700, fontSize: "1.1rem" }}>
          RU-PATH: Parking & Bus Assistant
        </div>
        <button
          onClick={() => setShowChat(false)}
          style={{
            background: "white",
            color: "#cc0033",
            borderRadius: "999px",
            border: "none",
            padding: "0.4rem 1rem",
            cursor: "pointer",
            fontWeight: 600,
          }}
        >
          ⬅ Back to lots
        </button>
      </div>

      {/* Chat body */}
      <div
        style={{
          flex: 1,
          padding: "1.5rem",
          display: "flex",
          justifyContent: "center",
        }}
      >
        <div
          style={{
            width: "min(900px, 100%)",
            background: "white",
            borderRadius: "1rem",
            boxShadow: "0 4px 16px rgba(0,0,0,0.08)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              padding: "1rem 1.25rem",
              borderBottom: "1px solid #eee",
              fontWeight: 600,
            }}
          >
            Chat with RU-PATH bot
          </div>

          {/* Messages */}
          <div
            style={{
              flex: 1,
              padding: "1rem 1.25rem",
              overflowY: "auto",
              background: "#fafafa",
            }}
          >
            {messages.map((m, idx) => (
              <div
                key={idx}
                style={{
                  display: "flex",
                  justifyContent:
                    m.sender === "user" ? "flex-end" : "flex-start",
                  marginBottom: "0.75rem",
                }}
              >
                <div
                  style={{
                    maxWidth: "70%",
                    padding: "0.6rem 0.9rem",
                    borderRadius: "0.9rem",
                    background:
                      m.sender === "user" ? "#cc0033" : "white",
                    color: m.sender === "user" ? "white" : "#222",
                    boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
                    whiteSpace: "pre-wrap",
                    fontSize: "0.95rem",
                  }}
                >
                  {m.text}
                </div>
              </div>
            ))}
          </div>

          {/* Input area */}
          <div
            style={{
              padding: "0.8rem 1rem",
              borderTop: "1px solid #eee",
              display: "flex",
              gap: "0.6rem",
            }}
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about parking or buses…"
              style={{
                flex: 1,
                resize: "none",
                borderRadius: "0.7rem",
                border: "1px solid #ddd",
                padding: "0.6rem 0.8rem",
                fontFamily: "inherit",
                fontSize: "0.95rem",
                minHeight: "2.4rem",
                maxHeight: "6rem",
              }}
            />
            <button
              onClick={sendMessage}
              style={{
                background: "#cc0033",
                color: "white",
                border: "none",
                borderRadius: "0.7rem",
                padding: "0 1.4rem",
                fontWeight: 600,
                cursor: "pointer",
              }}
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
