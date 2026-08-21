import { useState } from "react";
import "./App.css";

const applications = [
  {
    id: "ai-assist",
    name: "AI Assist",
    description: "AI-powered employee assistance",
    url: "http://localhost:5173",
    icon: "✦",
  },
  {
    id: "enterprise-knowledge",
    name: "Enterprise Knowledge",
    description: "Search and explore enterprise knowledge",
    url: "http://localhost:5174",
    icon: "◈",
  },
  {
    id: "incident-intelligence",
    name: "Incident Intelligence",
    description: "Investigate and resolve incidents",
    url: "http://localhost:5175",
    icon: "⚡",
  },
];

function App() {
  const [activeApp, setActiveApp] = useState(applications[0]);

  return (
    <div className="platform">

      {/* SIDEBAR */}
      <aside className="sidebar">

        <div className="brand">
          <div className="brand-logo">N</div>

          <div>
            <h1>NOVA</h1>
            <span>Enterprise AI Platform</span>
          </div>
        </div>

        <div className="sidebar-section">
          <p className="section-label">APPLICATIONS</p>

          {applications.map((app) => (
            <button
              key={app.id}
              className={`nav-item ${
                activeApp.id === app.id ? "active" : ""
              }`}
              onClick={() => setActiveApp(app)}
            >
              <span className="nav-icon">{app.icon}</span>

              <span className="nav-content">
                <strong>{app.name}</strong>
                <small>{app.description}</small>
              </span>
            </button>
          ))}
        </div>

        <div className="sidebar-bottom">
          <div className="system-status">
            <span className="online-dot"></span>

            <div>
              <strong>Platform Online</strong>
              <small>All services available</small>
            </div>
          </div>
        </div>

      </aside>

      {/* MAIN AREA */}
      <main className="main">

        {/* TOPBAR */}
        <header className="topbar">

          <div>
            <span className="breadcrumb">NOVA / APPLICATIONS</span>

            <h2>{activeApp.name}</h2>

            <p>{activeApp.description}</p>
          </div>

          <div className="topbar-right">

            <div className="connection">
              <span className="online-dot"></span>
              Connected
            </div>

            <div className="user">
              <div className="avatar">U</div>

              <div>
                <strong>Employee</strong>
                <small>Enterprise User</small>
              </div>
            </div>

          </div>

        </header>

        {/* APPLICATION */}
        <section className="application-container">

          <div className="application-header">

            <div>
              <span className="application-tag">
                ACTIVE APPLICATION
              </span>

              <h3>{activeApp.name}</h3>
            </div>

            <span className="app-status">
              ● Running
            </span>

          </div>

          <div className="iframe-wrapper">

            <iframe
              key={activeApp.id}
              src={activeApp.url}
              title={activeApp.name}
              className="application-frame"
            />

          </div>

        </section>

      </main>
    </div>
  );
}

export default App;