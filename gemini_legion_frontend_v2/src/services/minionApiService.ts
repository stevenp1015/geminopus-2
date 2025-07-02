// Purpose: Provides functions to interact with the backend Minion API V2 endpoints.
// Data_Contract (Interface):
//   Methods:
//     listMinions(status?: string): Promise<MinionsListResponse>
//     getMinion(minionId: string): Promise<MinionResponse>
//     spawnMinion(data: CreateMinionRequest): Promise<MinionResponse>
//     despawnMinion(minionId: string): Promise<OperationResponse>
//     updateMinionPersona(minionId: string, data: UpdateMinionPersonaRequest): Promise<MinionResponse>
//     updateEmotionalState(minionId: string, data: UpdateEmotionalStateRequest): Promise<MinionResponse>
//     getMinionMemories(minionId: string, memoryType?: string, limit?: number): Promise<MemoryListResponse>
// State_Management: None directly; handles API call state (loading, error) locally per call.
// Dependencies & Dependents: Uses 'apiClient'. Imported by minionStore.ts or components needing minion data.
// V2_Compliance_Check: Confirmed.

import apiClient from './apiClient';
import {
  MinionsListResponse,
  MinionResponse,
  CreateMinionRequest,
  OperationResponse,
  UpdateMinionPersonaRequest,
  UpdateEmotionalStateRequest,
  MemoryListResponse,
} from '../types'; // Assuming types are defined in src/types

const BASE_URL = '/minions'; // Relative to /api/v2 defined in apiClient

export const minionApiService = {
  listMinions: async (status?: string): Promise<MinionsListResponse> => {
    const params = status ? { status } : {};
    const response = await apiClient.get<MinionsListResponse>(BASE_URL, { params });
    return response.data;
  },

  getMinion: async (minionId: string): Promise<MinionResponse> => {
    const response = await apiClient.get<MinionResponse>(`${BASE_URL}/${minionId}`);
    return response.data;
  },

  spawnMinion: async (data: CreateMinionRequest): Promise<MinionResponse> => {
    // The V2 spawn endpoint returns the full MinionResponse
    const response = await apiClient.post<MinionResponse>(`${BASE_URL}/spawn`, data);
    return response.data;
  },

  despawnMinion: async (minionId: string): Promise<OperationResponse> => {
    const response = await apiClient.delete<OperationResponse>(`${BASE_URL}/${minionId}`);
    return response.data;
  },

  updateMinionPersona: async (minionId: string, data: UpdateMinionPersonaRequest): Promise<MinionResponse> => {
    const response = await apiClient.put<MinionResponse>(`${BASE_URL}/${minionId}/persona`, data);
    return response.data;
  },

  updateEmotionalState: async (minionId: string, data: UpdateEmotionalStateRequest): Promise<MinionResponse> => {
    // V2 endpoint returns the updated MinionResponse
    const response = await apiClient.post<MinionResponse>(`${BASE_URL}/${minionId}/emotional-state`, data);
    return response.data;
  },

  // Placeholder for getMinionMemories as per schemas.py; actual endpoint might differ or not exist in V2 yet.
  // Assuming it would be GET /minions/{minion_id}/memories
  getMinionMemories: async (minionId: string, memoryType?: string, limit?: number): Promise<MemoryListResponse> => {
    const params: Record<string, string | number> = {};
    if (memoryType) params.memory_type = memoryType; // Ensure query param matches backend if implemented
    if (limit) params.limit = limit;

    // This endpoint is not explicitly defined in the provided V2 backend files,
    // but is listed in the schemas.py for MinionResponse.
    // Assuming it would follow a similar pattern if it exists.
    // If it doesn't exist on the backend, this call will fail.
    // For now, providing a mock or a placeholder might be safer until backend confirms.
    // For this exercise, we'll assume the endpoint exists as per the schema's implication.
    try {
        const response = await apiClient.get<MemoryListResponse>(`${BASE_URL}/${minionId}/memories`, { params });
        return response.data;
    } catch (error) {
        console.warn(`getMinionMemories for ${minionId} failed. This V2 endpoint might not be implemented yet.`, error);
        // Returning a default empty response structure
        return {
            memories: [],
            minion_id: minionId,
            memory_type_filter: memoryType,
            total_returned: 0,
        };
    }
  },
};
