// Purpose: Root application component, sets up routing and global layout.
// Data_Contract (Interface):
//   Props: None
//   Returns: JSX.Element
// State_Management: May manage global layout state if not handled by a dedicated layout component.
// Dependencies & Dependents: Imports React, Router, pages, global styles. Imported by main.tsx.
// V2_Compliance_Check: Confirmed.

import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LegionDashboardPage from './pages/LegionDashboardPage';
import MinionDetailPage from './pages/MinionDetailPage';
import ChannelPage from './pages/ChannelPage';
import TaskPage from './pages/TaskPage';
import ConfigurationPage from './pages/ConfigurationPage';
import GlobalLayout from './components/Layout/GlobalLayout'; // Assuming a global layout component

function App() {
  return (
    <Router>
      <GlobalLayout> {/* Optional: Wrap routes in a global layout */}
        <Routes>
          <Route path="/" element={<LegionDashboardPage />} />
          <Route path="/minion/:minionId" element={<MinionDetailPage />} />
          <Route path="/channel/:channelId" element={<ChannelPage />} />
          <Route path="/task/:taskId" element={<TaskPage />} />
          <Route path="/configure" element={<ConfigurationPage />} />
          {/* Add other routes as needed */}
        </Routes>
      </GlobalLayout>
    </Router>
  );
}

export default App;
