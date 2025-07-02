// Purpose: Manages the global state for Minions, including their list, details, and real-time updates.
// Data_Contract (Interface):
//   State: {
//     minions: Minion[];
//     selectedMinion: Minion | null;
//     loadingMinions: boolean;
//     loadingSelectedMinion: boolean;
//     error: string | null;
//     spawnSuccessMessage: string | null; // Added for success state reinforcement
//   }
//   Actions: {
//     fetchMinions: () => Promise<void>;
//     fetchMinionById: (minionId: string) => Promise<void>;
//     spawnMinion: (data: CreateMinionRequest) => Promise<Minion | null>; // Returns spawned minion or null
//     clearSpawnSuccessMessage: () => void; // Added
//     setSelectedMinion: (minion: Minion | null) => void;
//     addMinion: (minion: Minion) => void;
//     removeMinion: (minionId: string) => void;
//     updateMinion: (minion: Partial<Minion> & { minion_id: string }) => void;
//   }
// State_Management: Uses Zustand for managing the Minions' state.
// Dependencies & Dependents: Imports Minion types from '~/types', minionApiService. Used by components displaying minion data.
// V2_Compliance_Check: Confirmed.

import { create } from 'zustand';
import { Minion, MinionsListResponse, CreateMinionRequest } from '../types';
import { minionApiService } from '../services/minionApiService';

interface MinionState {
  minions: Minion[];
  selectedMinion: Minion | null;
  loadingMinions: boolean;
  loadingSelectedMinion: boolean;
  error: string | null;
  spawnSuccessMessage: string | null; // For success state reinforcement

  fetchMinions: () => Promise<void>;
  fetchMinionById: (minionId: string) => Promise<void>;
  spawnMinion: (data: CreateMinionRequest) => Promise<Minion | null>; // Modified to return spawned minion or null
  clearSpawnSuccessMessage: () => void; // Action to clear the message

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
  spawnSuccessMessage: null,

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
    set({ loadingSelectedMinion: true, error: null, selectedMinion: null }); // Clear previous selected
    try {
      const minion = await minionApiService.getMinion(minionId);
      set({ selectedMinion: minion, loadingSelectedMinion: false });
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : `Failed to fetch minion ${minionId}`;
      set({ error: errorMsg, loadingSelectedMinion: false, selectedMinion: null });
      console.error(errorMsg, err);
    }
  },

  spawnMinion: async (data: CreateMinionRequest): Promise<Minion | null> => {
    set({ loadingSelectedMinion: true, error: null, spawnSuccessMessage: null }); // Use loadingSelectedMinion for spawn op
    try {
      // V2 spawnMinion now returns the full MinionResponse
      const spawnedMinion = await minionApiService.spawnMinion(data);
      // No need to call addMinion here if WebSocket event minion_spawned is reliable
      // If WebSocket is not guaranteed, uncomment:
      // get().addMinion(spawnedMinion);
      set({
        loadingSelectedMinion: false,
        spawnSuccessMessage: `Minion "${spawnedMinion.persona.name}" successfully spawned with ID: ${spawnedMinion.minion_id}!`
      });
      return spawnedMinion;
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : 'Failed to spawn minion';
      set({ error: errorMsg, loadingSelectedMinion: false });
      console.error(errorMsg, err);
      return null;
    }
  },

  clearSpawnSuccessMessage: () => {
    set({ spawnSuccessMessage: null });
  },

  setSelectedMinion: (minion: Minion | null) => {
    set({ selectedMinion: minion });
  },

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
        ? { ...state.selectedMinion, ...minionData } as Minion
        : state.selectedMinion,
    }));
  },
}));
