import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BrainCircuit, Search, UploadCloud } from 'lucide-react';
import { Button } from '../ui/Button';
export function Navbar() {
  const location = useLocation();
  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/80 backdrop-blur-md">
      <div className="flex h-16 items-center px-4 md:px-6 max-w-7xl mx-auto w-full">
        <Link to="/" className="flex items-center gap-2 mr-6">
          <div className="bg-blue-600 p-1.5 rounded-lg">
            <BrainCircuit className="h-5 w-5 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight text-slate-900 hidden sm:inline-block">
            NeuroPaper
          </span>
        </Link>

        <div className="flex-1 flex items-center justify-center max-w-md mx-auto hidden md:flex">
          <div className="relative w-full">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search papers, authors, or keywords..."
              className="w-full bg-gray-50 border border-gray-200 rounded-full pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 transition-all" />
            
          </div>
        </div>

        <div className="flex items-center gap-4 ml-auto">
          <nav className="hidden sm:flex items-center gap-1">
            <Link to="/papers">
              <Button
                variant={
                location.pathname === '/papers' ? 'secondary' : 'ghost'
                }
                size="sm">
                
                Dashboard
              </Button>
            </Link>
          </nav>
          <Link to="/upload">
            <Button size="sm" className="gap-2 rounded-full px-4">
              <UploadCloud className="h-4 w-4" />
              <span className="hidden sm:inline">Upload Paper</span>
            </Button>
          </Link>
        </div>
      </div>
    </header>);

}