import React, { useState } from "react";
import "./WebsiteQA.css";

const WebsiteQA = () => {
  const [url, setUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAnswer("");
    setError("");

    try {
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, question }),
      });

      if (!response.ok) {
        throw new Error("Failed to get answer from backend");
      }

      const data = await response.json();
      setAnswer(data.answer);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="websiteqa-page-wrapper">
      <header className="websiteqa-header">
        <h2>GenAI Web QA</h2>
        <p>Ask questions about any website using Google Gemini AI.</p>
      </header>
      <div className="websiteqa-container">
        <h1 className="websiteqa-title">Ask a Website</h1>
        <form className="websiteqa-form" onSubmit={handleSubmit}>
          <label htmlFor="website-url">Website URL:</label>
          <input
            id="website-url"
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            required
          />
          <label htmlFor="user-question">Your Question:</label>
          <input
            id="user-question"
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? "Asking..." : "Ask"}
          </button>
        </form>
        <div className="websiteqa-chat">
          {question && (
            <div className="websiteqa-message user">
              <strong>You:</strong> {question}
            </div>
          )}
          {answer && (
            <div className="websiteqa-message bot">
              <strong>Bot:</strong> {answer}
            </div>
          )}
        </div>
        {error && (
          <div className="websiteqa-error">
            <strong>Error:</strong> {error}
          </div>
        )}
      </div>
      <footer className="websiteqa-footer">
        <p>&copy; {new Date().getFullYear()} GenAI Web QA. Powered by React, FastAPI, and Google Gemini AI. By Abhinav Pratap Singh</p>
      </footer>
    </div>
  );
};

export default WebsiteQA; 