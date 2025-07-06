import type { ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Bot } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

export const Layout = ({ children }: LayoutProps) => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', current: location.pathname === '/' },
    { name: 'Insights', href: '/insights', current: location.pathname === '/insights' },
    { name: 'Trends', href: '/trends', current: location.pathname === '/trends' },
  ];

  return (
    <div className="min-h-screen bg-white">
      <nav className="bg-white border-b border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <div className="flex items-center">
                  <div className="w-8 h-8 bg-sourcegraph-600 rounded-md mr-3 flex items-center justify-center">
                    <Bot className="w-5 h-5 text-white" />
                  </div>
                  <h1 className="text-xl font-semibold text-neutral-800">
                    Agent Insights
                  </h1>
                </div>
              </div>
              <div className="ml-8 flex space-x-8">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200 ${
                      item.current
                        ? 'border-sourcegraph-600 text-sourcegraph-600'
                        : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300'
                    }`}
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  );
};
