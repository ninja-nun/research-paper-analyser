import React from 'react';
import { FileText, Key, MessageSquare, Layout } from 'lucide-react';
import { cn } from '../../lib/utils';
export type TabType = 'summary' | 'keywords' | 'chat' | 'preview';
interface SectionTabsProps {
  activeTab: TabType;
  onChange: (tab: TabType) => void;
}
export function SectionTabs({ activeTab, onChange }: SectionTabsProps) {
  const tabs = [
  {
    id: 'summary',
    label: 'Summary',
    icon: Layout
  },
  {
    id: 'keywords',
    label: 'Keywords',
    icon: Key
  },
  {
    id: 'chat',
    label: 'AI Chat',
    icon: MessageSquare
  },
  {
    id: 'preview',
    label: 'PDF Preview',
    icon: FileText
  }] as
  const;
  return (
    <div className="flex space-x-1 bg-gray-100/80 p-1 rounded-xl mb-6 overflow-x-auto scrollbar-hide">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={cn(
              'flex items-center gap-2 px-4 py-2.5 rounded-lg text-sm font-medium transition-all whitespace-nowrap flex-1 justify-center',
              isActive ?
              'bg-white text-blue-700 shadow-sm' :
              'text-slate-600 hover:text-slate-900 hover:bg-gray-200/50'
            )}>
            
            <tab.icon
              className={cn(
                'w-4 h-4',
                isActive ? 'text-blue-600' : 'text-slate-400'
              )} />
            
            {tab.label}
          </button>);

      })}
    </div>);

}