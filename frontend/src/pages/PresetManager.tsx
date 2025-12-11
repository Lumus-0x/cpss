import { useState, useEffect } from 'react'
import api from '../services/api'
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/react/24/outline'

interface Preset {
  id: number
  name: string
  platform: string
  config: any
  is_active: boolean
  created_at: string
}

const PresetManager = () => {
  const [presets, setPresets] = useState<Preset[]>([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [editingPreset, setEditingPreset] = useState<Preset | null>(null)

  useEffect(() => {
    fetchPresets()
  }, [])

  const fetchPresets = async () => {
    try {
      const response = await api.get('/presets')
      setPresets(response.data)
    } catch (error) {
      console.error('Failed to fetch presets:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this preset?')) return

    try {
      await api.delete(`/presets/${id}`)
      fetchPresets()
    } catch (error) {
      console.error('Failed to delete preset:', error)
    }
  }

  if (loading) {
    return <div className="text-center text-gray-400 py-8">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white">Presets</h1>
          <p className="mt-2 text-gray-400">Manage publication presets</p>
        </div>
        <button
          onClick={() => {
            setEditingPreset(null)
            setShowModal(true)
          }}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md font-medium flex items-center space-x-2"
        >
          <PlusIcon className="h-5 w-5" />
          <span>New Preset</span>
        </button>
      </div>

      {presets.length === 0 ? (
        <div className="text-center py-12 bg-gray-800 border border-gray-700 rounded-lg">
          <p className="text-gray-400">No presets yet. Create your first preset!</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {presets.map((preset) => (
            <div
              key={preset.id}
              className="bg-gray-800 border border-gray-700 rounded-lg p-4"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-semibold text-white">{preset.name}</h3>
                  <p className="text-sm text-gray-400 capitalize">{preset.platform}</p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => {
                      setEditingPreset(preset)
                      setShowModal(true)
                    }}
                    className="text-gray-400 hover:text-white"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(preset.id)}
                    className="text-red-400 hover:text-red-300"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="mt-4 pt-4 border-t border-gray-700">
                <p className="text-xs text-gray-400">
                  Created: {new Date(preset.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}

      {showModal && (
        <PresetModal
          preset={editingPreset}
          onClose={() => {
            setShowModal(false)
            setEditingPreset(null)
          }}
          onSave={() => {
            setShowModal(false)
            fetchPresets()
          }}
        />
      )}
    </div>
  )
}

const PresetModal = ({
  preset,
  onClose,
  onSave,
}: {
  preset: Preset | null
  onClose: () => void
  onSave: () => void
}) => {
  const [name, setName] = useState(preset?.name || '')
  const [platform, setPlatform] = useState(preset?.platform || 'telegram')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const data = {
        name,
        platform,
        config: {},
      }

      if (preset) {
        await api.put(`/presets/${preset.id}`, data)
      } else {
        await api.post('/presets', data)
      }
      onSave()
    } catch (error) {
      console.error('Failed to save preset:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 max-w-md w-full">
        <h2 className="text-xl font-bold text-white mb-4">
          {preset ? 'Edit Preset' : 'New Preset'}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Platform
            </label>
            <select
              value={platform}
              onChange={(e) => setPlatform(e.target.value)}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white"
            >
              <option value="telegram">Telegram</option>
              <option value="discord">Discord</option>
              <option value="youtube">YouTube</option>
              <option value="rutube">Rutube</option>
              <option value="twitch">Twitch</option>
            </select>
          </div>
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-600 text-gray-300 rounded-md hover:bg-gray-700"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default PresetManager

