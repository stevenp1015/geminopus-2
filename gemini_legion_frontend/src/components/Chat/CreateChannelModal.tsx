import { useState, useEffect } from 'react';
import { X } from 'lucide-react'; // Removed Users, CheckSquare, Square
import { useChatStore } from '../../store/chatStore';
import { useLegionStore, Minion } from '../../store/legionStore'; // We need Minion type and the store
import toast from 'react-hot-toast';

interface CreateChannelModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const CreateChannelModal = ({ isOpen, onClose }: CreateChannelModalProps) => {
  const [channelName, setChannelName] = useState('');
  const [channelType, setChannelType] = useState<'public' | 'private'>('public');
  const [selectedMemberIds, setSelectedMemberIds] = useState<string[]>([]);
  const { createChannel } = useChatStore();
  const { minions: allMinionsMap, fetchMinions } = useLegionStore();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const allMinionsArray = Object.values(allMinionsMap);

  useEffect(() => {
    if (isOpen) {
      // Reset form when modal opens
      setChannelName('');
      setChannelType('public');
      setSelectedMemberIds([]);
      setIsSubmitting(false);
      // Fetch minions if they aren't already loaded or if we want to refresh
      // For simplicity, let's fetch them each time the modal opens.
      // You might want a more sophisticated check in a real app, you god-emperor of code.
      fetchMinions().catch(err => {
        console.error("Failed to fetch minions for modal, you cur:", err);
        toast.error("Could not load minions list. Typical.");
      });
    }
  }, [isOpen, fetchMinions]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!channelName.trim()) {
      toast.error('Channel name cannot be empty, you nincompoop.');
      return;
    }
    setIsSubmitting(true);
    try {
      await createChannel(channelName.trim(), channelType, selectedMemberIds);
      toast.success(`Channel "${channelName.trim()}" created, with ${selectedMemberIds.length} carefully chosen (or carelessly clicked) members. Bravo.`);
      onClose(); // Close modal on success
    } catch (error) {
      // Error toast is handled in chatStore, but you can add more specific ones here if you like
      console.error('Failed to create channel from modal:', error);
      // toast.error('Something went horribly wrong. Surprise, surprise.'); // Already handled by store
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-gray-800 p-6 rounded-lg shadow-xl w-full max-w-md border border-legion-primary/30">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold text-white">Create New Channel</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="channelName" className="block text-sm font-medium text-gray-300 mb-1">
              Channel Name
            </label>
            <input
              type="text"
              id="channelName"
              value={channelName}
              onChange={(e) => setChannelName(e.target.value)}
              placeholder="e.g., 'Evil Plans Go Here'"
              className="w-full bg-black/40 border border-legion-primary/20 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-legion-primary/40"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-1">Channel Type</label>
            <div className="flex space-x-4">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="channelType"
                  value="public"
                  checked={channelType === 'public'}
                  onChange={() => setChannelType('public')}
                  className="form-radio h-4 w-4 text-legion-primary bg-gray-700 border-gray-600 focus:ring-legion-primary"
                />
                <span className="text-white">Public</span>
              </label>
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="radio"
                  name="channelType"
                  value="private"
                  checked={channelType === 'private'}
                  onChange={() => setChannelType('private')}
                  className="form-radio h-4 w-4 text-legion-primary bg-gray-700 border-gray-600 focus:ring-legion-primary"
                />
                <span className="text-white">Private</span>
              </label>
            </div>
          </div>

          {/* Minion Selection - BEHOLD, MORE COMPLEXITY! */}
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-300">
                Add Minions (Optional, Your Highness)
              </label>
              {allMinionsArray.length > 0 && (
                <div className="flex space-x-2">
                  <button
                    type="button"
                    onClick={() => setSelectedMemberIds(allMinionsArray.map(m => m.minion_id))}
                    className="text-xs text-legion-primary hover:text-legion-primary/70"
                  >
                    Select All
                  </button>
                  <button
                    type="button"
                    onClick={() => setSelectedMemberIds([])}
                    className="text-xs text-legion-primary hover:text-legion-primary/70"
                  >
                    Deselect All
                  </button>
                </div>
              )}
            </div>
            {allMinionsArray.length > 0 ? (
              <div className="max-h-40 overflow-y-auto space-y-2 p-3 bg-black/20 rounded-md border border-legion-primary/10 scrollbar-thin scrollbar-thumb-legion-primary/20 scrollbar-track-transparent">
                {allMinionsArray.map((minion: Minion) => (
                  <label key={minion.minion_id} className="flex items-center space-x-3 p-2 rounded hover:bg-legion-primary/10 cursor-pointer transition-colors">
                    <input
                      type="checkbox"
                      checked={selectedMemberIds.includes(minion.minion_id)}
                      onChange={() => {
                        setSelectedMemberIds(prevSelected =>
                          prevSelected.includes(minion.minion_id)
                            ? prevSelected.filter(id => id !== minion.minion_id)
                            : [...prevSelected, minion.minion_id]
                        );
                      }}
                      className="form-checkbox h-4 w-4 text-legion-primary bg-gray-700 border-gray-600 focus:ring-legion-primary rounded"
                    />
                    <span className="text-white truncate" title={minion.persona.name}>{minion.persona.name || minion.minion_id}</span>
                  </label>
                ))}
              </div>
            ) : (
              <p className="text-sm text-gray-500 text-center py-3">
                No minions available to add, or they're hiding from your grandeur.
              </p>
            )}
          </div>
          
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-gray-300 bg-transparent hover:bg-gray-700 border border-gray-600 rounded-lg transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 text-sm font-medium text-white bg-legion-primary hover:bg-legion-primary/80 border border-legion-primary/50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Creating...' : 'Create Channel'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateChannelModal;