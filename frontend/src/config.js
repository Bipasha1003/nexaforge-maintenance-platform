// frontend/src/config.js
//
// Single source of truth for the backend base URL.
// - In production (Netlify), VITE_API_URL is set via the Netlify env
//   var you already added, pointing at your Render backend.
// - In local dev, it falls back to your own machine's FastAPI server.
//
// Every file that currently has a hardcoded "http://127.0.0.1:8000..."
// constant should import API_BASE from here instead, so there is
// exactly one place to update if the backend URL ever changes again.

export const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
