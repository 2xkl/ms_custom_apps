import React, { useState, useEffect, useRef } from "react";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { materialLight } from "react-syntax-highlighter/dist/esm/styles/prism";
import mermaid from "mermaid";

function Mermaid({ chart }) {
  const ref = useRef(null);

  useEffect(() => {
    if (ref.current) {
      mermaid.initialize({ startOnLoad: false });
      try {
        mermaid.render(
          `mermaid-${Math.random()}`,
          chart,
          (svgCode) => {
            ref.current.innerHTML = svgCode;
          },
          ref.current
        );
      } catch (e) {
        ref.current.innerHTML = `<pre style="color:red;">Błąd w kodzie Mermaid:\n${e.message}</pre>`;
      }
    }
  }, [chart]);

  return <div ref={ref} />;
}

function parseCodeBlocks(text) {
  const regex = /```(\w+)?\n([\s\S]*?)```/g;
  let lastIndex = 0;
  const parts = [];
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push({ type: "text", content: text.slice(lastIndex, match.index) });
    }
    parts.push({ type: "code", lang: match[1] || "", content: match[2] });
    lastIndex = regex.lastIndex;
  }
  if (lastIndex < text.length) {
    parts.push({ type: "text", content: text.slice(lastIndex) });
  }
  return parts;
}

function ChatResponse({ response }) {
  const parts = parseCodeBlocks(response);

  return (
    <div>
      {parts.map((part, i) => {
        if (part.type === "code") {
          if (part.lang === "mermaid") {
            return <Mermaid key={i} chart={part.content} />;
          }
          return (
            <SyntaxHighlighter
              key={i}
              language={part.lang}
              style={materialLight}
              showLineNumbers
            >
              {part.content}
            </SyntaxHighlighter>
          );
        }
        return <p key={i}>{part.content}</p>;
      })}
    </div>
  );
}

export default function Chat() {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const apiUrl = process.env.REACT_APP_API_URL;
  async function handleSubmit(e) {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);

    try {
      const res = await fetch(apiUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();

      if (res.ok) {
        setHistory((prev) => [...prev, { question: input, answer: data.response }]);
        setInput("");
      } else {
        alert("Błąd serwera: " + JSON.stringify(data));
      }
    } catch (error) {
      alert("Błąd sieci: " + error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ maxWidth: 600, margin: "auto", padding: 20 }}>
      <h1>Chat AI</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Zadaj pytanie"
          disabled={loading}
          style={{ width: "80%", padding: 8 }}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          {loading ? "Ładowanie..." : "Wyślij"}
        </button>
      </form>

      <div style={{ marginTop: 20 }}>
        {history.length === 0 && <p>Brak historii rozmowy</p>}
        {[...history].reverse().map(({ question, answer }, i) => (
          <div
            key={i}
            style={{
              marginBottom: 15,
              padding: 10,
              border: "1px solid #ccc",
              borderRadius: 6,
            }}
          >
            <p>
              <strong>Ty:</strong> {question}
            </p>
            <p>
              <strong>AI:</strong>{" "}
              <ChatResponse response={answer} />
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
