import React, { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import { PaperCard } from '../components/paper/PaperCard';
import { Button } from '../components/ui/Button';
import { DEMO_PAPERS } from '../lib/demoPapers';
import { usePapers } from '../hooks/useApi';
export function PapersPage() {
  const { data: recentUploads, isLoading } = usePapers();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const filteredPapers = DEMO_PAPERS.filter((paper) => {
    const matchesSearch =
    paper.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    paper.authors.some((a) =>
    a.toLowerCase().includes(searchQuery.toLowerCase())
    );
    const matchesStatus =
    statusFilter === 'all' ||
    paper.status.toLowerCase() === statusFilter.toLowerCase();
    return matchesSearch && matchesStatus;
  });
  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto w-full">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 mb-2">My Papers</h1>
          <p className="text-slate-600">
            Manage and analyze your research library
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="relative w-full md:w-64">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search library..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full bg-white border border-gray-200 rounded-xl pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all shadow-sm" />
            
          </div>
          <Button variant="secondary" className="gap-2 shrink-0">
            <Filter className="w-4 h-4" />
            <span className="hidden sm:inline">Filter</span>
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-8 overflow-x-auto pb-2 scrollbar-hide">
        {['All', 'Embedded', 'Summarized', 'Parsed'].map((status) =>
        <button
          key={status}
          onClick={() => setStatusFilter(status.toLowerCase())}
          className={`px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors ${statusFilter === status.toLowerCase() ? 'bg-slate-800 text-white' : 'bg-white text-slate-600 border border-gray-200 hover:bg-gray-50'}`}>
          
            {status}
          </button>
        )}
      </div>

      <div className="mb-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-slate-900">Recent Uploads</h2>
          <span className="text-sm text-slate-500">Up to 2 most recent uploads are stored</span>
        </div>

        {isLoading ?
        <div className="text-slate-500">Loading recent uploads...</div> :
        recentUploads.length === 0 ?
        <div className="bg-white rounded-3xl border border-dashed border-gray-300 p-8 text-slate-500">
            No uploaded papers yet.
          </div> :
        <div className="grid sm:grid-cols-2 xl:grid-cols-2 gap-6">
            {recentUploads.map((paper) =>
          <PaperCard
            key={paper.id}
            paper={paper} />

          )}
          </div>
        }
      </div>

      {/* Demo Papers */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-slate-900">Demo Papers</h2>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredPapers.length === 0 ?
        <div className="col-span-full text-center py-20 bg-white rounded-3xl border border-dashed border-gray-300">
            <p className="text-slate-500 mb-4">
              No papers found matching your criteria.
            </p>
            <Button
            variant="secondary"
            onClick={() => {
              setSearchQuery('');
              setStatusFilter('all');
            }}>
            
              Clear Filters
            </Button>
          </div> :

        filteredPapers.map((paper) =>
        <PaperCard
          key={paper.id}
          paper={paper}
          clickable={false} />

        )
        }
      </div>
    </div>);

}
