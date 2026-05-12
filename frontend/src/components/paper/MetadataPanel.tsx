import React from 'react';
import { Paper } from '../../types';
import {
  Users,
  Calendar,
  BookOpen,
  Link as LinkIcon,
  Building2 } from
'lucide-react';
import { Badge } from '../ui/Badge';
import { Skeleton } from '../ui/Skeleton';
interface MetadataPanelProps {
  paper?: Paper;
  isLoading?: boolean;
}
export function MetadataPanel({ paper, isLoading }: MetadataPanelProps) {
  if (isLoading) {
    return (
      <div className="bg-white rounded-2xl border border-gray-200 p-6 space-y-6">
        <Skeleton className="h-8 w-3/4" />
        <div className="space-y-3">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
        </div>
        <div className="space-y-4 pt-4 border-t border-gray-100">
          {[1, 2, 3, 4].map((i) =>
          <div key={i} className="flex gap-3">
              <Skeleton className="h-5 w-5 rounded-md" />
              <Skeleton className="h-5 w-2/3" />
            </div>
          )}
        </div>
      </div>);

  }
  if (!paper) return null;
  return (
    <div className="bg-white rounded-2xl border border-gray-200 p-6 sticky top-24 shadow-sm">
      <div className="mb-6">
        <Badge variant="success" className="mb-3">
          {paper.status}
        </Badge>
        <h1 className="text-xl font-bold text-slate-900 leading-snug mb-4">
          {paper.title}
        </h1>
      </div>

      <div className="space-y-4 text-sm">
        <div className="flex items-start gap-3 text-slate-700">
          <Users className="w-5 h-5 text-slate-400 shrink-0 mt-0.5" />
          <div>
            <span className="font-medium text-slate-900 block mb-1">
              Authors
            </span>
            <div className="text-slate-600 leading-relaxed">
              {paper.authors.join(', ')}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-3 text-slate-700">
          <Calendar className="w-5 h-5 text-slate-400 shrink-0" />
          <div>
            <span className="font-medium text-slate-900 mr-2">Year:</span>
            <span className="text-slate-600">{paper.year}</span>
          </div>
        </div>

        {paper.journal &&
        <div className="flex items-center gap-3 text-slate-700">
            <BookOpen className="w-5 h-5 text-slate-400 shrink-0" />
            <div>
              <span className="font-medium text-slate-900 mr-2">Journal:</span>
              <span className="text-slate-600">{paper.journal}</span>
            </div>
          </div>
        }

        {paper.doi &&
        <div className="flex items-center gap-3 text-slate-700">
            <LinkIcon className="w-5 h-5 text-slate-400 shrink-0" />
            <div>
              <span className="font-medium text-slate-900 mr-2">DOI:</span>
              <a
              href={`https://doi.org/${paper.doi}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline">
              
                {paper.doi}
              </a>
            </div>
          </div>
        }

        {paper.affiliations && paper.affiliations.length > 0 &&
        <div className="flex items-start gap-3 text-slate-700">
            <Building2 className="w-5 h-5 text-slate-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-medium text-slate-900 block mb-1">
                Affiliations
              </span>
              <div className="text-slate-600">
                {paper.affiliations.join(' • ')}
              </div>
            </div>
          </div>
        }
      </div>
    </div>);

}