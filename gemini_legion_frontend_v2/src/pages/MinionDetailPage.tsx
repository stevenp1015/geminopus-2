// Purpose: Provides a page to display the detailed debug view for a specific Minion.
// Data_Contract (Interface):
//   Props: None (minionId is obtained from URL params)
//   Returns: JSX.Element
// State_Management: None directly; orchestrates display of MinionDebugView.
// Dependencies & Dependents: Imports React, useParams (from react-router-dom), MinionDebugView. Imported by App.tsx (router).
// V2_Compliance_Check: Confirmed.

import React from 'react';
import { useParams } from 'react-router-dom';
import MinionDebugView from '../components/Legion/MinionDebugView';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';

const MinionDetailPage: React.FC = () => {
  const { minionId } = useParams<{ minionId: string }>();

  if (!minionId) {
    return (
      <div className="p-4 text-red-500">
        <h2 className="text-2xl font-semibold mb-4">Minion Detail Error</h2>
        <p>Minion ID not found in URL.</p>
        <p className="mt-2">
          Please ensure you are navigating via a valid link, e.g., /minion/:minionId
        </p>
        <Link to="/" className="mt-4 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-legion-primary hover:bg-legion-secondary focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-legion-accent">
          <ArrowLeft size={18} className="mr-2" />
          Back to Dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link to="/" className="inline-flex items-center text-legion-primary hover:text-legion-secondary transition-colors">
          <ArrowLeft size={20} className="mr-2" />
          Back to Legion Dashboard
        </Link>
      </div>
      {/* The MinionDebugView itself will have its own title based on the minion's name */}
      <MinionDebugView minionId={minionId} />
    </div>
  );
};

export default MinionDetailPage;
