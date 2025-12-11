import { useState } from 'react'
import TelegramConfig from '@/components/BotConfig/TelegramConfig'
import DiscordConfig from '@/components/BotConfig/DiscordConfig'

const BotConfig = () => {
  const [activeTab, setActiveTab] = useState<'telegram' | 'discord'>('telegram')

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-white">Bot Configuration</h1>
        <p className="mt-2 text-gray-400">Configure Telegram and Discord bots</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-700">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('telegram')}
            className={`${
              activeTab === 'telegram'
                ? 'border-primary-500 text-primary-400'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Telegram
          </button>
          <button
            onClick={() => setActiveTab('discord')}
            className={`${
              activeTab === 'discord'
                ? 'border-primary-500 text-primary-400'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
            } whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm`}
          >
            Discord
          </button>
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'telegram' ? <TelegramConfig /> : <DiscordConfig />}
      </div>
    </div>
  )
}

export default BotConfig

