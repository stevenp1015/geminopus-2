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

const MinionDetailPage: React.FC = () => {
  const { minionId } = useParams<{ minionId: string }>();

  if (!minionId) {
    return (
      <div>
        <h2>Minion Detail Page</h2>
        <p style={{ color: 'red' }}>Error: Minion ID not found in URL.</p>
        <p>Usage: /minion/:minionId</p>
      </div>
    );
  }

  return (
    <div>
      {/* <h1>Minion Detail: {minionId}</h1> You can add a page title if desired */}
      <MinionDebugView minionId={minionId} />
    </div>
  );
};

export default MinionDetailPage;
