import { useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8003";

function App() {
  const [assets, setAssets] = useState([]);
  const [filter, setFilter] = useState("All");

  const [showScan, setShowScan] = useState(false);

  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [repositoryPath, setRepositoryPath] = useState(
  );

  const [scanMode, setScanMode] = useState("local");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const [selectedAsset, setSelectedAsset] = useState(null);

  // =====================================================
  // START SCAN
  // =====================================================

  const startScan = async () => {
    if (
      scanMode === "local" &&
      !repositoryPath.trim()
    ) {
      setError("Please enter the repository path.");
      return;
    }

    if (
      scanMode === "github" &&
      !repositoryUrl.trim()
    ) {
      setError("Please enter a GitHub repository URL.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const requestBody =
        scanMode === "local"
          ? {
              repository_path: repositoryPath.trim(),
            }
          : {
              repository_url: repositoryUrl.trim(),
            };

      const response = await fetch(
        `${API_URL}/discovery/scan`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(requestBody),
        }
      );

      if (!response.ok) {
        const errorData =
          await response.json().catch(() => null);

        throw new Error(
          errorData?.detail ||
            `Scan failed with status ${response.status}`
        );
      }

      const data = await response.json();

      setAssets(data.assets || []);
      setFilter("All");
      setSelectedAsset(null);
      setShowScan(false);

    } catch (err) {
      console.error(err);

      setError(
        err.message ||
          "Unable to connect to the AI Asset Discovery backend."
      );
    } finally {
      setLoading(false);
    }
  };

  // =====================================================
  // FILTER
  // =====================================================

  const filteredAssets =
    filter === "All"
      ? assets
      : assets.filter(
          (asset) =>
            asset.confidence === filter
        );

  // =====================================================
  // COUNTS
  // =====================================================

  const highCount = assets.filter(
    (asset) => asset.confidence === "High"
  ).length;

  const mediumCount = assets.filter(
    (asset) => asset.confidence === "Medium"
  ).length;

  const lowCount = assets.filter(
    (asset) => asset.confidence === "Low"
  ).length;

  // =====================================================
  // STATUS CLASS
  // =====================================================

  const getStatusClass = (status) => {
    if (!status) return "review";

    const normalized =
      status.toLowerCase();

    if (
      normalized.includes("discovered")
    ) {
      return "discovered";
    }

    return "review";
  };

  // =====================================================
  // RENDER
  // =====================================================

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

              <h3>
                Start New Repository Scan
              </h3>

              <p>
                Scan a local enterprise environment
                or a GitHub repository to discover
                AI assets.
              </p>

              {/* MODE */}

              <div className="scan-mode">

                <button
                  className={
                    scanMode === "local"
                      ? "active"
                      : ""
                  }
                  onClick={() => {
                    setScanMode("local");
                    setError("");
                  }}
                >
                  Local Repository
                </button>

                <button
                  className={
                    scanMode === "github"
                      ? "active"
                      : ""
                  }
                  onClick={() => {
                    setScanMode("github");
                    setError("");
                  }}
                >
                  GitHub Repository
                </button>

              </div>

              {/* LOCAL */}

              {scanMode === "local" && (

                <input
                  type="text"
                  placeholder="C:/path/to/repository"
                  value={repositoryPath}
                  onChange={(event) =>
                    setRepositoryPath(
                      event.target.value
                    )
                  }
                />

              )}

              {/* GITHUB */}

              {scanMode === "github" && (

                <input
                  type="url"
                  placeholder="https://github.com/owner/repository"
                  value={repositoryUrl}
                  onChange={(event) =>
                    setRepositoryUrl(
                      event.target.value
                    )
                  }
                />

              )}

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
                  {loading
                    ? "Scanning..."
                    : "Start Scan"}
                </button>

              </div>

            </div>

          )}

          {/* FILTERS */}

          <div className="filters">

            {[
              "All",
              "High",
              "Medium",
              "Low",
            ].map((item) => (

              <button
                key={item}
                className={
                  filter === item
                    ? "active"
                    : ""
                }
                onClick={() =>
                  setFilter(item)
                }
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
                      Click{" "}
                      <strong>
                        New Scan
                      </strong>{" "}
                      to start.
                    </td>

                  </tr>

                ) : (

                  filteredAssets.map(
                    (asset) => (

                      <tr
                        key={asset.id}
                        className="asset-row"
                        onClick={() =>
                          setSelectedAsset(
                            asset
                          )
                        }
                      >

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

                        <td>
                          {asset.asset_type ||
                            "Not detected"}
                        </td>

                        <td>
                          {asset.model ||
                            "Not detected"}
                        </td>

                        <td>
                          {asset.provider ||
                            "Not detected"}
                        </td>

                        <td>

                          <span
                            className={`badge ${(
                              asset.confidence ||
                              "Low"
                            ).toLowerCase()}`}
                          >
                            {asset.confidence ||
                              "Low"}
                          </span>

                        </td>

                        <td>

                          <span
                            className={`status-badge ${getStatusClass(
                              asset.status
                            )}`}
                          >
                            {asset.status ||
                              "Needs Review"}
                          </span>

                        </td>

                      </tr>

                    )
                  )

                )}

              </tbody>

            </table>

          </div>

        </section>

      </main>

      {/* DETAILS */}

      {selectedAsset && (

        <div
          className="details-overlay"
          onClick={() =>
            setSelectedAsset(null)
          }
        >

          <div
            className="details-panel"
            onClick={(event) =>
              event.stopPropagation()
            }
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
                onClick={() =>
                  setSelectedAsset(null)
                }
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
                    selectedAsset.confidence ||
                    "Low"
                  ).toLowerCase()}`}
                >
                  {selectedAsset.confidence ||
                    "Low"}
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
                  {selectedAsset.status ||
                    "Needs Review"}
                </span>

              </div>

            </div>

            {/* ASSET INFORMATION */}

            <div className="details-section">

              <h3>
                Asset Information
              </h3>

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
                    {Array.isArray(
                      selectedAsset.discovery_source
                    )
                      ? selectedAsset.discovery_source.join(
                          ", "
                        )
                      : selectedAsset.discovery_source ||
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

            {/* TOOLS */}

            {selectedAsset.tools?.length > 0 && (

              <div className="details-section">

                <h3>Tools</h3>

                <div className="tool-list">

                  {selectedAsset.tools.map(
                    (tool, index) => (

                      <span
                        className="tool-item"
                        key={index}
                      >
                        {tool}
                      </span>

                    )
                  )}

                </div>

              </div>

            )}

            {/* EVIDENCE */}

            <div className="details-section">

              <h3>
                Supporting Evidence
              </h3>

              <div className="details-evidence">

                {selectedAsset.evidence?.map(
                  (item, index) => (

                    <div
                      className="evidence-card"
                      key={index}
                    >

                      <div className="evidence-type">
                        {item.type ||
                          "Evidence"}
                      </div>

                      <div className="evidence-value">
                        {item.value ||
                          item}
                      </div>

                      <div className="evidence-file">
                        {item.file || "Unknown file"}
                      </div>

                      {item.line_number && (

                        <div className="evidence-line">
                          Line{" "}
                          {item.line_number}
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

                <h3>
                  Description
                </h3>

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