import React from 'react';
import { Link } from 'react-router-dom';
import { FileText, Calendar, Users, ChevronRight, Trash2 } from 'lucide-react';
import { Paper } from '../../types';
import { Badge } from '../ui/Badge';
interface PaperCardProps {
  paper: Paper;
  onDelete?: (id: string) => void;
  clickable?: boolean;
}
export function PaperCard({ paper, onDelete, clickable = true }: PaperCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Embedded':
        return 'success';
      case 'Summarized':
        return 'info';
      case 'Parsed':
        return 'warning';
      case 'Failed':
        return 'error';
      default:
        return 'default';
    }
  };
  return (
    <div className="group relative bg-white rounded-2xl border border-gray-200 p-5 hover:shadow-md hover:border-blue-200 transition-all duration-200 flex flex-col h-full">
      <div className="flex justify-between items-start mb-4 gap-4">
        <div className="p-2.5 bg-blue-50 text-blue-600 rounded-xl shrink-0">
          <FileText className="w-6 h-6" />
        </div>
        <Badge variant={getStatusColor(paper.status) as any}>
          {paper.status}
        </Badge>
      </div>

      <div className="flex-1 mb-4">
        {clickable ?
        <Link
          to={`/papers/${paper.id}`}
          className="block group-hover:text-blue-600 transition-colors">
          
            <h3 className="text-lg font-bold text-slate-900 line-clamp-2 mb-2 leading-tight">
              {paper.title}
            </h3>
          </Link> :
        <h3 className="text-lg font-bold text-slate-900 line-clamp-2 mb-2 leading-tight">
            {paper.title}
          </h3>
        }

        <div className="space-y-2 text-sm text-slate-600">
          <div className="flex items-start gap-2">
            <Users className="w-4 h-4 mt-0.5 shrink-0 text-slate-400" />
            <span className="line-clamp-1">{paper.authors.join(', ')}</span>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4 shrink-0 text-slate-400" />
            <span>{paper.year}</span>
          </div>
        </div>
      </div>

      <div className="pt-4 border-t border-gray-100 flex items-center justify-between mt-auto">
        <span className="text-xs text-gray-400">
          Added {new Date(paper.uploadDate).toLocaleDateString()}
        </span>
        <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
          {onDelete &&
          <button
            onClick={(e) => {
              e.preventDefault();
              onDelete(paper.id);
            }}
            className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
            title="Delete paper">
            
              <Trash2 className="w-4 h-4" />
            </button>
          }
          {clickable ?
          <Link
            to={`/papers/${paper.id}`}
            className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors">
            
              <ChevronRight className="w-5 h-5" />
            </Link> :
          null}
        </div>
      </div>
    </div>);

}
