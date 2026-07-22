import { Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import AppShell from "./layouts/AppShell";
import OverviewPage from "./pages/OverviewPage";
import IngestPage from "./pages/IngestPage";
import CopilotPage from "./pages/CopilotPage";
import RcaPage from "./pages/RcaPage";
import LessonsPage from "./pages/LessonsPage";
import CompliancePage from "./pages/CompliancePage";
import GraphExplorerPage from "./pages/GraphExplorerPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/app" element={<AppShell />}>
        <Route index element={<OverviewPage />} />
        <Route path="ingest" element={<IngestPage />} />
        <Route path="copilot" element={<CopilotPage />} />
        <Route path="rca" element={<RcaPage />} />
        <Route path="lessons" element={<LessonsPage />} />
        <Route path="compliance" element={<CompliancePage />} />
        <Route path="graph" element={<GraphExplorerPage />} />
      </Route>
    </Routes>
  );
}

export default App;
