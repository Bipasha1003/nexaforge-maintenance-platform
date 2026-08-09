import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import ChatWidget from "../components/ChatWidget";
import "./PublicSite.css";

const DOCS_URL = "http://127.0.0.1:8000/documents";

const FLEET = [
  { id: "mx500", name: "Mill X500", type: "CNC Mill", manualReady: true, status: "operational",
    lastCheckIn: "4 minutes ago", nextMaintenance: "Coolant filter — Quarterly",
    nextMaintenanceDue: "Due in 12 days", openIssues: 0 },
  { id: "lathe-210", name: "Lathe L-210", type: "CNC Lathe", manualReady: false, status: "warning",
    lastCheckIn: "22 minutes ago", nextMaintenance: "Tailstock alignment check",
    nextMaintenanceDue: "Due in 4 days", openIssues: 1 },
  { id: "press-b7", name: "Press B7", type: "Hydraulic Press", manualReady: false, status: "critical",
    lastCheckIn: "1 hour ago", nextMaintenance: "Hydraulic seal replacement",
    nextMaintenanceDue: "Overdue by 2 days", openIssues: 2 },
];

const STATUS_LABEL = { operational: "Operational", warning: "Needs attention", critical: "Critical" };

const CAPABILITIES = [
  { title: "Troubleshoot equipment", desc: "Ask about an error code or symptom — the assistant searches the manual and cites the exact page it answered from.", tool: "search_manual" },
  { title: "Check maintenance schedules", desc: "Ask when a part is due for service — pulled from the manual's maintenance-interval sections.", tool: "check_schedule" },
  { title: "Log a new issue", desc: "Report something you just noticed on the floor. It's recorded for the maintenance team to review.", tool: "log_issue" },
  { title: "Escalate when unsure", desc: "If a question is unclear or safety-critical, the assistant hands off to a technician instead of guessing.", tool: "escalate" },
];

const SECTIONS = [
  { id: "overview", label: "Overview" },
  { id: "capabilities", label: "Capabilities" },
  { id: "documents", label: "Documents" },
  { id: "log", label: "Maintenance log" },
];

function fleetSummary(fleet) {
  const operational = fleet.filter((m) => m.status === "operational").length;
  const needsAttention = fleet.filter((m) => m.status !== "operational").length;
  const openIssues = fleet.reduce((sum, m) => sum + m.openIssues, 0);
  return { total: fleet.length, operational, needsAttention, openIssues };
}

export default function PublicSite() {
  const [active, setActive] = useState("overview");
  const [docs, setDocs] = useState([]);
  const [chatSignal, setChatSignal] = useState(0);
  const summary = fleetSummary(FLEET);

  useEffect(() => {
    fetch(DOCS_URL).then((r) => r.json()).then(setDocs).catch(() => setDocs([]));
  }, []);

  function goTo(id) {
    setActive(id);
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  return (
    <div className="site">
      <header className="site-header">
        <div className="site-brand">
          <span className="site-brand-mark">MM</span>
          <div>
            <div className="site-title">Meridian Manufacturing Co.</div>
            <div className="site-subtitle">Equipment maintenance console</div>
          </div>
        </div>
        <nav className="site-nav">
          <span className="site-nav-item">Bipasha</span>
          {SECTIONS.map((s) => (
            <span key={s.id} className={`site-nav-item ${active === s.id ? "active" : ""}`} onClick={() => goTo(s.id)}>
              {s.label}
            </span>
          ))}
          <Link to="/admin/login" className="site-nav-item site-nav-admin">Admin</Link>
        </nav>
      </header>

      {/* ---- Hero ---- */}
      <section className="hero">
        <div className="hero-inner">
          <div className="hero-eyebrow">AI maintenance assistant</div>
          <h1 className="hero-title">Ask your equipment manuals a question. Get a cited answer.</h1>
          <p className="hero-sub">
            Meridian's maintenance console indexes every ingested equipment manual — error codes,
            troubleshooting steps, service intervals — and answers floor workers' questions in plain
            language, with the source page attached to every answer.
          </p>
          <div className="hero-actions">
            <button className="hero-btn hero-btn-primary" onClick={() => setChatSignal((n) => n + 1)}>
              Ask the assistant
            </button>
            <button className="hero-btn hero-btn-ghost" onClick={() => goTo("overview")}>
              View equipment fleet
            </button>
          </div>
        </div>
      </section>

      <main className="site-main">
        <section id="overview">
          <div className="site-grid">
            <section className="card">
              <div className="card-label">Fleet status</div>
              <div className="card-value ok">{summary.operational}/{summary.total} operational</div>
              <div className="card-meta">{summary.needsAttention} machine(s) need attention</div>
            </section>
            <section className="card">
              <div className="card-label">Open issues (all machines)</div>
              <div className="card-value">{summary.openIssues}</div>
              <div className="card-meta">{summary.openIssues === 0 ? "Nothing logged this week" : "See maintenance log below"}</div>
            </section>
            <section className="card">
              <div className="card-label">Manuals ingested</div>
              <div className="card-value">{FLEET.filter((m) => m.manualReady).length}/{summary.total}</div>
              <div className="card-meta">Assistant only covers ingested manuals</div>
            </section>
          </div>

          <div className="card-label" style={{ marginTop: 32, marginBottom: 12 }}>Equipment fleet</div>
          <div className="site-grid">
            {FLEET.map((m) => (
              <section key={m.id} className="card fleet-tile">
                <div className="fleet-tile-top">
                  <div>
                    <div className="card-label" style={{ marginBottom: 2 }}>{m.name}</div>
                    <div className="fleet-type">{m.type}</div>
                  </div>
                  <div className="fleet-status">
                    <span className={`status-dot ${m.status}`} />
                    <span className={`status-text ${m.status}`}>{STATUS_LABEL[m.status]}</span>
                  </div>
                </div>
                <div className="fleet-meta-row"><span>Last check-in</span><b>{m.lastCheckIn}</b></div>
                <div className="fleet-meta-row"><span>Next maintenance</span><b>{m.nextMaintenance}</b></div>
                <div className="fleet-meta-row"><span></span><span className="fleet-due">{m.nextMaintenanceDue}</span></div>
                <div className="fleet-meta-row"><span>Open issues</span><b>{m.openIssues}</b></div>
                <div className="fleet-manual-row">
                  {m.manualReady ? (
                    <span className="fleet-manual-ok">Manual ingested — assistant available below</span>
                  ) : (
                    <Link to="/admin/login" className="fleet-manual-missing">No manual uploaded — upload one in admin →</Link>
                  )}
                </div>
              </section>
            ))}
          </div>
        </section>

        {/* ---- Capabilities ---- */}
        <section id="capabilities" style={{ marginTop: 48 }}>
          <div className="card-label" style={{ marginBottom: 12 }}>What the assistant can do</div>
          <div className="site-grid">
            {CAPABILITIES.map((c) => (
              <section key={c.tool} className="card capability-card">
                <div className="capability-title">{c.title}</div>
                <p className="capability-desc">{c.desc}</p>
              </section>
            ))}
          </div>
        </section>

        <section id="documents" style={{ marginTop: 48 }}>
          <div className="card-label" style={{ marginBottom: 12 }}>Ingested documents</div>
          {docs.length === 0 ? (
            <div className="card">No documents ingested yet.</div>
          ) : (
            <table className="admin-table">
              <thead><tr><th>Document</th><th>Status</th><th>Pages</th></tr></thead>
              <tbody>
                {docs.map((d, i) => (
                  <tr key={i}>
                    <td>{d.name}</td>
                    <td><span className={`status-pill status-${d.status}`}>{d.status}</span></td>
                    <td>{d.pages ?? "—"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </section>

        <section id="log" className="card wide" style={{ marginTop: 48, marginBottom: 24 }}>
          <div className="card-label">Maintenance log — sample entry</div>
          <p className="card-help-text">
            Example incident pulled from the ingested manual: technician R. Alvarez logged
            E-322 caused by chip sludge buildup from a missed weekly strainer cleaning;
            resolved by cleaning the strainer, flushing the line, and a pump reset.
            Ask the assistant for any other logged incident by error code or date.
          </p>
        </section>
      </main>

      <footer className="site-footer">
        <div className="site-footer-inner">
          <div className="site-footer-brand">
            <span className="site-brand-mark">MM</span>
            <div>
              <div className="site-title">Meridian Manufacturing Co.</div>
              <div className="site-subtitle">Equipment maintenance console — internal tool, not a public product.</div>
            </div>
          </div>
          <div className="site-footer-links">
            <div className="site-footer-col">
              <div className="site-footer-heading">Console</div>
              {SECTIONS.map((s) => (
                <span key={s.id} className="site-footer-link" onClick={() => goTo(s.id)}>{s.label}</span>
              ))}
            </div>
            <div className="site-footer-col">
              <div className="site-footer-heading">Access</div>
              <Link to="/admin/login" className="site-footer-link">Admin login</Link>
            </div>
          </div>
        </div>
        <div className="site-footer-bottom">Built for the Manufacturing Equipment Maintenance Query Agent capstone.</div>
      </footer>

      <ChatWidget openSignal={chatSignal} />
    </div>
  );
}