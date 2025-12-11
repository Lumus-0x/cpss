import { useState, useEffect } from 'react'
import api from '../services/api'

const TelegramConfig = () => {
  const [token, setToken] = useState('')
  const [config, setConfig] = useState<any>({})
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    fetchConfig()
  }, [])

  const fetchConfig = async () => {
    try {
      const response = await api.get('/bots/configure/telegram')
      setToken(response.data.token || '')
      setConfig(response.data.config || {})
    } catch (error: any) {
      if (error.response?.status !== 404) {
        setMessage({ type: 'error', text: 'Failed to load configuration' })
      }
    }
  }

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setMessage(null)

    try {
      await api.post('/bots/configure', {
        platform: 'telegram',
        token,
        config,
      })
      setMessage({ type: 'success', text: 'Configuration saved successfully' })
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to save configuration',
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSave} className="space-y-6">
      {message && (
        <div
          className={`p-4 rounded ${
            message.type === 'success'
              ? 'bg-green-500/10 text-green-500 border border-green-500/20'
              : 'bg-red-500/10 text-red-500 border border-red-500/20'
          }`}
        >
          {message.text}
        </div>
      )}

      <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 space-y-4">
        <div>
          <label htmlFor="token" className="block text-sm font-medium text-gray-300 mb-2">
            Bot Token
          </label>
          <input
            id="token"
            type="text"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="Enter Telegram bot token"
            required
          />
          <p className="mt-1 text-xs text-gray-400">
            Get your token from @BotFather on Telegram
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Channel ID (optional)
          </label>
          <input
            type="text"
            value={config.channel_id || ''}
            onChange={(e) => setConfig({ ...config, channel_id: e.target.value })}
            className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder="e.g., -1001234567890"
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={loading}
          className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-md font-medium disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Saving...' : 'Save Configuration'}
        </button>
      </div>
    </form>
  )
}

export default TelegramConfig

