import { useEffect, useState } from 'react'
import api from '../services/api'
import {
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline'

interface BotStatus {
  platform: string
  is_active: boolean
  last_health_check: string | null
  status: string
}

const Dashboard = () => {
  const [botsStatus, setBotsStatus] = useState<BotStatus[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchStatus()
    const interval = setInterval(fetchStatus, 30000) // Обновление каждые 30 секунд
    return () => clearInterval(interval)
  }, [])

  const fetchStatus = async () => {
    try {
      const response = await api.get('/bots/status')
      setBotsStatus(response.data)
    } catch (error) {
      console.error('Failed to fetch status:', error)
    } finally {
      setLoading(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />
      case 'offline':
        return <XCircleIcon className="h-5 w-5 text-red-500" />
      case 'error':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
      default:
        return <ClockIcon className="h-5 w-5 text-gray-500" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online':
        return 'bg-green-500/10 text-green-500 border-green-500/20'
      case 'offline':
        return 'bg-red-500/10 text-red-500 border-red-500/20'
      case 'error':
        return 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20'
      default:
        return 'bg-gray-500/10 text-gray-500 border-gray-500/20'
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <p className="mt-2 text-gray-400">System overview and bot status</p>
      </div>

      {/* Bots Status */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {loading ? (
          <div className="col-span-full text-center text-gray-400 py-8">
            Loading...
          </div>
        ) : (
          botsStatus.map((bot) => (
            <div
              key={bot.platform}
              className={`border rounded-lg p-4 ${getStatusColor(bot.status)}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(bot.status)}
                  <div>
                    <h3 className="font-semibold capitalize">{bot.platform}</h3>
                    <p className="text-sm opacity-75">{bot.status}</p>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs ${
                  bot.is_active ? 'bg-green-500/20' : 'bg-gray-500/20'
                }`}>
                  {bot.is_active ? 'Active' : 'Inactive'}
                </div>
              </div>
              {bot.last_health_check && (
                <p className="text-xs mt-2 opacity-75">
                  Last check: {new Date(bot.last_health_check).toLocaleString()}
                </p>
              )}
            </div>
          ))
        )}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h3 className="text-sm text-gray-400">Total Syncs</h3>
          <p className="text-2xl font-bold text-white mt-2">0</p>
        </div>
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h3 className="text-sm text-gray-400">Queue Size</h3>
          <p className="text-2xl font-bold text-white mt-2">0</p>
        </div>
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-4">
          <h3 className="text-sm text-gray-400">Failed Syncs</h3>
          <p className="text-2xl font-bold text-red-500 mt-2">0</p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard

