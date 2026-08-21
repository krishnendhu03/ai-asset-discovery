import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8001";

function App() {
  const [question, setQuestion] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const searchKnowledge = async () => {
    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/knowledge/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question,
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to retrieve enterprise knowledge.");
      }

      const data = await response.json();

      setResult(data);
    } catch (err) {
      setError(
        "Unable to connect to Enterprise Knowledge. Please make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  const suggestedQuestions = [
    "How quickly should a P2 incident be acknowledged?",
    "Who approves a production access request?",
    "What is the incident escalation process?",
    "Which tools do support employees use?",
  ];

  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">⌘</div>

          <div>
            <h1>Enterprise Knowledge</h1>
            <span>Support Operations</span>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Knowledge Service Online
        </div>
      </header>

      <main className="container">
        <section className="hero">
          <div className="eyebrow">
            SUPPORT KNOWLEDGE
          </div>

          <h2>
            Find the right
            <span> support guidance.</span>
          </h2>

          <p>
            Ask questions about incident procedures, response
            expectations, approval hierarchies, escalation
            processes, and support tools.
          </p>
        </section>

        <section className="knowledge-card">
          <div className="card-header">
            <div>
              <h3>Ask Enterprise Knowledge</h3>

              <p>
                Search the organization's support knowledge.
              </p>
            </div>

            <div className="knowledge-badge">
              KNOWLEDGE BASE
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="question">
              Question
            </label>

            <textarea
              id="question"
              value={question}
              onChange={(event) =>
                setQuestion(event.target.value)
              }
              placeholder="Example: How quickly should a P2 incident be acknowledged?"
              rows={5}
            />
          </div>

          <div className="suggestions">
            <span>Try asking:</span>

            <div className="suggestion-list">
              {suggestedQuestions.map((item) => (
                <button
                  type="button"
                  key={item}
                  onClick={() => setQuestion(item)}
                >
                  {item}
                </button>
              ))}
            </div>
          </div>

          {error && (
            <div className="error">
              {error}
            </div>
          )}

          <button
            type="button"
            className="search-button"
            onClick={searchKnowledge}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Searching...
              </>
            ) : (
              <>
                Search Knowledge
                <span>→</span>
              </>
            )}
          </button>
        </section>

        {result && (
          <section className="results">
            <div className="results-header">
              <div>
                <div className="eyebrow">
                  KNOWLEDGE RESPONSE
                </div>

                <h3>
                  Support guidance
                </h3>
              </div>

              <div className="confidence">
                <span>Confidence</span>

                <strong>
                  {result.confidence}
                </strong>
              </div>
            </div>

            <div className="answer-card">
              <div className="result-icon">
                ✓
              </div>

              <div>
                <h4>Answer</h4>

                <p>
                  {result.answer}
                </p>
              </div>
            </div>

            <div className="source-card">
              <div>
                <h4>Source</h4>

                {result.sources?.length ? (
                  <div className="sources">
                    {result.sources.map((source) => (
                      <span key={source}>
                        {source}
                      </span>
                    ))}
                  </div>
                ) : (
                  <p>
                    No specific knowledge article matched
                    this question.
                  </p>
                )}
              </div>
            </div>
          </section>
        )}
      </main>

      <footer>
        <span>Enterprise Knowledge</span>
        <span>Enterprise Support Platform</span>
      </footer>
    </div>
  );
}

export default App;