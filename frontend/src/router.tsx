import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import CopilotPage    from "@/pages/CopilotPage";
import RCAPage        from "@/pages/RCAPage";
import CompliancePage from "@/pages/CompliancePage";
import LessonsPage    from "@/pages/LessonsPage";
import AdminPage      from "@/pages/AdminPage";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/"           element={<Navigate to="/copilot" replace />} />
        <Route path="/copilot"    element={<CopilotPage />} />
        <Route path="/rca"        element={<RCAPage />} />
        <Route path="/rca/:id"    element={<RCAPage />} />
        <Route path="/compliance" element={<CompliancePage />} />
        <Route path="/lessons"    element={<LessonsPage />} />
        <Route path="/admin"      element={<AdminPage />} />
      </Routes>
    </BrowserRouter>
  );
}
