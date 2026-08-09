import { useState, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import "./Admin.css";

const UPLOAD_URL = "http://127.0.0.1:8000/admin/upload";

export default function AdminAddDocument() {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [notice, setNotice] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const token = localStorage.getItem("admin_token");

  async function handleFiles(files) {
    const file = files?.[0];
    if (!file) return;

    // 1. UPDATED: Allow PDFs, text files, and images
    const allowedTypes = [
      "application/pdf", 
      "text/plain", 
      "image/jpeg", 
      "image/png"
    ];
    
    if (!allowedTypes.includes(file.type)) {
      setNotice({ type: "error", text: "Please upload a PDF, TXT, PNG, or JPG file." });
      return;
    }

    setUploading(true);
    setNotice(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(UPLOAD_URL, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (!res.ok) throw new Error();
      setNotice({ type: "success", text: `${file.name} uploaded. Processing in background.` });
      setTimeout(() => navigate("/admin"), 2000);
    } catch {
      setNotice({ type: "error", text: "Upload failed — check backend terminal." });
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="admin-shell admin-shell-center">
      <div className="admin-login-card" style={{ maxWidth: 500 }}>
        {/* 2. UPDATED UI TEXT */}
        <div className="admin-login-title" style={{ marginBottom: 16 }}>Add a Document</div>
        
        <div
          className={`admin-drop ${dragOver ? "admin-drop-active" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files); }}
          onClick={() => fileInputRef.current?.click()}
        >
          {/* 3. UPDATED ACCEPT ATTRIBUTE */}
          <input 
            ref={fileInputRef} 
            type="file" 
            accept=".pdf, .txt, .png, .jpg, .jpeg" 
            hidden 
            onChange={(e) => handleFiles(e.target.files)} 
          />
          <div className="admin-drop-title">
            {uploading ? "Uploading…" : "Drop a PDF, text file, or image here, or click to browse"}
          </div>
        </div>

        {notice && <div className={`admin-notice admin-notice-${notice.type}`}>{notice.text}</div>}
        
        <Link to="/admin" className="admin-btn admin-btn-ghost" style={{ textDecoration: "none", marginTop: 16 }}>
          Cancel
        </Link>
      </div>
    </div>
  );
}