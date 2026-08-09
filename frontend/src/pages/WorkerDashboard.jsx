import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import ChatWidget from "../components/ChatWidget";
import "./WorkerDashboard.css";

const ME_URL = "http://127.0.0.1:8000/worker/me";
const DOCUMENTS_URL = "http://127.0.0.1:8000/admin/documents";

const FLEET_DATA = [
  {
    id: "MILL-X500",
    name: "CNC Mill X500",
    status: "Operational",
    statusColor: "green",
    lastCheckIn: "4 minutes ago",
    nextMaintenance: "Clean coolant tank strainer",
    dueIn: "Due in 12 days",
    openIssues: 0,
    manualStatus: "Manual ingested — assistant available below"
  },
  {
    id: "LATHE-T999",
    name: "Fervi Gear Head Bench Lathe",
    status: "Needs attention",
    statusColor: "orange",
    lastCheckIn: "22 minutes ago",
    nextMaintenance: "Adjust motor belt tension",
    dueIn: "Due in 4 days",
    openIssues: 1,
    manualStatus: "Manual ingested — assistant available below"
  },
  {
    id: "SAW-CPO350",
    name: "Scotchman CPO-350 Cold Saw",
    status: "Operational",
    statusColor: "green",
    lastCheckIn: "15 minutes ago",
    nextMaintenance: "Check regulator water-trap filter",
    dueIn: "Due in 30 days",
    openIssues: 0,
    manualStatus: "Manual ingested — assistant available below"
  },
  {
    id: "GRIND-KGS",
    name: "Kent Precision Surface Grinder",
    status: "Operational",
    statusColor: "green",
    lastCheckIn: "1 hour ago",
    nextMaintenance: "Clean hydraulic tank & change oil",
    dueIn: "Due in 5 days",
    openIssues: 0,
    manualStatus: "Manual ingested — assistant available below"
  },
  {
    id: "PRESS-P001",
    name: "Fervi 20-Ton Hydraulic Press",
    status: "Critical",
    statusColor: "red",
    lastCheckIn: "1 hour ago",
    nextMaintenance: "Check hydraulic oil level",
    dueIn: "Overdue by 2 days",
    openIssues: 2,
    manualStatus: "Manual ingested — assistant available below"
  }
];

export default function WorkerDashboard() {
  const navigate = useNavigate();
  const [isScrolled, setIsScrolled] = useState(false);
  const [chatSignal, setChatSignal] = useState(0);
  const [username, setUsername] = useState(localStorage.getItem("worker_username") || "worker");
  const [documents, setDocuments] = useState([
    { id: 1, name: "CNC Mill X500 (Model X500-3AX).pdf", pages: 11, status: "Ready" },
    { id: 2, name: "Fervi Gear Head Bench Lathe (Art. T999 Series).pdf", pages: 84, status: "Ready" },
    { id: 3, name: "Scotchman CPO-350 Cold Saw.pdf", pages: 92, status: "Ready" },
    { id: 4, name: "Kent Precision Surface Grinder (Models KGS818AHAHD).pdf", pages: 80, status: "Ready" },
    { id: 5, name: "Fervi Manual Hydraulic Press (Art. P00120).pdf", pages: 26, status: "Ready" }
  ]);

  const token = localStorage.getItem("worker_token");

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    // Fetch live worker details
    fetch(ME_URL, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((data) => {
        if (data.username) {
          setUsername(data.username);
          localStorage.setItem("worker_username", data.username);
        }
      })
      .catch(() => {});

    // Fetch documents dynamically from the backend database if available
    fetch(DOCUMENTS_URL, { headers: { Authorization: `Bearer ${token}` } })
      .then((r) => r.json())
      .then((data) => {
        if (Array.isArray(data) && data.length > 0) {
          setDocuments(data);
        }
      })
      .catch(() => {});
  }, [token, navigate]);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Real database file download handler
  const handleDownload = (e, doc) => {
    e.preventDefault();
    // Connects directly to the backend document download endpoint using the database document ID
    const downloadUrl = `http://127.0.0.1:8000/admin/documents/${doc.id}/download`;
    
    const link = document.createElement("a");
    link.href = doc.file_url || downloadUrl;
    link.setAttribute("download", doc.name);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="dashboard-container">
      {/* --- STICKY HEADER --- */}
      <header className={`dashboard-header ${isScrolled ? "scrolled" : ""}`}>
        <div className="dashboard-brand" onClick={() => navigate("/")} style={{cursor: "pointer"}}>
          <img 
            src="/images/company-logo.png" 
            alt="NexaForge Logo" 
            className="dashboard-logo"
          />
          <div>
            <div className="dashboard-brand-title">NexaForge</div>
            <div className="dashboard-brand-subtitle">Fleet Console</div>
          </div>
        </div>
        
        <nav className="dashboard-nav">
          <a href="#overview" className="nav-link">Overview</a>
          <a href="#capabilities" className="nav-link">Capabilities</a>
          <a href="#documents" className="nav-link">Documents</a>
          <a href="#maintenance" className="nav-link">Maintenance log</a>
        </nav>

        <div className="dashboard-header-actions">
          <button 
            className="dashboard-btn-accent" 
            onClick={() => setChatSignal(prev => prev + 1)}
          >
            Ask assistant
          </button>
          <span 
            className="profile-link" 
            onClick={() => navigate("/profile")}
          >
            My profile
          </span>
          <span className="user-badge">{username}</span>
          <button className="dashboard-btn-outline" onClick={() => navigate("/")}>Log out</button>
        </div>
      </header>

      {/* --- MAIN CONTENT --- */}
      <main className="dashboard-main">
        
        <div id="overview">
          {/* KPI Cards */}
          <div className="kpi-grid">
            <div className="kpi-card">
              <div className="kpi-label">FLEET STATUS</div>
              <div className="kpi-value text-green">3/5 operational</div>
              <div className="kpi-sub">2 machine(s) need attention</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">OPEN ISSUES (ALL MACHINES)</div>
              <div className="kpi-value">3</div>
              <div className="kpi-sub">See maintenance log below</div>
            </div>
            <div className="kpi-card">
              <div className="kpi-label">MANUALS INGESTED</div>
              <div className="kpi-value">5/5</div>
              <div className="kpi-sub">Assistant covers all ingested manuals</div>
            </div>
          </div>

          {/* Equipment Fleet */}
          <section className="dashboard-section">
            <h2 className="section-title">EQUIPMENT FLEET</h2>
            <div className="equipment-grid">
              {FLEET_DATA.map((machine) => (
                <div className="equipment-card" key={machine.id}>
                  <div className="eq-header">
                    <div>
                      <div className="eq-id">{machine.id}</div>
                      <div className="eq-name">{machine.name}</div>
                    </div>
                    <div className={`eq-status status-${machine.statusColor}`}>
                      <span className="status-dot"></span> {machine.status}
                    </div>
                  </div>
                  
                  <div className="eq-details">
                    <div className="eq-row">
                      <span className="eq-label">Last check-in</span>
                      <span className="eq-val">{machine.lastCheckIn}</span>
                    </div>
                    <div className="eq-row">
                      <span className="eq-label">Next maintenance</span>
                      <span className="eq-val font-medium">{machine.nextMaintenance}</span>
                    </div>
                    <div className="eq-row right-align">
                      <span className="eq-sub-val">{machine.dueIn}</span>
                    </div>
                    <div className="eq-row">
                      <span className="eq-label">Open issues</span>
                      <span className="eq-val">{machine.openIssues}</span>
                    </div>
                  </div>

                  <div className={`eq-footer manual-${machine.statusColor === 'green' ? 'ready' : (machine.statusColor === 'red' ? 'missing' : 'ready')}`}>
                    {machine.manualStatus}
                  </div>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* What the assistant can do - Alternate Color Section */}
        <section id="capabilities" className="dashboard-section section-card">
          <h2 className="section-title">WHAT THE ASSISTANT CAN DO</h2>
          <div className="assistant-grid">
            <div className="assistant-card">
              <h3>Troubleshoot equipment</h3>
              <p>Ask about an error code or symptom — the assistant searches the manual and cites the exact page it answered from.</p>
            </div>
            <div className="assistant-card">
              <h3>Check maintenance schedules</h3>
              <p>Ask when a part is due for service — pulled directly from the manual's maintenance-interval sections.</p>
            </div>
            <div className="assistant-card">
              <h3>Log a new issue</h3>
              <p>Report something you just noticed on the floor. It's recorded for the maintenance team to review.</p>
            </div>
            <div className="assistant-card">
              <h3>Escalate when unsure</h3>
              <p>If a question is unclear or safety-critical, the assistant hands off to a technician instead of guessing.</p>
            </div>
          </div>
        </section>

        {/* Ingested Documents */}
        <section id="documents" className="dashboard-section">
          <h2 className="section-title">INGESTED DOCUMENTS</h2>
          <div className="docs-table-container">
            <table className="docs-table">
              <thead>
                <tr>
                  <th>DOCUMENT</th>
                  <th>STATUS</th>
                  <th>PAGES</th>
                  <th>ACTION</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc, idx) => (
                  <tr key={doc.id || idx}>
                    <td className="doc-name">{doc.name}</td>
                    <td><span className="badge-ready">{doc.status || "Ready"}</span></td>
                    <td>{doc.pages || "—"}</td>
                    <td>
                      <a 
                        href="#" 
                        className="download-btn"
                        onClick={(e) => handleDownload(e, doc)}
                      >
                        ⬇ Download
                      </a>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* Maintenance Log Sample - Alternate Color Section */}
        <section id="maintenance" className="dashboard-section section-card">
          <h2 className="section-title">MAINTENANCE LOG — SAMPLE ENTRY</h2>
          <div className="log-card">
            <p>Example incident pulled from the ingested manual: technician R. Alvarez logged E-322 caused by chip sludge buildup from a missed weekly strainer cleaning; resolved by cleaning the strainer, flushing the line, and a pump reset. Ask the assistant for any other logged incident by error code or date.</p>
          </div>
        </section>

      </main>

      {/* --- FOOTER --- */}
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-section brand-section">
            <div className="footer-brand">
              <img 
                src="/images/company-logo.png" 
                alt="NexaForge Logo" 
                className="footer-logo" 
              />
              <span>NexaForge</span>
            </div>
            <p>
              Precision manufacturing backed by instant digital maintenance insights. 
              Bridging the gap between traditional metalworking and smart floor technology.
            </p>
          </div>
          
          <div className="footer-section links-section">
            <h4>Quick Links</h4>
            <ul>
              <li><Link to="/dashboard">Fleet Console</Link></li>
              <li><Link to="/admin/login">Admin Panel</Link></li>
              <li><Link to="/">Main Website</Link></li>
            </ul>
          </div>

          <div className="footer-section contact-section">
            <h4>Contact Us</h4>
            <p>📍 123 Industrial Parkway</p>
            <p>📞 (555) 019-2834</p>
            <p>✉️ operations@nexaforge.com</p>
          </div>
        </div>
        
        <div className="footer-bottom">
          © 2026 NexaForge · Internal Operations & Maintenance Intelligence Platform
        </div>
      </footer>

      <ChatWidget openSignal={chatSignal} />
    </div>
  );
}