// Purpose: Displays a summary card for a single Minion, showing key details and status.
// Data_Contract (Interface):
//   Props: {
//     minion: Minion; // Assuming Minion type is defined in src/types
//   }
//   Returns: JSX.Element
// State_Management: Primarily presentational, may have minor UI state (e.g., hover effects).
// Dependencies & Dependents: Imports Minion type. Used in LegionDashboardPage or MinionMatrixView.
// V2_Compliance_Check: Confirmed.

import React from 'react';
import { Minion } from '../../types'; // Assuming Minion type will be in src/types/index.ts or src/types/minionTypes.ts

interface MinionCardProps {
  minion: Minion;
}

const MinionCard: React.FC<MinionCardProps> = ({ minion }) => {
  return (
    <div style={{ border: '1px solid gray', padding: '10px', margin: '10px' }}>
      <h2>{minion.persona?.name || minion.minion_id}</h2>
      <p>Status: {minion.status}</p>
      <p>Personality: {minion.persona?.base_personality || 'N/A'}</p>
      {/* Display other relevant minion details */}
    </div>
  );
};

export default MinionCard;
