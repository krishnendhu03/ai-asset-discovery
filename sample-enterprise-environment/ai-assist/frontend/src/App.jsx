import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [issue, setIssue] = useState("");
  const [service, setService] = useState("Identity Service");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const getAssistance = async () => {
    if (!issue.trim()) {
      setError("Please describe the issue first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/assist/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          issue,
          service,
        }),
      });

      if (!response.ok) {
        throw new Error("Unable to get AI assistance.");
      }

      const data = await response.json();

      setResult(data);
    } catch (err) {
      setError(
        "Unable to connect to AI Assist. Please make sure the backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">

      {/* =========================
          NAVBAR
      ========================= */}

      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">✦</div>

          <div>
            <h1>AI Assist</h1>
            <span>Employee Support</span>
          </div>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          AI Service Online
        </div>
      </header>

      {/* =========================
          MAIN CONTENT
      ========================= */}

      <main className="container">

        {/* HERO */}

        <section className="hero">
          <div className="eyebrow">
            INTELLIGENT SUPPORT
          </div>

          <h2>
            How can we
            <span> help you?</span>
          </h2>

          <p>
            Describe your issue and AI Assist will provide
            possible causes, troubleshooting steps, and
            recommended actions.
          </p>
        </section>

        {/* =========================
            ASSIST FORM
        ========================= */}

        <section className="assist-card">

          <div className="card-header">

            <div>
              <h3>Describe your issue</h3>

              <p>
                Provide as much detail as possible.
              </p>
            </div>

            <div className="ai-badge">
              AI POWERED
            </div>

          </div>

          {/* ISSUE */}

          <div className="form-group">

            <label htmlFor="issue">
              Issue
            </label>

            <textarea
              id="issue"
              value={issue}
              onChange={(event) =>
                setIssue(event.target.value)
              }
              placeholder="Example: Users are unable to log in intermittently..."
              rows={6}
            />

          </div>

          {/* SERVICE */}

          <div className="form-group">

            <label htmlFor="service">
              Service
            </label>

            <select
              id="service"
              value={service}
              onChange={(event) =>
                setService(event.target.value)
              }
            >
              <option>Identity Service</option>
              <option>Payment API</option>
              <option>Document Processing</option>
              <option>Customer Service</option>
              <option>Database Service</option>
              <option>Other</option>
            </select>

          </div>

          {/* ERROR */}

          {error && (
            <div className="error">
              {error}
            </div>
          )}

          {/* BUTTON */}

          <button
            type="button"
            className="assist-button"
            onClick={getAssistance}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyzing...
              </>
            ) : (
              <>
                Get AI Assistance
                <span>→</span>
              </>
            )}
          </button>

        </section>

        {/* =========================
            AI RESULTS
        ========================= */}

        {result && (
          <section className="results">

            <div className="results-header">

              <div>
                <div className="eyebrow">
                  AI ANALYSIS
                </div>

                <h3>
                  Recommended assistance
                </h3>
              </div>

              <div className="confidence">

                <span>
                  Confidence
                </span>

                <strong>
                  {result.confidence}
                </strong>

              </div>

            </div>

            {/* CAUSE + ACTION */}

            <div className="result-grid">

              <div className="result-card cause">

                <div className="result-icon">
                  !
                </div>

                <div>
                  <h4>
                    Possible Cause
                  </h4>

                  <p>
                    {result.possible_cause}
                  </p>
                </div>

              </div>

              <div className="result-card action">

                <div className="result-icon">
                  ✓
                </div>

                <div>
                  <h4>
                    Recommended Action
                  </h4>

                  <p>
                    {result.recommended_action}
                  </p>
                </div>

              </div>

            </div>

            {/* TROUBLESHOOTING */}

            <div className="steps-card">

              <div className="steps-heading">

                <div className="result-icon">
                  ☷
                </div>

                <div>
                  <h4>
                    Troubleshooting Steps
                  </h4>

                  <p>
                    Recommended steps to investigate
                    the issue
                  </p>
                </div>

              </div>

              <div className="steps">

                {result.troubleshooting_steps?.map(
                  (step, index) => (
                    <div
                      className="step"
                      key={index}
                    >
                      <span>
                        {index + 1}
                      </span>

                      <p>
                        {step}
                      </p>
                    </div>
                  )
                )}

              </div>

            </div>

          </section>
        )}

      </main>

      {/* =========================
          FOOTER
      ========================= */}

      <footer>
        <span>
          AI Assist
        </span>

        <span>
          Enterprise Support Platform
        </span>
      </footer>

    </div>
  );
}

export default App;