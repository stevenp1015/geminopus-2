import { useState, useEffect } from 'react'
import { Save, X, Brain, Zap, MessageSquare } from 'lucide-react' // Corrected imports
import type { Minion } from '../../types'
import PersonaEditor from './PersonaEditor'
import ToolSelector from './ToolSelector'
import EmotionalStateConfig from './EmotionalStateConfig'

interface MinionConfigProps {
  minion: Minion
  onSave: (config: Partial<Minion>) => void
  onCancel: () => void
}

export default function MinionConfig({ minion, onSave, onCancel }: MinionConfigProps) {
  const [config, setConfig] = useState<Partial<Minion>>({
    // name: minion.persona.name, // Name is part of persona, no need for top-level name in config state
    persona: { ...minion.persona },
    emotional_state: { ...minion.emotional_state }
  })
  
  const [activeTab, setActiveTab] = useState<'persona' | 'tools' | 'emotional'>('persona')
  const [hasChanges, setHasChanges] = useState(false)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    // Check if there are any changes
    const hasPersonaChanges = JSON.stringify(config.persona) !== JSON.stringify(minion.persona)
    const hasEmotionalChanges = JSON.stringify(config.emotional_state) !== JSON.stringify(minion.emotional_state)
    // Check if top-level config.name (if it were used) differs from minion.persona.name
    // const hasNameChange = config.name !== minion.persona.name; // If 'name' was part of Partial<Minion> state
    setHasChanges(hasPersonaChanges || hasEmotionalChanges /* || hasNameChange */)
  }, [config, minion])

  const handleSave = async () => {
    setSaving(true)
    // Construct the payload for onSave.
    // It should be Partial<Minion>, but changes are primarily in persona and emotional_state.
    // The onSave prop likely expects the relevant parts that can be updated.
    // If onSave internally calls minionApi.updatePersona, it needs just the persona.
    // If it's a more general update, it might take more.
    // Given the context, it's likely persona changes that are primary.
    // The current onSave(config) passes the whole Partial<Minion> config object.
    // This implies the parent component (MinionDetail) handles what to do with it.
    // MinionDetail's onSavePersona calls minionApi.updatePersona which takes persona data.
    // This suggests MinionConfig's onSave should probably pass config.persona.
    // However, MinionConfig also allows editing emotional_state.
    // The onSave type is (config: Partial<Minion>) => void.
    // So, passing `config` is type-correct. The parent `MinionDetail` must then extract
    // the relevant parts for specific API calls (persona vs emotional state).
    try {
      await onSave(config)
    } finally {
      setSaving(false)
    }
  }

  const tabs = [
    { id: 'persona', label: 'Persona', icon: Brain },
    { id: 'tools', label: 'Tools & Capabilities', icon: Zap },
    { id: 'emotional', label: 'Emotional State', icon: MessageSquare }
  ]

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50">
      <div className="bg-gray-900 rounded-lg border border-legion-primary/20 w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white/10">
          <h2 className="text-2xl font-bold text-white">Configure {minion.persona.name}</h2>
          <button
            onClick={onCancel}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="border-b border-white/10">
          <div className="flex">
            {tabs.map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex items-center space-x-2 px-6 py-3 transition-colors ${
                    activeTab === tab.id
                      ? 'bg-legion-primary/20 text-legion-primary border-b-2 border-legion-primary'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'persona' && config.persona && (
            <PersonaEditor
              persona={config.persona}
              onChange={(personaUpdates) => setConfig(prevConfig => ({
                ...prevConfig,
                persona: { ...prevConfig.persona!, ...personaUpdates }
              }))}
            />
          )}
          
          {activeTab === 'tools' && config.persona && (
            <ToolSelector
              selectedTools={config.persona.allowed_tools || []}
              onChange={(tools) => setConfig(prevConfig => ({
                ...prevConfig,
                persona: { ...prevConfig.persona!, allowed_tools: tools }
              }))}
            />
          )}
          
          {activeTab === 'emotional' && config.emotional_state && (
            <EmotionalStateConfig
              emotionalState={config.emotional_state}
              onChange={(emotionalStateUpdates) => setConfig(prevConfig => ({
                ...prevConfig,
                emotional_state: { ...prevConfig.emotional_state!, ...emotionalStateUpdates}
              }))}
            />
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-white/10">
          <div className="text-sm text-gray-400">
            {hasChanges && "You have unsaved changes"}
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onCancel}
              className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!hasChanges || saving}
              className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Save className="w-4 h-4" />
              <span>{saving ? 'Saving...' : 'Save Changes'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}