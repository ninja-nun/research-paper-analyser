import React, { useState } from 'react';
import { PaperSummary } from '../../types';
import { ChevronDown, ChevronUp, Sparkles } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Skeleton } from '../ui/Skeleton';
interface SummaryViewProps {
  summary?: PaperSummary;
  isLoading?: boolean;
}
export function SummaryView({ summary, isLoading }: SummaryViewProps) {
  const [openSection, setOpenSection] = useState<string | null>('abstract');
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="bg-indigo-50/50 rounded-2xl p-6 border border-indigo-100">
          <Skeleton className="h-6 w-48 mb-4" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-3/4" />
        </div>
        <div className="space-y-3">
          {[1, 2, 3, 4].map((i) =>
          <Skeleton key={i} className="h-14 w-full rounded-xl" />
          )}
        </div>
      </div>);

  }
  if (!summary)
  return (
    <div className="text-center py-12 text-gray-500">
        No summary available.
      </div>);

  const sections = [
  {
    id: 'abstract',
    title: 'Abstract',
    content: summary.sections.abstract
  },
  {
    id: 'introduction',
    title: 'Introduction',
    content: summary.sections.introduction
  },
  {
    id: 'methodology',
    title: 'Methodology',
    content: summary.sections.methodology
  },
  {
    id: 'results',
    title: 'Results',
    content: summary.sections.results
  },
  {
    id: 'discussion',
    title: 'Discussion',
    content: summary.sections.discussion
  },
  {
    id: 'conclusion',
    title: 'Conclusion',
    content: summary.sections.conclusion
  }].
  filter((s) => s.content);
  return (
    <div className="space-y-8">
      {/* AI Brief */}
      <div className="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-2xl p-6 border border-indigo-100/50 relative overflow-hidden">
        <div className="absolute top-0 right-0 p-6 opacity-10">
          <Sparkles className="w-24 h-24" />
        </div>
        <div className="relative z-10">
          <h3 className="flex items-center gap-2 text-lg font-bold text-indigo-900 mb-3">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            AI Executive Brief
          </h3>
          <p className="text-slate-700 leading-relaxed text-lg">
            {summary.brief}
          </p>
        </div>
      </div>

      {/* Accordion Sections */}
      <div>
        <h3 className="text-lg font-bold text-slate-900 mb-4 px-1">
          Section Summaries
        </h3>
        <div className="space-y-3">
          {sections.map((section) => {
            const isOpen = openSection === section.id;
            return (
              <div
                key={section.id}
                className={cn(
                  'bg-white border rounded-xl overflow-hidden transition-all duration-200',
                  isOpen ?
                  'border-blue-200 shadow-sm' :
                  'border-gray-200 hover:border-gray-300'
                )}>
                
                <button
                  onClick={() => setOpenSection(isOpen ? null : section.id)}
                  className="w-full flex items-center justify-between p-4 text-left focus:outline-none">
                  
                  <span className="font-semibold text-slate-800">
                    {section.title}
                  </span>
                  {isOpen ?
                  <ChevronUp className="w-5 h-5 text-gray-400" /> :

                  <ChevronDown className="w-5 h-5 text-gray-400" />
                  }
                </button>

                <div
                  className={cn(
                    'px-4 overflow-hidden transition-all duration-300 ease-in-out',
                    isOpen ? 'max-h-96 pb-4 opacity-100' : 'max-h-0 opacity-0'
                  )}>
                  
                  <div className="pt-2 border-t border-gray-100 text-slate-600 leading-relaxed prose prose-sm max-w-none">
                    {section.content}
                  </div>
                </div>
              </div>);

          })}
        </div>
      </div>
    </div>);

}