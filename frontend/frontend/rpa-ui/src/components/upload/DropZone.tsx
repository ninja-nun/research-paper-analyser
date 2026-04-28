import React, { useCallback, useState } from 'react';
import { UploadCloud, File, X, AlertCircle } from 'lucide-react';
import { cn } from '../../lib/utils';
import { Button } from '../ui/Button';
interface DropZoneProps {
  onUpload: (file: File) => void;
  isUploading: boolean;
  progress: number;
}
export function DropZone({ onUpload, isUploading, progress }: DropZoneProps) {
  const [isDragActive, setIsDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  }, []);
  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  }, []);
  const validateFile = (file: File) => {
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are supported.');
      return false;
    }
    if (file.size > 50 * 1024 * 1024) {
      setError('File size exceeds 50MB limit.');
      return false;
    }
    setError(null);
    return true;
  };
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
      }
    }
  }, []);
  const handleFileInput = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (e.target.files && e.target.files.length > 0) {
        const file = e.target.files[0];
        if (validateFile(file)) {
          setSelectedFile(file);
        }
      }
    },
    []
  );
  const handleUploadClick = () => {
    if (selectedFile) {
      onUpload(selectedFile);
    }
  };
  return (
    <div className="w-full max-w-2xl mx-auto">
      {!selectedFile ?
      <div
        onDragEnter={handleDragEnter}
        onDragOver={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'relative flex flex-col items-center justify-center w-full h-80 rounded-3xl border-2 border-dashed transition-all duration-200 bg-white',
          isDragActive ?
          'border-blue-500 bg-blue-50/50 scale-[1.02]' :
          'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
        )}>
        
          <input
          type="file"
          accept=".pdf"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={isUploading} />
        

          <div className="flex flex-col items-center justify-center pt-5 pb-6 px-4 text-center">
            <div
            className={cn(
              'p-4 rounded-full mb-4 transition-colors',
              isDragActive ?
              'bg-blue-100 text-blue-600' :
              'bg-gray-100 text-gray-500'
            )}>
            
              <UploadCloud className="w-10 h-10" />
            </div>
            <p className="mb-2 text-xl font-semibold text-slate-700">
              Click to upload or drag and drop
            </p>
            <p className="text-sm text-gray-500 mb-6">
              PDF documents only (Max 50MB)
            </p>
            <Button variant="secondary" className="pointer-events-none">
              Select File
            </Button>
          </div>
        </div> :

      <div className="bg-white rounded-3xl border border-gray-200 p-8 shadow-sm">
          <div className="flex items-start gap-4 mb-8">
            <div className="p-3 bg-blue-50 rounded-2xl text-blue-600 shrink-0">
              <File className="w-8 h-8" />
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="text-lg font-semibold text-slate-900 truncate">
                {selectedFile.name}
              </h4>
              <p className="text-sm text-gray-500">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
            {!isUploading &&
          <button
            onClick={() => setSelectedFile(null)}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors">
            
                <X className="w-5 h-5" />
              </button>
          }
          </div>

          {isUploading ?
        <div className="space-y-3">
              <div className="flex justify-between text-sm font-medium">
                <span className="text-blue-600">
                  {progress < 30 ?
              'Uploading...' :
              progress < 70 ?
              'Extracting text...' :
              'Running analysis...'}
                </span>
                <span className="text-slate-700">{progress}%</span>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2.5 overflow-hidden">
                <div
              className="bg-blue-600 h-2.5 rounded-full transition-all duration-300 ease-out"
              style={{
                width: `${progress}%`
              }}>
            </div>
              </div>
            </div> :

        <div className="flex justify-end gap-3">
              <Button variant="ghost" onClick={() => setSelectedFile(null)}>
                Cancel
              </Button>
              <Button onClick={handleUploadClick} className="px-8">
                Analyze Paper
              </Button>
            </div>
        }
        </div>
      }

      {error &&
      <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-xl flex items-center gap-2 text-sm">
          <AlertCircle className="w-4 h-4" />
          {error}
        </div>
      }
    </div>);

}