import React, { Component } from 'react';
import { FileText, ZoomIn, ZoomOut, Download, Maximize } from 'lucide-react';
import { Button } from '../ui/Button';
export function PdfPreview() {
  return (
    <div className="flex flex-col h-[600px] bg-gray-900 rounded-2xl overflow-hidden border border-gray-200 shadow-sm">
      {/* Toolbar */}
      <div className="h-14 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4 text-gray-300">
        <div className="flex items-center gap-4 text-sm">
          <FileText className="w-5 h-5 text-gray-400" />
          <span className="truncate max-w-[200px]">document.pdf</span>
          <span className="text-gray-500">|</span>
          <span>Page 1 / 15</span>
        </div>

        <div className="flex items-center gap-2">
          <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-sm w-12 text-center">100%</span>
          <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
            <ZoomIn className="w-4 h-4" />
          </button>
          <div className="w-px h-4 bg-gray-700 mx-2" />
          <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
            <Download className="w-4 h-4" />
          </button>
          <button className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
            <Maximize className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* PDF Content Placeholder */}
      <div className="flex-1 overflow-auto p-8 flex justify-center bg-gray-900/50">
        <div className="w-full max-w-3xl bg-white shadow-2xl aspect-[1/1.4] p-12">
          {/* Mock PDF Content */}
          <div className="space-y-6 opacity-30">
            <div className="h-8 bg-gray-300 w-3/4 mx-auto mb-12" />
            <div className="h-4 bg-gray-200 w-1/4 mx-auto mb-16" />

            <div className="h-6 bg-gray-300 w-1/3 mb-4" />
            <div className="space-y-2 mb-8">
              <div className="h-3 bg-gray-200 w-full" />
              <div className="h-3 bg-gray-200 w-full" />
              <div className="h-3 bg-gray-200 w-full" />
              <div className="h-3 bg-gray-200 w-5/6" />
            </div>

            <div className="h-6 bg-gray-300 w-1/4 mb-4" />
            <div className="space-y-2">
              <div className="h-3 bg-gray-200 w-full" />
              <div className="h-3 bg-gray-200 w-full" />
              <div className="h-3 bg-gray-200 w-4/5" />
            </div>
          </div>

          <div className="absolute inset-0 flex items-center justify-center bg-gray-900/10 backdrop-blur-[1px]">
            <div className="bg-white/90 backdrop-blur-md px-6 py-4 rounded-2xl shadow-xl flex items-center gap-3 border border-gray-200">
              <FileText className="w-6 h-6 text-blue-600" />
              <div>
                <p className="font-semibold text-slate-900">
                  PDF Viewer Component
                </p>
                <p className="text-sm text-slate-500">
                  Requires react-pdf integration
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>);

}