// Purpose: Manages the global state for Minions, including their list, details, and real-time updates.
// Data_Contract (Interface):
//   State: {
//     minions: Minion[];
//     selectedMinion: Minion | null;
//     loadingMinions: boolean;
//     loadingSelectedMinion: boolean;
//     error: string | null;
//   }
//   Actions: {
//     fetchMinions: () => Promise<void>;
//     fetchMinionById: (minionId: string) => Promise<void>;
//     setSelectedMinion: (minion: Minion | null) => void;
//     addMinion: (minion: Minion) => void; // For WebSocket event: minion_spawned
//     removeMinion: (minionId: string) => void; // For WebSocket event: minion_despawned
//     updateMinion: (minion: Partial<Minion> & { minion_id: string }) => void; // For WebSocket event: minion_state_changed etc.
//   }
// State_Management: Uses Zustand for managing the Minions' state.
// Dependencies & Dependents: Imports Minion types from '~/types', minionApiService. Used by components displaying minion data.
// V2_Compliance_Check: Confirmed.

import { create } from 'zustand';
import { Minion, MinionsListResponse } from '../types';
import { minionApiService } from '../services/minionApiService';

interface MinionState {
  minions: Minion[];
  selectedMinion: Minion | null;
  loadingMinions: boolean;
  loadingSelectedMinion: boolean;
  error: string | null;
  fetchMinions: () => Promise<void>;
  fetchMinionById: (minionId: string) => Promise<void>;
  setSelectedMinion: (minion: Minion | null) => void;
  addMinion: (minion: Minion) => void;
  removeMinion: (minionId: string) => void;
  updateMinion: (minionData: Partial<Minion> & { minion_id: string }) => void;
}

export const useMinionStore = create<MinionState>((set, get) => ({
  minions: [],
  selectedMinion: null,
  loadingMinions: false,
  loadingSelectedMinion: false,
  error: null,

  fetchMinions: async () => {
    set({ loadingMinions: true, error: null });
    try {
      const response: MinionsListResponse = await minionApiService.listMinions();
      set({ minions: response.minions || [], loadingMinions: false });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to fetch minions';
      set({ error: errorMsg, loadingMinions: false });
      console.error(errorMsg, err);
    }
  },

  fetchMinionById: async (minionId: string) => {
    set({ loadingSelectedMinion: true, error: null });
    try {
      const minion = await minionApiService.getMinion(minionId);
      set({ selectedMinion: minion, loadingSelectedMinion: false });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : `Failed to fetch minion ${minionId}`;
      set({ error: errorMsg, loadingSelectedMinion: false, selectedMinion: null });
      console.error(errorMsg, err);
    }
  },

  setSelectedMinion: (minion: Minion | null) => {
    set({ selectedMinion: minion });
  },

  // Actions for WebSocket updates
  addMinion: (minion: Minion) => {
    set((state) => ({
      minions: [...state.minions.filter(m => m.minion_id !== minion.minion_id), minion],
    }));
  },

  removeMinion: (minionId: string) => {
    set((state) => ({
      minions: state.minions.filter((m) => m.minion_id !== minionId),
      selectedMinion: state.selectedMinion?.minion_id === minionId ? null : state.selectedMinion,
    }));
  },

  updateMinion: (minionData: Partial<Minion> & { minion_id: string }) => {
    set((state) => ({
      minions: state.minions.map((m) =>
        m.minion_id === minionData.minion_id ? { ...m, ...minionData } : m
      ),
      selectedMinion: state.selectedMinion?.minion_id === minionData.minion_id
        ? { ...state.selectedMinion, ...minionData } as Minion // Type assertion needed as selectedMinion can be null
        : state.selectedMinion,
    }));
  },
}));

// Example usage (typically in a component):
// const minions = useMinionStore((state) => state.minions);
// const fetchMinions = useMinionStore((state) => state.fetchMinions);
// useEffect(() => { fetchMinions(); }, [fetchMinions]);
