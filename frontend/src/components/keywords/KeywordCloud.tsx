import React from 'react';
import { Keyword } from '../../types';
import { Skeleton } from '../ui/Skeleton';
interface KeywordCloudProps {
  keywords?: Keyword[];
  concepts?: string[];
  isLoading?: boolean;
}
export function KeywordCloud({
  keywords,
  concepts,
  isLoading
}: KeywordCloudProps) {
  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="w-full h-48 rounded-2xl" />
        <Skeleton className="w-full h-24 rounded-2xl" />
      </div>);

  }
  if (!keywords) return null;
  // Simple size calculation based on score
  const getFontSize = (score: number) => {
    const min = 0.8;
    const max = 2.5;
    return `${Math.max(min, score * max)}rem`;
  };
  const getOpacity = (score: number) => {
    return Math.max(0.4, score);
  };
  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
        <h3 className="text-lg font-bold text-slate-900 mb-6">Keyword Cloud</h3>
        <div className="flex flex-wrap gap-x-4 gap-y-2 items-center justify-center py-4">
          {keywords.map((kw, i) =>
          <span
            key={i}
            className="font-medium text-blue-600 hover:text-blue-800 transition-colors cursor-default"
            style={{
              fontSize: getFontSize(kw.score),
              opacity: getOpacity(kw.score),
              lineHeight: 1.2
            }}
            title={`Score: ${(kw.score * 100).toFixed(0)}%`}>
            
              {kw.term}
            </span>
          )}
        </div>
      </div>

      {concepts && concepts.length > 0 &&
      <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-4">
            Extracted Concepts
          </h3>
          <div className="flex flex-wrap gap-2">
            {concepts.map((concept, i) =>
          <span
            key={i}
            className="px-3 py-1.5 bg-white border border-slate-200 rounded-lg text-sm font-medium text-slate-700 shadow-sm">
            
                {concept}
              </span>
          )}
          </div>
        </div>
      }
    </div>);

}