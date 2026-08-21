import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8002";

function App() {
  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);

  const [analysis, setAnalysis] = useState(null);

  const [loadingIncidents, setLoadingIncidents] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  const [error, setError] = useState("");

  // =========================================================
  // LOAD INCIDENTS
  // =========================================================

  useEffect(() => {
    const loadIncidents = async () => {
      try {
        setLoadingIncidents(true);
        setError("");

        const response = await fetch(`${API_URL}/incidents/`);

        if (!response.ok) {
          throw new Error("Unable to load incidents.");
        }

        const data = await response.json();

        setIncidents(data);
      } catch (err) {
        console.error("Incident loading error:", err);

        setError(
          "Unable to load incidents. Please make sure the Incident Intelligence backend is running."
        );
      } finally {
        setLoadingIncidents(false);
      }
    };

    loadIncidents();
  }, []);

  // =========================================================
  // SELECT INCIDENT
  // =========================================================

  const handleSelectIncident = (incident) => {
    setSelectedIncident(incident);
    setAnalysis(null);
    setError("");
  };

  // =========================================================
  // ANALYZE INCIDENT
  // =========================================================

  const handleAnalyze = async () => {
    if (!selectedIncident) {
      return;
    }

    try {
      setAnalyzing(true);
      setError("");
      setAnalysis(null);

      const response = await fetch(
        `${API_URL}/incidents/${selectedIncident.id}/analyze`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Unable to analyze incident.");
      }

      const data = await response.json();

      setAnalysis(data.analysis);
    } catch (err) {
      console.error("Incident analysis error:", err);

      setError(
        "Unable to analyze the incident. Please make sure the backend and ML models are available."
      );
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="app">

      {/* =====================================================
          NAVBAR
      ===================================================== */}

      <header className="navbar">
        <div className="brand">

          <div className="brand-icon">
            ✦
          </div>

          <div>
            <h1>Incident Intelligence</h1>

            <span>
              Enterprise Incident Operations
            </span>
          </div>

        </div>

        <div className="status">
          <span className="status-dot"></span>
          Intelligence Service Online
        </div>
      </header>


      {/* =====================================================
          MAIN
      ===================================================== */}

      <main className="container">

        {/* ===================================================
            HERO
        =================================================== */}

        <section className="hero">

          <div className="eyebrow">
            INCIDENT INTELLIGENCE
          </div>

          <h2>
            Understand incidents.
            <span> Respond faster.</span>
          </h2>

          <p>
            Review active incidents, understand their impact,
            and use intelligence-driven analysis to identify
            possible causes, risks, and recommended actions.
          </p>

        </section>


        {/* ===================================================
            ERROR
        =================================================== */}

        {error && (
          <div className="error">
            {error}
          </div>
        )}


        {/* ===================================================
            INCIDENT LAYOUT
        =================================================== */}

        <section className="incident-layout">

          {/* =================================================
              INCIDENT LIST
          ================================================= */}

          <div className="incident-list">

            <div className="section-header">

              <div>
                <h3>
                  Active Incidents
                </h3>

                <p>
                  Current incidents requiring attention
                </p>
              </div>

              <div className="incident-count">
                {loadingIncidents
                  ? "Loading..."
                  : `${incidents.length} Incidents`}
              </div>

            </div>


            {/* =================================================
                INCIDENTS
            ================================================= */}

            <div className="incidents">

              {loadingIncidents ? (

                <div className="empty-state">

                  <div className="empty-icon">
                    ◌
                  </div>

                  <h3>
                    Loading incidents
                  </h3>

                  <p>
                    Retrieving incidents from the
                    Incident Intelligence service.
                  </p>

                </div>

              ) : incidents.length === 0 ? (

                <div className="empty-state">

                  <div className="empty-icon">
                    ◇
                  </div>

                  <h3>
                    No incidents found
                  </h3>

                  <p>
                    There are currently no incidents available.
                  </p>

                </div>

              ) : (

                incidents.map((incident) => (

                  <button
                    key={incident.id}
                    className={`incident-item ${
                      selectedIncident?.id === incident.id
                        ? "selected"
                        : ""
                    }`}
                    onClick={() =>
                      handleSelectIncident(incident)
                    }
                  >

                    {/* INCIDENT TOP */}

                    <div className="incident-top">

                      <span className="incident-id">
                        {incident.id}
                      </span>

                      <span
                        className={`severity ${
                          incident.severity === "P1"
                            ? "severity-p1"
                            : "severity-p2"
                        }`}
                      >
                        {incident.severity || "Pending"}
                      </span>

                    </div>


                    {/* TITLE */}

                    <h4>
                      {incident.title}
                    </h4>


                    {/* META */}

                    <div className="incident-meta">

                      <span>
                        {incident.service}
                      </span>

                      <span>
                        •
                      </span>

                      <span>
                        {incident.created_at}
                      </span>

                    </div>


                    {/* STATUS */}

                    <span className="incident-status">
                      {incident.status}
                    </span>

                  </button>

                ))

              )}

            </div>

          </div>


          {/* =================================================
              INCIDENT DETAILS
          ================================================= */}

          <div className="incident-details">

            {!selectedIncident ? (

              /* =================================================
                 EMPTY DETAIL STATE
              ================================================= */

              <div className="empty-state">

                <div className="empty-icon">
                  ◇
                </div>

                <h3>
                  Select an incident
                </h3>

                <p>
                  Select an incident from the list to view
                  its details and perform AI-powered analysis.
                </p>

              </div>

            ) : (

              <>

                {/* =================================================
                    DETAILS HEADER
                ================================================= */}

                <div className="details-header">

                  <div>

                    <span
                      className={`severity ${
                        selectedIncident.severity === "P1"
                          ? "severity-p1"
                          : "severity-p2"
                      }`}
                    >
                      {selectedIncident.severity || "Pending"}
                    </span>

                    <h3>
                      {selectedIncident.title}
                    </h3>

                    <p>
                      {selectedIncident.id}
                    </p>

                  </div>

                  <span className="incident-status">
                    {selectedIncident.status}
                  </span>

                </div>


                {/* =================================================
                    DETAIL GRID
                ================================================= */}

                <div className="detail-grid">

                  <div className="detail-card">

                    <span>
                      Service
                    </span>

                    <strong>
                      {selectedIncident.service}
                    </strong>

                  </div>


                  <div className="detail-card">

                    <span>
                      Status
                    </span>

                    <strong>
                      {selectedIncident.status}
                    </strong>

                  </div>


                  <div className="detail-card">

                    <span>
                      Created
                    </span>

                    <strong>
                      {selectedIncident.created_at}
                    </strong>

                  </div>

                </div>


                {/* =================================================
                    INCIDENT OVERVIEW
                ================================================= */}

                <div className="analysis-card">

                  <div className="analysis-heading">

                    <div className="analysis-icon">
                      ✦
                    </div>

                    <div>

                      <h4>
                        Incident Overview
                      </h4>

                      <p>
                        Current incident description
                      </p>

                    </div>

                  </div>

                  <p>
                    {selectedIncident.description}
                  </p>

                </div>


                {/* =================================================
                    AI ANALYSIS
                ================================================= */}

                <div className="analysis-card">

                  <div className="analysis-heading">

                    <div className="analysis-icon">
                      AI
                    </div>

                    <div>

                      <h4>
                        AI Incident Analysis
                      </h4>

                      <p>
                        Analyze this incident using the
                        local intelligence models.
                      </p>

                    </div>

                  </div>


                  <button
                    className="analyze-button"
                    onClick={handleAnalyze}
                    disabled={analyzing}
                  >

                    {analyzing ? (

                      <>
                        <span className="spinner"></span>
                        Analyzing...
                      </>

                    ) : (

                      <>
                        Analyze Incident
                        <span>→</span>
                      </>

                    )}

                  </button>

                </div>


                {/* =================================================
                    ANALYSIS RESULT
                ================================================= */}

                {analysis && (

                  <div className="analysis-card">

                    <div className="analysis-heading">

                      <div className="analysis-icon">
                        ✓
                      </div>

                      <div>

                        <h4>
                          Analysis Result
                        </h4>

                        <p>
                          Intelligence generated from
                          the incident details.
                        </p>

                      </div>

                    </div>


                    {/* =================================================
                        ANALYSIS DETAILS
                    ================================================= */}

                    <div className="detail-grid">

                      <div className="detail-card">

                        <span>
                          Severity
                        </span>

                        <strong>
                          {analysis.severity}
                        </strong>

                      </div>


                      <div className="detail-card">

                        <span>
                          Category
                        </span>

                        <strong>
                          {analysis.category}
                        </strong>

                      </div>


                      <div className="detail-card">

                        <span>
                          Recommended Team
                        </span>

                        <strong>
                          {analysis.recommended_team}
                        </strong>

                      </div>

                    </div>


                    {/* =================================================
                        SUMMARY
                    ================================================= */}

                    <div className="analysis-card">

                      <div className="analysis-heading">

                        <div className="analysis-icon">
                          i
                        </div>

                        <div>
                          <h4>
                            Summary
                          </h4>
                        </div>

                      </div>

                      <p>
                        {analysis.summary}
                      </p>

                    </div>


                    {/* =================================================
                        RECOMMENDATION
                    ================================================= */}

                    <div className="analysis-card">

                      <div className="analysis-heading">

                        <div className="analysis-icon">
                          →
                        </div>

                        <div>
                          <h4>
                            Recommendation
                          </h4>
                        </div>

                      </div>

                      <p>
                        {analysis.reason}
                      </p>

                    </div>


                    {/* =================================================
                        CONFIDENCE
                    ================================================= */}

                    <div className="confidence">

                      <span>
                        Confidence
                      </span>

                      <strong>
                        {analysis.confidence}
                      </strong>

                    </div>

                  </div>

                )}

              </>

            )}

          </div>

        </section>

      </main>


      {/* =====================================================
          FOOTER
      ===================================================== */}

      <footer>

        <span>
          Incident Intelligence
        </span>

        <span>
          Enterprise Support Platform
        </span>

      </footer>

    </div>
  );
}

export default App;