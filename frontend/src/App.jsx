import { Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import WorkerLogin from "./pages/WorkerLogin";
import WorkerDashboard from "./pages/WorkerDashboard";
import WorkerProfile from "./pages/WorkerProfile";
import AdminLogin from "./pages/AdminLogin";
import AdminDashboard from "./pages/AdminDashboard";
import AdminAddWorker from "./pages/AdminAddWorker";
import AdminAddDocument from "./pages/AdminAddDocument";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<WorkerLogin />} />
      <Route path="/dashboard" element={<WorkerDashboard />} />
      <Route path="/profile" element={<WorkerProfile />} />
      <Route path="/admin/login" element={<AdminLogin />} />
      <Route path="/admin" element={<AdminDashboard />} />
      <Route path="/admin/workers/new" element={<AdminAddWorker />} />
      <Route path="/admin/documents/new" element={<AdminAddDocument />} />
    </Routes>
  );
}