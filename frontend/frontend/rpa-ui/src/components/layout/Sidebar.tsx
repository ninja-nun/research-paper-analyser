import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileText, Clock, Star, Settings, LayoutDashboard } from 'lucide-react';
import { cn } from '../../lib/utils';
export function Sidebar() {
  const location = useLocation();
  const navItems = [
  {
    icon: LayoutDashboard,
    label: 'Dashboard',
    href: '/papers'
  },
  {
    icon: Clock,
    label: 'Recent',
    href: '/papers?filter=recent'
  },
  {
    icon: Star,
    label: 'Starred',
    href: '/papers?filter=starred'
  }];

  return (
    <aside className="w-64 border-r border-gray-200 bg-gray-50/50 hidden lg:block h-[calc(100vh-4rem)] sticky top-16 overflow-y-auto">
      <div className="p-4 space-y-6">
        <div>
          <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Library
          </h3>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const isActive =
              location.pathname === item.href ||
              location.search.includes(item.href.split('?')[1] || '');
              return (
                <Link
                  key={item.label}
                  to={item.href}
                  className={cn(
                    'flex items-center gap-3 px-3 py-2 rounded-xl text-sm font-medium transition-colors',
                    isActive ?
                    'bg-blue-50 text-blue-700' :
                    'text-slate-600 hover:bg-gray-100 hover:text-slate-900'
                  )}>
                  
                  <item.icon
                    className={cn(
                      'h-4 w-4',
                      isActive ? 'text-blue-600' : 'text-slate-400'
                    )} />
                  
                  {item.label}
                </Link>);

            })}
          </nav>
        </div>

        <div>
          <h3 className="px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Recent Papers
          </h3>
          <div className="space-y-1">
            {[
            'Attention Is All You Need',
            'BERT: Pre-training...',
            'Language Models are...'].
            map((title, i) =>
            <Link
              key={i}
              to={`/papers/p${i + 1}`}
              className="flex items-start gap-3 px-3 py-2 rounded-xl text-sm text-slate-600 hover:bg-gray-100 transition-colors group">
              
                <FileText className="h-4 w-4 text-slate-400 mt-0.5 shrink-0 group-hover:text-blue-500 transition-colors" />
                <span className="line-clamp-2 leading-tight">{title}</span>
              </Link>
            )}
          </div>
        </div>
      </div>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200 bg-gray-50">
        <button className="flex items-center gap-3 px-3 py-2 w-full rounded-xl text-sm font-medium text-slate-600 hover:bg-gray-100 transition-colors">
          <Settings className="h-4 w-4 text-slate-400" />
          Settings
        </button>
      </div>
    </aside>);

}