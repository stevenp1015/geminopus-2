/**
 * Channel API Service
 */

import { API_BASE_URL, API_ENDPOINTS, getHeaders, handleAPIResponse } from './config'
import type { Channel, Message } from '@/types'

export const channelApi = {
  /**
   * List all channels
   */
  async list(): Promise<Channel[]> {
    console.log('[channelApi] list: Fetching channels...');
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.channels.list}`, {
      method: 'GET',
      headers: getHeaders(),
    });
    console.log('[channelApi] list: Raw response status:', response.status);
    // Clone the response to log its body, as body can only be read once
    const responseCloneForLogging = response.clone();
    try {
      const rawText = await responseCloneForLogging.text();
      console.log('[channelApi] list: Raw response text:', rawText);
    } catch (e) {
      console.error('[channelApi] list: Error reading raw response text for logging:', e);
    }

    const data = await handleAPIResponse<{ channels: Channel[], total: number }>(response);
    console.log('[channelApi] list: Processed data:', data);
    if (data && data.channels) {
      console.log('[channelApi] list: Returning channels:', data.channels);
      return data.channels;
    }
    console.warn('[channelApi] list: Processed data did not contain channels or data itself was nullish. Returning empty array.');
    return []; // Fallback to empty array if data.channels is not as expected
  },

  /**
   * Get a specific channel
   */
  async get(channelId: string): Promise<Channel> {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.channels.get(channelId)}`, {
      method: 'GET',
      headers: getHeaders(),
    })
    return handleAPIResponse<Channel>(response)
  },

  /**
   * Create a new channel
   */
  async create(data: {
    name: string
    description?: string
    channel_type: 'public' | 'private' | 'direct' // Keep for input clarity
    members?: string[]
  }): Promise<Channel> {
    console.log('[channelApi] create CALLED. Data:', data); // Log 1: Entry and raw data
    // Payload should now directly use channel_type, not is_private
    const payload = {
      name: data.name,
      description: data.description, // Ensure this is null or not present if undefined, matching Pydantic's Optional
      channel_type: data.channel_type, // Send the string 'public', 'private', or 'dm'
      members: data.members || [], // Ensure members is always an array
    };
    console.log('[channelApi] create: Attempting to POST to create channel. Payload:', payload); // Log 2: Final payload
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.channels.create}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload), // Send transformed payload
    })
    return handleAPIResponse<Channel>(response)
  },

  /**
   * Get channel messages
   */
  async getMessages(channelId: string, limit?: number, before?: string): Promise<Message[]> {
    const params = new URLSearchParams()
    if (limit) params.append('limit', limit.toString())
    if (before) params.append('before', before)
    
    const url = `${API_BASE_URL}${API_ENDPOINTS.channels.messages(channelId)}?${params}`
    const response = await fetch(url, {
      method: 'GET',
      headers: getHeaders(),
    })
    const data = await handleAPIResponse<{ messages: Message[], total: number, has_more: boolean }>(response)
    return data.messages
  },

  /**
   * Send a message to a channel
   */
  async sendMessage(channelId: string, data: {
    sender_id: string  // This is what chatStore provides
    content: string
  }): Promise<Message> {
    // Step 1 log is here:
    console.log('[channelApi] sendMessage: Received data argument:', JSON.stringify(data));
    const url = `${API_BASE_URL}${API_ENDPOINTS.channels.sendMessage(channelId)}`;

    // Step 2: Explicitly construct payload ensuring correct key mapping
    const payload = {
      sender: data.sender_id, // Ensure this uses data.sender_id from the destructured 'data' param
      channel_id: channelId,  // Pass channelId from the function parameter
      content: data.content
    };

    console.log('[channelApi] sendMessage: Constructed payload for backend:', JSON.stringify(payload)); // Log constructed payload
    const response = await fetch(url, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(payload),
    })
    return handleAPIResponse<Message>(response)
  },

  /**
   * Add a member to a channel
   */
  async addMember(channelId: string, minionId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.channels.addMember(channelId)}`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ minion_id: minionId }),
    })
    if (!response.ok) {
      throw new Error(`Failed to add member: ${response.statusText}`)
    }
  },

  /**
   * Remove a member from a channel
   */
  async removeMember(channelId: string, minionId: string): Promise<void> {
    const response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.channels.removeMember(channelId, minionId)}`, {
      method: 'DELETE',
      headers: getHeaders(),
    })
    if (!response.ok) {
      throw new Error(`Failed to remove member: ${response.statusText}`)
    }
  },
}