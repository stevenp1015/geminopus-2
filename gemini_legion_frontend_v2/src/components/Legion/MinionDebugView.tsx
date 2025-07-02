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
import { AlertCircle, Info, Brain, Smile, Zap, ShieldAlert, Users, Palette, BarChartBig, ListChecks, Briefcase, Bot } from 'lucide-react';

interface MinionDebugViewProps {
  minionId: string;
}

const DetailSection: React.FC<{ title: string; icon?: React.ElementType; children: React.ReactNode }> = ({ title, icon: Icon, children }) => (
  <div className="mb-6 p-4 bg-legion-surface/50 shadow-lg rounded-lg border border-legion-secondary/30">
    <h3 className="text-xl font-semibold text-legion-primary mb-3 flex items-center">
      {Icon && <Icon size={22} className="mr-2 text-legion-accent" />}
      {title}
    </h3>
    <div className="space-y-1 text-sm">
      {children}
    </div>
  </div>
);

const DataPair: React.FC<{ label: string; value: React.ReactNode; className?: string }> = ({ label, value, className = '' }) => (
  <p className={`py-1 ${className}`}>
    <span className="font-medium text-legion-text_secondary mr-2">{label}:</span>
    <span className="text-legion-text_primary">
      {value === undefined || value === null || (typeof value === 'string' && value.trim() === '') || (Array.isArray(value) && value.length === 0)
        ? <span className="italic text-gray-500">N/A</span>
        : value}
    </span>
  </p>
);

const EmotionalStateDisplay: React.FC<{ emotionalState: EmotionalState | undefined }> = ({ emotionalState }) => {
  if (!emotionalState) return <DataPair label="Emotional State" value="Not available" />;

  const renderMoodVector = (mv: MoodVector | undefined) => {
    if (!mv) return <DataPair label="Mood Vector" value="Not available" />;
    return (
      <div className="grid grid-cols-2 gap-x-4 gap-y-1">
        {Object.entries(mv).map(([key, value]) => (
          <DataPair key={key} label={key.charAt(0).toUpperCase() + key.slice(1)} value={value?.toFixed(2)} />
        ))}
      </div>
    );
  };

  const renderOpinionScores = (scores: Record<string, OpinionScore> | undefined) => {
    if (!scores || Object.keys(scores).length === 0) return <DataPair label="Opinions" value="None recorded" />;
    return (
      <ul className="space-y-2">
        {Object.entries(scores).map(([entityId, opinion]) => (
          <li key={entityId} className="p-2 bg-legion-background/30 rounded">
            <p className="font-semibold text-legion-accent">{entityId} <span className="text-xs text-gray-400">({opinion.entity_type || EntityTypeEnum.UNKNOWN})</span></p>
            <div className="grid grid-cols-2 gap-x-2 text-xs">
              <DataPair label="Trust" value={opinion.trust?.toFixed(1)} />
              <DataPair label="Respect" value={opinion.respect?.toFixed(1)} />
              <DataPair label="Affection" value={opinion.affection?.toFixed(1)} />
              <DataPair label="Overall" value={opinion.overall_sentiment?.toFixed(1)} />
              <DataPair label="Interactions" value={opinion.interaction_count} />
            </div>
            {/* Further details for notable_events could be a sub-component */}
          </li>
        ))}
      </ul>
    );
  };

  return (
    <>
      <DetailSection title="Mood Vector" icon={BarChartBig}>
        {renderMoodVector(emotionalState.mood)}
      </DetailSection>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-3">
        <DataPair label="Energy Level" value={`${(emotionalState.energy_level * 100)?.toFixed(0)}%`} className="p-2 bg-legion-background/30 rounded" />
        <DataPair label="Stress Level" value={`${(emotionalState.stress_level * 100)?.toFixed(0)}%`} className="p-2 bg-legion-background/30 rounded" />
      </div>
      <DetailSection title="Opinion Scores" icon={Users}>
        {renderOpinionScores(emotionalState.opinion_scores)}
      </DetailSection>
      <DataPair label="Last Updated" value={new Date(emotionalState.last_updated).toLocaleString()} />
      <DataPair label="State Version" value={emotionalState.state_version} />
    </>
  );
};

const MinionDebugView: React.FC<MinionDebugViewProps> = ({ minionId }) => {
  const { selectedMinion, fetchMinionById, loadingSelectedMinion, error } = useMinionStore((state) => ({
    selectedMinion: state.minions.find(m => m.minion_id === minionId) || state.selectedMinion,
    fetchMinionById: state.fetchMinionById,
    loadingSelectedMinion: state.loadingSelectedMinion,
    error: state.error,
  }));

  useEffect(() => {
    if (!selectedMinion || selectedMinion.minion_id !== minionId) {
      fetchMinionById(minionId);
    }
  }, [minionId, fetchMinionById, selectedMinion]);

  if (loadingSelectedMinion) {
    return (
      <div className="flex items-center justify-center h-64">
        <Zap size={32} className="text-legion-accent animate-ping mr-4" />
        <p className="text-xl text-legion-text_secondary">Summoning Minion Data...</p>
      </div>
    );
  }

  if (error && (!selectedMinion || selectedMinion.minion_id !== minionId)) {
    return (
      <div className="p-6 bg-red-900/30 border border-red-700 rounded-lg text-red-300">
        <div className="flex items-center mb-2">
          <AlertCircle size={24} className="mr-3 text-red-400" />
          <h2 className="text-xl font-semibold">Error Fetching Minion</h2>
        </div>
        <p>{error}</p>
      </div>
    );
  }

  if (!selectedMinion || selectedMinion.minion_id !== minionId) {
    return (
       <div className="p-6 bg-yellow-900/30 border border-yellow-700 rounded-lg text-yellow-300">
        <div className="flex items-center mb-2">
          <Info size={24} className="mr-3 text-yellow-400" />
          <h2 className="text-xl font-semibold">Minion Data Unavailable</h2>
        </div>
        <p>No data found for Minion ID: {minionId}. Please check the ID or try fetching again.</p>
      </div>
    );
  }

  const { persona, emotional_state, status, creation_date } = selectedMinion;

  const renderList = (items: string[] | undefined, noneText: string = 'None') => {
    if (!items || items.length === 0) return <span className="italic text-gray-500">{noneText}</span>;
    return (
      <ul className="list-disc list-inside pl-1">
        {items.map((item, index) => <li key={index} className="text-legion-text_primary">{item}</li>)}
      </ul>
    );
  }

  const renderPersona = (p: MinionPersona | undefined) => {
    if (!p) return <DataPair label="Persona" value="Not available" />;
    return (
      <>
        <DataPair label="Display Name" value={<span className="font-bold text-lg text-legion-accent">{p.name}</span>} />
        <DataPair label="Base Personality" value={<span className="italic">"{p.base_personality}"</span>} />
        <DataPair label="Quirks" value={renderList(p.quirks)} />
        <DataPair label="Catchphrases" value={renderList(p.catchphrases)} />
        <DataPair label="Expertise Areas" value={renderList(p.expertise_areas)} />
        <DataPair label="Allowed Tools" value={renderList(p.allowed_tools, 'Default Set')} />
        <div className="mt-2 pt-2 border-t border-legion-secondary/20">
            <DataPair label="Model Name" value={p.model_name} />
            <DataPair label="Temperature" value={p.temperature} />
            <DataPair label="Max Tokens" value={p.max_tokens} />
        </div>
      </>
    );
  };

  return (
    <div className="p-1 bg-gradient-to-br from-legion-primary via-legion-background to-legion-secondary shadow-2xl rounded-xl">
      <div className="p-6 bg-legion-background text-legion-text_primary rounded-lg">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-legion-secondary/30">
            <h2 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-legion-primary to-legion-accent">
              Minion Intel: {persona?.name || minionId}
            </h2>
            <Bot size={36} className="text-legion-primary" />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <DetailSection title="Core Vitals" icon={Info}>
            <DataPair label="Minion ID" value={selectedMinion.minion_id} />
            <DataPair label="Status" value={
              <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
                status === 'active' ? 'bg-green-700/50 text-green-300' :
                status === 'idle' ? 'bg-sky-700/50 text-sky-300' :
                status === 'busy' ? 'bg-yellow-700/50 text-yellow-300' :
                'bg-red-700/50 text-red-300' // error or rebooting
              }`}>{status}</span>
            } />
            <DataPair label="Creation Date" value={new Date(creation_date).toLocaleString()} />
          </DetailSection>

          <DetailSection title="Persona Configuration" icon={Palette}>
            {renderPersona(persona)}
          </DetailSection>
        </div>

        <DetailSection title="Psyche Matrix (Emotional State)" icon={Smile}>
          <EmotionalStateDisplay emotionalState={emotional_state} />
        </DetailSection>

        {/* Placeholder for future sections */}
        {/* <DetailSection title="Memory Banks" icon={Brain}>...</DetailSection> */}
        {/* <DetailSection title="Assigned Tasks" icon={ListChecks}>...</DetailSection> */}
      </div>
    </div>
  );
};

export default MinionDebugView;
