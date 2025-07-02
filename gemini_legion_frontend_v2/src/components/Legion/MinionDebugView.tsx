// Purpose: Displays detailed personality and emotional state for a single Minion for debugging and showcasing the #1 Holy Shit Objective.
// Data_Contract (Interface):
//   Props: {
//     minionId: string;
//   }
//   Returns: JSX.Element
// State_Management: Fetches and displays data for a specific minion from the useMinionStore. Reacts to store updates.
// Dependencies & Dependents: Imports Minion types, useMinionStore. Used by a detail page (e.g., MinionDetailPage.tsx).
// V2_Compliance_Check: Confirmed.

import React, { useEffect } from 'react';
import { useMinionStore } from '../../store/minionStore';
import { Minion, EmotionalState, MinionPersona, OpinionScore, MoodVector, EntityTypeEnum } from '../../types';

interface MinionDebugViewProps {
  minionId: string;
}

const DetailSection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
  <div style={{ marginBottom: '15px', padding: '10px', border: '1px solid #444', borderRadius: '4px' }}>
    <h3 style={{ marginTop: 0, color: '#8E2DE2' }}>{title}</h3>
    {children}
  </div>
);

const DataPair: React.FC<{ label: string; value: React.ReactNode }> = ({ label, value }) => (
  <p style={{ margin: '2px 0' }}>
    <strong style={{ color: '#aaa' }}>{label}:</strong> {value === undefined || value === null || value === '' ? <span style={{color: '#777'}}>N/A</span> : value}
  </p>
);

// New dedicated component for Emotional State
const EmotionalStateDisplay: React.FC<{ emotionalState: EmotionalState | undefined }> = ({ emotionalState }) => {
  if (!emotionalState) return <DataPair label="Emotional State" value="Not available" />;

  const renderMoodVector = (mv: MoodVector | undefined) => {
    if (!mv) return <DataPair label="Mood Vector" value="Not available" />;
    return Object.entries(mv).map(([key, value]) => (
        <DataPair key={key} label={key.charAt(0).toUpperCase() + key.slice(1)} value={value?.toFixed(2)} />
    ));
  };

  const renderOpinionScores = (scores: Record<string, OpinionScore> | undefined) => {
    if (!scores || Object.keys(scores).length === 0) return <DataPair label="Opinions" value="None recorded" />;
    return (
      <ul style={{ paddingLeft: '20px', margin: 0 }}>
        {Object.entries(scores).map(([entityId, opinion]) => (
          <li key={entityId} style={{ marginBottom: '5px' }}>
            <strong style={{color: '#bbb'}}>{entityId} ({opinion.entity_type || EntityTypeEnum.UNKNOWN}):</strong>
            <DataPair label="  Trust" value={opinion.trust?.toFixed(1)} />
            <DataPair label="  Respect" value={opinion.respect?.toFixed(1)} />
            <DataPair label="  Affection" value={opinion.affection?.toFixed(1)} />
            <DataPair label="  Overall" value={opinion.overall_sentiment?.toFixed(1)} />
            <DataPair label="  Interactions" value={opinion.interaction_count} />
            {/* Further details for notable_events could be a sub-component */}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <>
      <DetailSection title="Mood Vector">
          {renderMoodVector(emotionalState.mood)}
      </DetailSection>
      <DataPair label="Energy Level" value={emotionalState.energy_level?.toFixed(2)} />
      <DataPair label="Stress Level" value={emotionalState.stress_level?.toFixed(2)} />
      <DetailSection title="Opinion Scores">
          {renderOpinionScores(emotionalState.opinion_scores)}
      </DetailSection>
      <DataPair label="Last Updated" value={new Date(emotionalState.last_updated).toLocaleString()} />
      <DataPair label="State Version" value={emotionalState.state_version} />
    </>
  );
};

const MinionDebugView: React.FC<MinionDebugViewProps> = ({ minionId }) => {
  const { selectedMinion, fetchMinionById, loadingSelectedMinion, error } = useMinionStore((state) => ({
    selectedMinion: state.minions.find(m => m.minion_id === minionId) || state.selectedMinion, // Fallback to general selectedMinion if not in list
    fetchMinionById: state.fetchMinionById,
    loadingSelectedMinion: state.loadingSelectedMinion,
    error: state.error,
  }));

  useEffect(() => {
    // Fetch if the minionId doesn't match the selectedMinion or if selectedMinion is null
    if (!selectedMinion || selectedMinion.minion_id !== minionId) {
      fetchMinionById(minionId);
    }
  }, [minionId, fetchMinionById, selectedMinion]);

  if (loadingSelectedMinion) return <p>Loading Minion details...</p>;
  if (error && (!selectedMinion || selectedMinion.minion_id !== minionId)) return <p style={{ color: 'red' }}>Error: {error}</p>;
  if (!selectedMinion || selectedMinion.minion_id !== minionId) return <p>No Minion data available for ID: {minionId}. Try fetching.</p>;

  const { persona, emotional_state, status, creation_date } = selectedMinion;

  const renderPersona = (p: MinionPersona | undefined) => {
    if (!p) return <DataPair label="Persona" value="Not available" />;
    return (
      <>
        <DataPair label="Display Name" value={p.name} />
        <DataPair label="Base Personality" value={p.base_personality} />
        <DataPair label="Quirks" value={p.quirks?.join(', ') || 'None'} />
        <DataPair label="Catchphrases" value={p.catchphrases?.join('; ') || 'None'} />
        <DataPair label="Expertise Areas" value={p.expertise_areas?.join(', ') || 'None'} />
        <DataPair label="Allowed Tools" value={p.allowed_tools?.join(', ') || 'Default'} />
        <DataPair label="Model Name" value={p.model_name} />
        <DataPair label="Temperature" value={p.temperature} />
        <DataPair label="Max Tokens" value={p.max_tokens} />
      </>
    );
  };

  return (
    <div style={{ padding: '20px', backgroundColor: '#282c34', color: 'white', border: '1px solid #8E2DE2', borderRadius: '8px' }}>
      <h2 style={{ color: '#4A00E0', borderBottom: '1px solid #4A00E0', paddingBottom: '10px' }}>
        Minion Debug View: {persona?.name || minionId}
      </h2>

      <DetailSection title="Core Info">
        <DataPair label="Minion ID" value={selectedMinion.minion_id} />
        <DataPair label="Status" value={status} />
        <DataPair label="Creation Date" value={new Date(creation_date).toLocaleString()} />
      </DetailSection>

      <DetailSection title="Persona">
        {renderPersona(persona)}
      </DetailSection>

      <DetailSection title="Emotional State">
        <EmotionalStateDisplay emotionalState={emotional_state} />
      </DetailSection>

      {/* Placeholder for future sections like Memory Summary, Current Task, etc. */}
    </div>
  );
};

export default MinionDebugView;
