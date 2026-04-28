import React from 'react';
import { Link } from 'react-router-dom';
import {
  ArrowRight,
  BrainCircuit,
  FileText,
  MessageSquare,
  Zap } from
'lucide-react';
import { Button } from '../components/ui/Button';
import { usePapers } from '../hooks/useApi';
import { PaperCard } from '../components/paper/PaperCard';
import { Skeleton } from '../components/ui/Skeleton';
export function HomePage() {
  const { data: papers, isLoading } = usePapers();
  return (
    <div className="flex flex-col w-full">
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full text-center">
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full max-w-3xl opacity-30 pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-b from-blue-100 to-transparent rounded-full blur-3xl" />
        </div>

        <div className="relative z-10 max-w-3xl mx-auto space-y-8">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-blue-50 border border-blue-100 text-blue-700 text-sm font-medium mb-4">
            <Zap className="w-4 h-4" />
            <span>AI-Powered Research Assistant</span>
          </div>

          <h1 className="text-5xl sm:text-6xl font-extrabold text-slate-900 tracking-tight leading-[1.1]">
            Understand research papers{' '}
            <span className="text-blue-600">10x faster</span>
          </h1>

          <p className="text-xl text-slate-600 leading-relaxed max-w-2xl mx-auto">
            Upload any PDF. Get instant section-wise summaries, extract key
            concepts, and chat directly with the document using advanced AI.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link to="/upload">
              <Button
                size="lg"
                className="w-full sm:w-auto gap-2 px-8 rounded-full text-lg h-14">
                
                Start Analyzing
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
            <Link to="/papers">
              <Button
                variant="secondary"
                size="lg"
                className="w-full sm:w-auto rounded-full text-lg h-14 px-8">
                
                View Demo Papers
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 bg-white border-y border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-6 rounded-3xl bg-gray-50 border border-gray-100">
              <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-2xl flex items-center justify-center mb-6">
                <FileText className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">
                Smart Summarization
              </h3>
              <p className="text-slate-600 leading-relaxed">
                Get an executive brief and detailed section-by-section
                summaries. Skip the jargon and grasp the core methodology
                instantly.
              </p>
            </div>

            <div className="p-6 rounded-3xl bg-gray-50 border border-gray-100">
              <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-2xl flex items-center justify-center mb-6">
                <BrainCircuit className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">
                Concept Extraction
              </h3>
              <p className="text-slate-600 leading-relaxed">
                Automatically identify key terms, metrics, and concepts.
                Visualize relevance with interactive keyword clouds and charts.
              </p>
            </div>

            <div className="p-6 rounded-3xl bg-gray-50 border border-gray-100">
              <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-2xl flex items-center justify-center mb-6">
                <MessageSquare className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-bold text-slate-900 mb-3">
                Interactive Chat
              </h3>
              <p className="text-slate-600 leading-relaxed">
                Ask specific questions about the paper. Get precise answers
                backed by direct source citations from the document.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Recent Papers */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div className="flex items-center justify-between mb-10">
          <h2 className="text-3xl font-bold text-slate-900">Recent Papers</h2>
          <Link
            to="/papers"
            className="text-blue-600 font-medium hover:text-blue-700 flex items-center gap-1">
            
            View all <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {isLoading ?
          Array(3).
          fill(0).
          map((_, i) =>
          <Skeleton key={i} className="h-48 rounded-2xl" />
          ) :
          papers?.
          slice(0, 3).
          map((paper) => <PaperCard key={paper.id} paper={paper} />)}
        </div>
      </section>
    </div>);

}