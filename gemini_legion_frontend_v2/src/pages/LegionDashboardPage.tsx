// Purpose: Displays the main dashboard for the Gemini Legion, showing overview of minions, tasks, and channels.
// Data_Contract (Interface):
//   Props: None
//   Returns: JSX.Element
// State_Management: Fetches and displays list of minions from useMinionStore. Shows zero-state message.
// Dependencies & Dependents: Imports React, useMinionStore, MinionCard, Link. Imported by App.tsx (router).
// V2_Compliance_Check: Confirmed.

import React, { useEffect } from 'react';
import { useMinionStore } from '../store/minionStore';
import MinionCard from '../components/Legion/MinionCard'; // Assuming this will be used to list minions
import { Link } from 'react-router-dom';
import { Users, AlertTriangle } from 'lucide-react';

const LegionDashboardPage: React.FC = () => {
  const { minions, fetchMinions, loadingMinions, error } = useMinionStore((state) => ({
    minions: state.minions,
    fetchMinions: state.fetchMinions,
    loadingMinions: state.loadingMinions,
    error: state.error,
  }));

  useEffect(() => {
    fetchMinions();
  }, [fetchMinions]);

  return (
    <div className="p-2">
      <h1 className="text-3xl font-bold text-legion-primary mb-6">Legion Command Dashboard</h1>

      {loadingMinions && (
        <div className="flex items-center justify-center h-40 text-legion-text_secondary">
          <Users size={32} className="animate-pulse mr-3" />
          <p className="text-xl">Loading Minion Roster...</p>
        </div>
      )}

      {error && !loadingMinions && (
        <div className="p-4 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
          <div className="flex items-center mb-2">
            <AlertTriangle size={24} className="mr-3 text-red-400" />
            <h2 className="text-xl font-semibold">Error Loading Dashboard Data</h2>
          </div>
          <p>Could not fetch Minion data: {error}</p>
        </div>
      )}

      {!loadingMinions && !error && minions.length === 0 && (
        <div className="text-center p-10 border-2 border-dashed border-legion-secondary/30 rounded-lg bg-legion-surface/30">
          <Users size={48} className="mx-auto mb-4 text-legion-accent" />
          <h2 className="text-2xl font-semibold text-legion-text_primary mb-2">The Legion is Quiet... Too Quiet.</h2>
          <p className="text-legion-text_secondary mb-6">
            No Minions are currently active or registered in the system.
            <br />
            Head over to the Configuration panel to spawn your first Minion and begin your command!
          </p>
          <Link
            to="/configure"
            className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-legion-primary hover:bg-legion-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-legion-accent transition-colors"
          >
            Go to Configuration
          </Link>
        </div>
      )}

      {!loadingMinions && !error && minions.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {minions.map((minion) => (
            <MinionCard key={minion.minion_id} minion={minion} />
          ))}
        </div>
      )}

      {/* Placeholder for other dashboard sections like Active Tasks, Recent Activity */}
      {/* <div className="mt-8">
        <h2 className="text-2xl font-semibold text-legion-primary mb-4">Active Operations</h2>
        <p className="text-legion-text_secondary">Task overview will be displayed here.</p>
      </div>
      <div className="mt-8">
        <h2 className="text-2xl font-semibold text-legion-primary mb-4">Communication Feed</h2>
        <p className="text-legion-text_secondary">Recent channel activity will appear here.</p>
      </div> */}
    </div>
  );
};

export default LegionDashboardPage;
