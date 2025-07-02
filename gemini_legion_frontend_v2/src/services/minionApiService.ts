// Purpose: Provides functions to interact with the backend Minion API endpoints.
// Data_Contract (Interface):
//   Methods:
//     listMinions(status?: string): Promise<MinionsListResponse>
//     getMinion(minionId: string): Promise<MinionResponse>
//     spawnMinion(data: CreateMinionRequest): Promise<MinionResponse> // Or OperationResponse
//     despawnMinion(minionId: string): Promise<OperationResponse>
//     updateMinionPersona(minionId: string, data: UpdateMinionPersonaRequest): Promise<MinionResponse>
//     updateEmotionalState(minionId: string, data: UpdateEmotionalStateRequest): Promise<MinionResponse> // Or OperationResponse
//     getMinionMemories(minionId: string, memoryType?: string, limit?: number): Promise<MemoryListResponse>
// State_Management: None directly; handles API call state (loading, error) locally per call.
// Dependencies & Dependents: Uses 'axios' or a global API client. Imported by components or state slices that need minion data.
// V2_Compliance_Check: Confirmed.

import apiClient from './apiClient'; // Assuming a shared API client setup
import {
  MinionsListResponse,
  MinionResponse,
  CreateMinionRequest,
  OperationResponse,
  UpdateMinionPersonaRequest,
  UpdateEmotionalStateRequest,
  MemoryListResponse
} from '../types'; // Assuming types are defined in src/types

const BASE_URL_V2 = '/api/v2/minions';

export const minionApiService = {
  listMinions: async (status?: string): Promise<MinionsListResponse> => {
    const params = status ? { status } : {};
    const response = await apiClient.get<MinionsListResponse>(BASE_URL_V2, { params });
    return response.data;
  },

  getMinion: async (minionId: string): Promise<MinionResponse> => {
    const response = await apiClient.get<MinionResponse>(`${BASE_URL_V2}/${minionId}`);
    return response.data;
  },

  spawnMinion: async (data: CreateMinionRequest): Promise<MinionResponse> => { // Assuming it returns the full MinionResponse on spawn
    const response = await apiClient.post<MinionResponse>(`${BASE_URL_V2}/spawn`, data);
    return response.data;
  },

  despawnMinion: async (minionId: string): Promise<OperationResponse> => {
    const response = await apiClient.delete<OperationResponse>(`${BASE_URL_V2}/${minionId}`);
    return response.data;
  },

  updateMinionPersona: async (minionId: string, data: UpdateMinionPersonaRequest): Promise<MinionResponse> => {
    const response = await apiClient.put<MinionResponse>(`${BASE_URL_V2}/${minionId}/persona`, data);
    return response.data;
  },

  updateEmotionalState: async (minionId: string, data: UpdateEmotionalStateRequest): Promise<MinionResponse> => {
    const response = await apiClient.post<MinionResponse>(`${BASE_URL_V2}/${minion_id}/emotional-state`, data);
    return response.data;
  },

  getMinionMemories: async (minionId: string, memoryType?: string, limit?: number): Promise<MemoryListResponse> => {
    const params: Record<string, string | number> = {};
    if (memoryType) params.memory_type = memoryType;
    if (limit) params.limit = limit;
    const response = await apiClient.get<MemoryListResponse>(`${BASE_URL_V2}/${minionId}/memories`, { params });
    return response.data;
  },
};
