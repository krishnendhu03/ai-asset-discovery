import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8003";

function App() {
  const [assets, setAssets] = useState([]);
  const [filter, setFilter] = useState("All");

  const [showScan, setShowScan] = useState(false);
  const [repositoryPath, setRepositoryPath] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [selectedAsset, setSelectedAsset] = useState(null);

  // --------------------------------------------------
  // START SCAN
  // --------------------------------------------------

  const startScan = async () => {
    if (!repositoryPath.trim()) {
      setError("Please enter a repository path.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/discovery/scan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repository_path: repositoryPath.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`Scan failed with status ${response.status}`);
      }

      const data = await response.json();

      setAssets(data.assets || []);
      setFilter("All");
      setSelectedAsset(null);
      setShowScan(false);
      setRepositoryPath("");
    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to the scanner. Make sure the FastAPI backend is running."
      );
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // FILTER
  // --------------------------------------------------

  const filteredAssets =
    filter === "All"
      ? assets
      : assets.filter((asset) => asset.confidence === filter);

  // --------------------------------------------------
  // COUNTS
  // --------------------------------------------------

  const highCount = assets.filter(
    (asset) => asset.confidence === "High"
  ).length;

  const mediumCount = assets.filter(
    (asset) => asset.confidence === "Medium"
  ).length;

  const lowCount = assets.filter(
    (asset) => asset.confidence === "Low"
  ).length;

  // --------------------------------------------------
  // HELPER
  // --------------------------------------------------

  const getStatusClass = (status) => {
  if (!status) return "review";

  const normalized = status.toLowerCase();

  if (normalized === "discovered") {
    return "discovered";
  }

  return "review";
};
  // --------------------------------------------------
  // RENDER
  // --------------------------------------------------

  return (
    <div className="app">

      {/* HEADER */}

      <header className="topbar">
        <div>
          <h1>AI Asset Discovery</h1>

          <p>
            Enterprise AI discovery, evidence and inventory
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          Scanner Online
        </div>
      </header>

      <main className="container">

        {/* SUMMARY */}

        <section className="summary-grid">

          <div className="summary-card">
            <span>Total Assets</span>
            <strong>{assets.length}</strong>
          </div>

          <div className="summary-card high">
            <span>High Confidence</span>
            <strong>{highCount}</strong>
          </div>

          <div className="summary-card medium">
            <span>Medium Confidence</span>
            <strong>{mediumCount}</strong>
          </div>

          <div className="summary-card low">
            <span>Low Confidence</span>
            <strong>{lowCount}</strong>
          </div>

        </section>

        {/* INVENTORY */}

        <section className="inventory">

          <div className="inventory-header">

            <div>
              <h2>AI Asset Inventory</h2>

              <p>
                Discovered AI systems and supporting evidence
              </p>
            </div>

            <button
              className="scan-button"
              onClick={() => {
                setShowScan(true);
                setError("");
              }}
            >
              + New Scan
            </button>

          </div>

          {/* SCAN PANEL */}

          {showScan && (
            <div className="scan-panel">

              <h3>Start New Repository Scan</h3>

              <p>
                Enter the local repository path that should be
                analyzed for AI assets.
              </p>

              <input
                type="text"
                placeholder="C:\path\to\repository"
                value={repositoryPath}
                onChange={(event) =>
                  setRepositoryPath(event.target.value)
                }
              />

              {error && (
                <div className="error-message">
                  {error}
                </div>
              )}

              <div className="scan-actions">

                <button
                  className="cancel-button"
                  onClick={() => {
                    setShowScan(false);
                    setError("");
                  }}
                >
                  Cancel
                </button>

                <button
                  className="start-button"
                  onClick={startScan}
                  disabled={loading}
                >
                  {loading ? "Scanning..." : "Start Scan"}
                </button>

              </div>

            </div>
          )}

          {/* FILTERS */}

          <div className="filters">

            {["All", "High", "Medium", "Low"].map((item) => (
              <button
                key={item}
                className={filter === item ? "active" : ""}
                onClick={() => setFilter(item)}
              >
                {item}
              </button>
            ))}

          </div>

          {/* TABLE */}

          <div className="table-wrapper">

            <table>

              <thead>
                <tr>
                  <th>Asset</th>
                  <th>Type</th>
                  <th>Model</th>
                  <th>Provider</th>
                  <th>Confidence</th>
                  <th>Status</th>
                </tr>
              </thead>

              <tbody>

                {filteredAssets.length === 0 ? (

                  <tr>
                    <td
                      colSpan="6"
                      className="empty-state"
                    >
                      No AI assets discovered yet.
                      Click <strong>New Scan</strong> to start.
                    </td>
                  </tr>

                ) : (

                  filteredAssets.map((asset) => (

                    <tr
                      key={asset.id}
                      className="asset-row"
                      onClick={() => setSelectedAsset(asset)}
                    >

                      {/* ASSET */}

                      <td>
                        <div className="asset-name">

                          <strong>
                            {asset.name}
                          </strong>

                          <small>
                            {asset.id}
                          </small>

                        </div>
                      </td>

                      {/* TYPE */}

                      <td>
                        {asset.asset_type || "Not detected"}
                      </td>

                      {/* MODEL */}

                      <td>
                        {asset.model || "Not detected"}
                      </td>

                      {/* PROVIDER */}

                      <td>
                        {asset.provider || "Not detected"}
                      </td>

                      {/* CONFIDENCE */}

                      <td>
                        <span
                          className={`badge ${(
                            asset.confidence || "Low"
                          ).toLowerCase()}`}
                        >
                          {asset.confidence || "Low"}
                        </span>
                      </td>

                      {/* STATUS */}

                      <td>
                        <span
                          className={`status-badge ${getStatusClass(
                            asset.status
                          )}`}
                        >
                          {asset.status || "Needs Review"}
                        </span>
                      </td>

                    </tr>

                  ))

                )}

              </tbody>

            </table>

          </div>

        </section>

      </main>

      {/* =================================================
          ASSET DETAILS PANEL
      ================================================= */}

      {selectedAsset && (

        <div
          className="details-overlay"
          onClick={() => setSelectedAsset(null)}
        >

          <div
            className="details-panel"
            onClick={(event) => event.stopPropagation()}
          >

            {/* HEADER */}

            <div className="details-header">

              <div>

                <span className="details-label">
                  AI ASSET
                </span>

                <h2>
                  {selectedAsset.name}
                </h2>

                <span className="details-id">
                  {selectedAsset.id}
                </span>

              </div>

              <button
                className="close-button"
                onClick={() => setSelectedAsset(null)}
              >
                ×
              </button>

            </div>

            {/* CONFIDENCE + STATUS */}

            <div className="details-confidence">

              <div>
                <span className="details-meta-label">
                  Confidence
                </span>

                <span
                  className={`badge ${(
                    selectedAsset.confidence || "Low"
                  ).toLowerCase()}`}
                >
                  {selectedAsset.confidence || "Low"}
                </span>
              </div>

              <div>
                <span className="details-meta-label">
                  Status
                </span>

                <span
                  className={`status-badge ${getStatusClass(
                    selectedAsset.status
                  )}`}
                >
                  {selectedAsset.status || "Needs Review"}
                </span>
              </div>

            </div>

            {/* ASSET INFORMATION */}

            <div className="details-section">

              <h3>Asset Information</h3>

              <div className="details-grid">

                <div>
                  <span>Type</span>

                  <strong>
                    {selectedAsset.asset_type ||
                      "Not detected"}
                  </strong>
                </div>

                <div>
                  <span>Model</span>

                  <strong>
                    {selectedAsset.model ||
                      "Not detected"}
                  </strong>
                </div>

                <div>
                  <span>Provider</span>

                  <strong>
                    {selectedAsset.provider ||
                      "Not detected"}
                  </strong>
                </div>

                <div>
                  <span>Location</span>

                  <strong>
                    {selectedAsset.location ||
                      "Not detected"}
                  </strong>
                </div>

                <div>
                  <span>Application</span>

                  <strong>
                    {selectedAsset.application ||
                      "Not detected"}
                  </strong>
                </div>

                <div>
                  <span>Purpose</span>

                  <strong>
                    {selectedAsset.purpose ||
                      "Not detected"}
                  </strong>
                </div>

                <div>
                  <span>Discovery Source</span>

                  <strong>
                    {selectedAsset.discovery_source ||
                      "Local Repository"}
                  </strong>
                </div>

                <div>
                  <span>Category</span>

                  <strong>
                    {selectedAsset.category ||
                      "AI/ML"}
                  </strong>
                </div>

              </div>

            </div>

            {/* SUPPORTING EVIDENCE */}

            <div className="details-section">

              <h3>Supporting Evidence</h3>

              <div className="details-evidence">

                {selectedAsset.evidence?.map(
                  (item, index) => (

                    <div
                      className="evidence-card"
                      key={index}
                    >

                      <div className="evidence-type">
                        {item.type || "Evidence"}
                      </div>

                      <div className="evidence-value">
                        {item.value || item}
                      </div>

                      {item.file && (
                        <div className="evidence-file">
                          {item.file}
                        </div>
                      )}

                    </div>

                  )
                )}

              </div>

            </div>

            {/* DESCRIPTION */}

            {selectedAsset.description && (

              <div className="details-section">

                <h3>Description</h3>

                <p className="details-description">
                  {selectedAsset.description}
                </p>

              </div>

            )}

          </div>

        </div>

      )}

    </div>
  );
}

export default App;