// Purpose: Provides the overall layout structure for the application (e.g., header, sidebar, main content area).
// Data_Contract (Interface):
//   Props: {
//     children: React.ReactNode;
//   }
//   Returns: JSX.Element
// State_Management: May manage state related to layout visibility (e.g., sidebar open/closed).
// Dependencies & Dependents: Imports React. Wraps page content in App.tsx.
// V2_Compliance_Check: Confirmed.

import React from 'react';

interface GlobalLayoutProps {
  children: React.ReactNode;
}

const GlobalLayout: React.FC<GlobalLayoutProps> = ({ children }) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      {/* Placeholder for Header */}
      <header style={{ backgroundColor: '#333', padding: '1rem', color: 'white' }}>
        Gemini Legion V2 - Commander Interface
      </header>

      <div style={{ display: 'flex', flexGrow: 1 }}>
        {/* Placeholder for Sidebar */}
        <nav style={{ width: '200px', backgroundColor: '#222', padding: '1rem' }}>
          <p>Navigation</p>
          <ul>
            <li><a href="/">Dashboard</a></li>
            <li><a href="/configure">Configure</a></li>
            {/* Add other nav links here */}
          </ul>
        </nav>

        {/* Main Content Area */}
        <main style={{ flexGrow: 1, padding: '1rem', backgroundColor: '#1a1a1a' }}>
          {children}
        </main>
      </div>

      {/* Placeholder for Footer */}
      <footer style={{ backgroundColor: '#333', padding: '1rem', color: 'white', textAlign: 'center' }}>
        <p>&copy; {new Date().getFullYear()} Gemini Legion Command</p>
      </footer>
    </div>
  );
};

export default GlobalLayout;
