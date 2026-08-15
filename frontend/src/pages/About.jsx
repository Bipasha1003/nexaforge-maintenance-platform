import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './About.css';
import './LandingPage.css'; 

const About = () => {
  const navigate = useNavigate();

  return (
    <div className="about-container" style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      
      {/* --- HEADER --- */}
      <header className="landing-header">
        {/* FIX 1: Added color: '#1c1a17' so it doesn't turn blue/purple */}
        <Link to="/" className="landing-brand" style={{ textDecoration: 'none', color: '#1c1a17' }}>
          <img 
            src="/images/company-logo.png" 
            alt="NexaForge Logo" 
            style={{ 
              width: "38px", 
              height: "38px", 
              objectFit: "contain",
              filter: "invert(32%) sepia(85%) saturate(1450%) hue-rotate(345deg) brightness(90%) contrast(95%)" 
            }} 
          />
          <div>
            <div className="landing-brand-title">NexaForge</div>
            <div className="landing-brand-subtitle" style={{ color: "#6b6459" }}>Precision components & contract manufacturing</div>
          </div>
        </Link>
        <div className="landing-header-actions">
          {/* FIX 2: Replaced login buttons with a single boxed Back to Home button */}
          <button className="landing-btn landing-btn-ghost" onClick={() => navigate("/")}>
            &larr; Back to Home
          </button>
        </div>
      </header>
      {/* ---------------- */}

      {/* Main Content */}
      <main className="about-main">
        <h2 className="about-page-title">About NexaForge</h2>
        
        <div className="about-content">
          <section className="about-section">
            <h3 className="about-section-title">The Project</h3>
            <p>
              NexaForge is a centralized Fleet Console and Operations Dashboard designed to bridge the gap between heavy metalworking machinery and modern, real-time data tracking. In high-tolerance manufacturing, machine downtime is incredibly expensive. NexaForge solves this by digitizing technical manuals into a searchable knowledge base.
            </p>
            <p>
              Powered by a hybrid Retrieval-Augmented Generation (RAG) pipeline, our AI assistant instantly reads ingested PDF manuals to answer equipment questions in plain language for factory floor workers—always citing the exact manual and page to ensure absolute safety and accuracy.
            </p>
          </section>

          <hr className="about-divider" />

          <section className="about-section">
            <h3 className="about-section-title">The Developer</h3>
            <p>
              NexaForge was architected and built by <strong>Bipasha Mondal</strong>. As a full-stack developer pursuing a Master of Science (M.Sc.) in Computer Science at the University of Calcutta, Bipasha specializes in building robust web applications that integrate advanced artificial intelligence.
            </p>
            <p>
              This platform serves as an extended capstone project, showcasing a deep interest in machine learning, Python-based AI architectures, and seamless React.js frontends. By combining a modern stack with intelligent LLM integrations, NexaForge represents the cutting edge of applied academic research and practical, industry-ready software engineering.
            </p>
          </section>
        </div>
      </main>

      {/* --- MATCHING LANDING PAGE FOOTER --- */}
      <footer className="landing-footer" style={{ backgroundColor: "#1c1a17", color: "#ffffff", padding: "60px 40px 20px", marginTop: "auto" }}>
        <div className="footer-content" style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: "40px", maxWidth: "1160px", margin: "0 auto", paddingBottom: "40px" }}>
          
          <div className="footer-section brand-section">
            <div className="footer-brand" style={{ display: "flex", alignItems: "center", gap: "12px", fontFamily: "'Fraunces', serif", fontSize: "22px", fontWeight: "600", color: "#ffffff", marginBottom: "16px" }}>
              <img 
                src="/images/company-logo.png" 
                alt="NexaForge Logo" 
                className="footer-logo" 
                style={{ width: "32px", height: "32px", objectFit: "contain" }}
              />
              <span>NexaForge</span>
            </div>
            <p style={{ color: "#a39f98", lineHeight: "1.6" }}>
              Precision manufacturing backed by instant digital maintenance insights. 
              Bridging the gap between traditional metalworking and smart floor technology.
            </p>
          </div>
          
          <div className="footer-section links-section">
            <h4 style={{ color: "#ffffff", fontFamily: "'Fraunces', serif", fontSize: "16px", marginBottom: "16px" }}>Quick Links</h4>
            <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
              <li style={{ marginBottom: "12px" }}><Link to="/login" style={{ color: "#a39f98", textDecoration: "none", transition: "color 0.2s" }}>Worker Login</Link></li>
              <li style={{ marginBottom: "12px" }}><Link to="/admin/login" style={{ color: "#a39f98", textDecoration: "none", transition: "color 0.2s" }}>Admin Panel</Link></li>
              <li style={{ marginBottom: "12px" }}><Link to="/about" style={{ color: "#a39f98", textDecoration: "none", transition: "color 0.2s" }}>About Us</Link></li>
            </ul>
          </div>

          <div className="footer-section contact-section">
            <h4 style={{ color: "#ffffff", fontFamily: "'Fraunces', serif", fontSize: "16px", marginBottom: "16px" }}>Contact Us</h4>
            <p style={{ color: "#a39f98", marginBottom: "10px" }}>📍 123 Industrial Parkway</p>
            <p style={{ color: "#a39f98", marginBottom: "10px" }}>📞 (555) 019-2834</p>
            <p style={{ color: "#a39f98", marginBottom: "10px" }}>✉️ operations@nexaforge.com</p>
          </div>
        </div>
        
        <div className="footer-bottom" style={{ textAlign: "center", paddingTop: "24px", borderTop: "1px solid #36322d", fontSize: "13px", maxWidth: "1160px", margin: "0 auto", color: "#9c9284" }}>
          © 2026 NexaForge · Internal Operations & Maintenance Intelligence Platform
          <br/>
          <span style={{ color: "#ffffff", fontWeight: "500", marginTop: "8px", display: "inline-block" }}>Developed by Bipasha Mondal</span>
        </div>
      </footer>
    </div>
  );
};

export default About;