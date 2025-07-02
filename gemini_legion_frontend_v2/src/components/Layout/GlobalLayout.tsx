// Purpose: Provides the overall layout structure for the application (e.g., header, sidebar, main content area).
// Data_Contract (Interface):
//   Props: {
//     children: React.ReactNode;
//   }
//   Returns: JSX.Element
// State_Management: Manages state related to layout visibility (e.g., sidebar open/closed) and first-visit onboarding message.
// Dependencies & Dependents: Imports React, NavLink from react-router-dom, Lucide icons. Wraps page content in App.tsx.
// V2_Compliance_Check: Confirmed.

import React, { useState, useEffect } from 'react';
import { NavLink } from 'react-router-dom';
import { Menu, X, LayoutDashboard, Users, MessageSquare, Settings, ChevronsLeft, ChevronsRight, Info, Zap } from 'lucide-react';

interface GlobalLayoutProps {
  children: React.ReactNode;
}

const ONBOARDING_MESSAGE_KEY = 'geminiLegionV2_onboardingShown';

const GlobalLayout: React.FC<GlobalLayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    const onboardingShown = localStorage.getItem(ONBOARDING_MESSAGE_KEY);
    if (!onboardingShown) {
      setShowOnboarding(true);
    }
  }, []);

  const dismissOnboarding = () => {
    localStorage.setItem(ONBOARDING_MESSAGE_KEY, 'true');
    setShowOnboarding(false);
  };

  const navItems = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Minions', href: '/minions', icon: Users },
    { name: 'Channels', href: '/channels', icon: MessageSquare },
    { name: 'Configuration', href: '/configure', icon: Settings },
  ];

  return (
    <div className="flex h-screen bg-legion-background text-legion-text_primary">
      {/* Sidebar */}
      <aside
        className={`transition-all duration-300 ease-in-out bg-legion-surface text-white ${
          sidebarOpen ? 'w-64' : 'w-20'
        } flex flex-col border-r border-legion-secondary/20 shadow-lg`}
      >
        <div className={`flex items-center justify-between p-4 border-b border-legion-secondary/20 ${sidebarOpen ? '' : 'h-[60px]'}`}>
          {sidebarOpen && (
             <Link to="/" className="flex items-center space-x-2 text-xl font-bold text-legion-primary hover:text-legion-accent transition-colors">
                <Zap size={28} />
                <span>Gemini Legion</span>
            </Link>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-md text-legion-text_secondary hover:bg-legion-primary/30 hover:text-legion-text_primary focus:outline-none focus:ring-2 focus:ring-legion-accent"
            aria-label={sidebarOpen ? "Close sidebar" : "Open sidebar"}
          >
            {sidebarOpen ? <ChevronsLeft size={24} /> : <ChevronsRight size={24} />}
          </button>
        </div>
        <nav className="flex-grow p-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                `flex items-center p-2 space-x-3 rounded-md hover:bg-legion-primary/80 hover:text-white transition-colors duration-200 ${
                  isActive ? 'bg-legion-primary text-white shadow-md' : 'text-legion-text_secondary hover:text-legion-text_primary'
                } ${sidebarOpen ? '' : 'justify-center'}`
              }
              title={item.name}
            >
              <item.icon size={sidebarOpen ? 20 : 24} className="flex-shrink-0" />
              {sidebarOpen && <span className="font-medium">{item.name}</span>}
            </NavLink>
          ))}
        </nav>
        {sidebarOpen && (
          <div className="p-4 mt-auto border-t border-legion-secondary/20">
            <p className="text-xs text-gray-500">&copy; {new Date().getFullYear()} Legion Command</p>
          </div>
        )}
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-col flex-grow overflow-hidden">
        <header className="bg-legion-surface p-4 shadow-md border-b border-legion-secondary/20">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-legion-text_primary">Legion Commander Interface</h2>
            {/* User profile / actions can go here */}
          </div>
        </header>

        {showOnboarding && (
          <div className="m-4 p-4 bg-legion-primary/20 border border-legion-primary rounded-lg shadow-lg text-legion-text_primary flex justify-between items-center">
            <div className="flex items-center">
              <Info size={24} className="text-legion-accent mr-3 flex-shrink-0" />
              <div>
                <h3 className="font-semibold">Welcome, Commander!</h3>
                <p className="text-sm text-legion-text_secondary">
                  This is the Gemini Legion V2 interface. Use the sidebar to navigate and manage your Minions.
                  Start by visiting the <NavLink to="/configure" className="underline hover:text-legion-accent">Configuration</NavLink> page to spawn your first Minion!
                </p>
              </div>
            </div>
            <button
              onClick={dismissOnboarding}
              className="p-1.5 text-legion-text_secondary hover:text-legion-text_primary hover:bg-legion-primary/50 rounded-md focus:outline-none focus:ring-2 focus:ring-legion-accent"
              aria-label="Dismiss welcome message"
            >
              <X size={20} />
            </button>
          </div>
        )}

        <main className="flex-grow p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

export default GlobalLayout;
