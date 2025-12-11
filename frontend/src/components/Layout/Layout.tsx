import { Outlet, Link, useLocation } from 'react-router-dom'
import { useAuth } from '../../contexts/AuthContext'
import {
  HomeIcon,
  CogIcon,
  DocumentTextIcon,
  PaperAirplaneIcon,
  ArrowRightOnRectangleIcon,
} from '@heroicons/react/24/outline'

const Layout = () => {
  const { logout, user } = useAuth()
  const location = useLocation()

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: HomeIcon },
    { name: 'Bot Config', href: '/bots', icon: CogIcon },
    { name: 'Presets', href: '/presets', icon: DocumentTextIcon },
    { name: 'Publisher', href: '/publish', icon: PaperAirplaneIcon },
  ]

  const isActive = (href: string) => location.pathname === href

  return (
    <div className="min-h-screen bg-gray-900">
      <div className="flex h-screen">
        {/* Sidebar */}
        <div className="hidden md:flex md:w-64 md:flex-col">
          <div className="flex flex-col flex-grow border-r border-gray-800 bg-gray-800 overflow-y-auto">
            <div className="flex items-center flex-shrink-0 px-4 py-4 border-b border-gray-700">
              <h1 className="text-xl font-bold text-white">CPSS</h1>
            </div>
            <div className="flex flex-col flex-grow mt-5">
              <nav className="flex-1 px-2 space-y-1">
                {navigation.map((item) => {
                  const Icon = item.icon
                  return (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={`${
                        isActive(item.href)
                          ? 'bg-primary-600 text-white'
                          : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                      } group flex items-center px-2 py-2 text-sm font-medium rounded-md`}
                    >
                      <Icon className="mr-3 h-5 w-5" />
                      {item.name}
                    </Link>
                  )
                })}
              </nav>
            </div>
            <div className="flex-shrink-0 flex border-t border-gray-700 p-4">
              <div className="flex items-center w-full">
                <div className="flex-1">
                  <p className="text-sm font-medium text-white">{user?.username}</p>
                </div>
                <button
                  onClick={logout}
                  className="text-gray-400 hover:text-white"
                  title="Logout"
                >
                  <ArrowRightOnRectangleIcon className="h-5 w-5" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Main content */}
        <div className="flex flex-col flex-1 overflow-hidden">
          <main className="flex-1 relative overflow-y-auto focus:outline-none">
            <div className="py-6">
              <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
                <Outlet />
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  )
}

export default Layout

