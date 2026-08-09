import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./LandingPage.css";

function ImageSlot({ src, alt, label, className = "" }) {
  return (
    <div className={`img-slot ${className}`}>
      <img src={src} alt={alt} />
      <div className="img-slot-caption">{label}</div>
    </div>
  );
}

const COMPANY_VALUES = [
  {
    title: "Engineering Excellence",
    desc: "We are dedicated to achieving flawless finishes and exact tolerances on every single project that hits our floor.",
    image: "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80",
    label: "Precision First",
  },
  {
    title: "Smart Operations",
    desc: "Our facility is powered by integrated digital intelligence, giving our team instant access to technical data and maintenance insights.",
    image: "https://images.unsplash.com/photo-1565043589221-1a6fd9ae45c7?auto=format&fit=crop&w=800&q=80",
    label: "Digital Floor",
  },
  {
    title: "Trusted Partnership",
    desc: "We have spent decades building reliable, long-term relationships with clients across the automotive and heavy industrial sectors.",
    image: "https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?auto=format&fit=crop&w=800&q=80",
    label: "Dedicated Team",
  },
];

const STATS = [
  { value: "1998", label: "Operating Since" },
  { value: "±0.005mm", label: "Precision Tolerance" },
  { value: "100%", label: "Digital Integration" },
];

export default function LandingPage() {
  const navigate = useNavigate();
  const [isScrolled, setIsScrolled] = useState(false);

  // This effect listens for scrolling and updates the state
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="landing">
      {/* The header now adds a "scrolled" class when you scroll down */}
      <header className={`landing-header ${isScrolled ? "scrolled" : ""}`}>
        <div className="landing-brand">
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
            <div className="landing-brand-subtitle">Precision components & contract manufacturing</div>
          </div>
        </div>
        <div className="landing-header-actions">
          <button className="landing-btn landing-btn-ghost" onClick={() => navigate("/admin/login")}>
            Admin Panel
          </button>
          <button className="landing-btn landing-btn-primary" onClick={() => navigate("/login")}>
            Worker Login
          </button>
        </div>
      </header>

      <section className="landing-hero">
        <div className="landing-hero-grid">
          <div>
            <div className="landing-hero-eyebrow">Welcome to NexaForge</div>
            <h1 className="landing-hero-title">
              Modern manufacturing driven by smart technology.
            </h1>
            <p className="landing-hero-sub">
              At NexaForge, we blend traditional metalworking expertise with cutting-edge digital intelligence. We are a premier contract manufacturer specializing in high-tolerance components, custom fabrication, and reliable industrial solutions.
            </p>
            <div className="landing-hero-actions">
              <button
                className="landing-btn landing-btn-primary landing-btn-lg"
                onClick={() => navigate("/login")}
              >
                Worker Login
              </button>
            </div>
          </div>

          <ImageSlot
            src="https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=1200&q=80"
            alt="NexaForge shop floor"
            label="The NexaForge Production Line"
            className="img-slot-hero"
          />
        </div>
      </section>

      <section className="landing-strip">
        <div className="landing-strip-grid">
          {STATS.map((s) => (
            <div key={s.label}>
              <div className="landing-stat-value">{s.value}</div>
              <div className="landing-stat-label">{s.label}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="landing-products">
        <div className="landing-section-label">About Our Company</div>
        <h2 className="landing-section-title">Why choose NexaForge?</h2>
        <div className="landing-product-grid">
          {COMPANY_VALUES.map((p) => (
            <div className="landing-product-card" key={p.title}>
              <ImageSlot
                src={p.image}
                alt={p.title}
                label={p.label}
                className="img-slot-product"
              />
              <div className="landing-product-title">{p.title}</div>
              <p className="landing-product-desc">{p.desc}</p>
            </div>
          ))}
        </div>
      </section>

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
              <li><Link to="/login">Worker Login</Link></li>
              <li><Link to="/admin/login">Admin Panel</Link></li>
              <li><a href="#about" onClick={(e) => e.preventDefault()}>About Us</a></li>
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
    </div>
  );
}