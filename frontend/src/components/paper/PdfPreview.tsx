import React, { useEffect, useMemo, useState } from 'react';
import { FileText, ZoomIn, ZoomOut, Download, Maximize } from 'lucide-react';
import { api } from '../../lib/api';
import { Paper } from '../../types';

interface PdfPreviewProps {
  paper?: Paper;
}

export function PdfPreview({ paper }: PdfPreviewProps) {
  const [zoom, setZoom] = useState(100);
  const [blobUrl, setBlobUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pdfUrl = useMemo(() => {
    if (!paper?.id) {
      return null;
    }
    return api.getPdfUrl(paper.id);
  }, [paper?.id]);

  const viewerUrl = useMemo(() => {
    if (!blobUrl) {
      return null;
    }
    return `${blobUrl}#toolbar=0&navpanes=0&zoom=${zoom}`;
  }, [blobUrl, zoom]);

  const fileName = paper?.originalFilename || `${paper?.title || 'uploaded-paper'}.pdf`;

  const changeZoom = (delta: number) => {
    setZoom((current) => Math.min(200, Math.max(50, current + delta)));
  };

  useEffect(() => {
    if (!pdfUrl) {
      setBlobUrl(null);
      setError(null);
      return;
    }

    let cancelled = false;
    let objectUrl: string | null = null;

    const loadPdfBlob = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch(pdfUrl);
        if (!response.ok) {
          throw new Error('Failed to load PDF preview');
        }

        const blob = await response.blob();
        objectUrl = URL.createObjectURL(blob);

        if (!cancelled) {
          setBlobUrl((current) => {
            if (current) {
              URL.revokeObjectURL(current);
            }
            return objectUrl;
          });
        }
      } catch (err) {
        if (!cancelled) {
          setBlobUrl(null);
          setError(err instanceof Error ? err.message : 'Failed to load PDF preview');
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        } else if (objectUrl) {
          URL.revokeObjectURL(objectUrl);
        }
      }
    };

    loadPdfBlob();

    return () => {
      cancelled = true;
      setBlobUrl((current) => {
        if (current) {
          URL.revokeObjectURL(current);
        }
        return null;
      });
    };
  }, [pdfUrl]);

  const handleDownload = () => {
    if (!blobUrl) {
      return;
    }

    const link = document.createElement('a');
    link.href = blobUrl;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!paper || !pdfUrl) {
    return (
      <div className="flex items-center justify-center h-[600px] rounded-2xl border border-gray-200 bg-white text-slate-500">
        Upload a paper to preview its PDF.
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[600px] bg-gray-900 rounded-2xl overflow-hidden border border-gray-200 shadow-sm">
      {/* Toolbar */}
      <div className="h-14 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4 text-gray-300">
        <div className="flex items-center gap-4 text-sm">
          <FileText className="w-5 h-5 text-gray-400" />
          <span className="truncate max-w-[260px]">{fileName}</span>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => changeZoom(-10)}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
            <ZoomOut className="w-4 h-4" />
          </button>
          <span className="text-sm w-12 text-center">{zoom}%</span>
          <button
            type="button"
            onClick={() => changeZoom(10)}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors">
            <ZoomIn className="w-4 h-4" />
          </button>
          <div className="w-px h-4 bg-gray-700 mx-2" />
          <button
            type="button"
            onClick={handleDownload}
            disabled={!blobUrl || isLoading}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            title="Download PDF">
            <Download className="w-4 h-4" />
          </button>
          <a
            href={viewerUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors"
            title="Open PDF in new tab">
            <Maximize className="w-4 h-4" />
          </a>
        </div>
      </div>

      <div className="flex-1 bg-slate-950">
        {isLoading ?
        <div className="w-full h-full flex items-center justify-center text-slate-300">
            Loading PDF preview...
          </div> :
        error ?
        <div className="w-full h-full flex items-center justify-center text-red-300 px-6 text-center">
            {error}
          </div> :
        viewerUrl ?
        <iframe
          key={viewerUrl}
          title="Paper PDF Preview"
          src={viewerUrl}
          className="w-full h-full border-0 bg-white"
        /> :
        <div className="w-full h-full flex items-center justify-center text-slate-300">
            Preparing preview...
          </div>
        }
      </div>
    </div>);

}
