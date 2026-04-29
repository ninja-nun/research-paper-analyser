import React from 'react';
import { useNavigate } from 'react-router-dom';
import { DropZone } from '../components/upload/DropZone';
import { useUpload } from '../hooks/useApi';
export function UploadPage() {
  const navigate = useNavigate();
  const { mutateAsync, isUploading, progress, error } = useUpload();
  const handleUpload = async (file: File) => {
    try {
      const { paper_id } = await mutateAsync(file);
      // In a real app, we might wait for processing to finish or poll status
      // Here we redirect immediately to the detail page
      navigate(`/papers/${paper_id}`);
    } catch (error) {
      console.error('Upload failed:', error);
      // Error is handled in the hook/component
    }
  };
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 max-w-4xl mx-auto w-full min-h-[calc(100vh-4rem)]">
      <div className="text-center mb-10 space-y-4">
        <h1 className="text-4xl font-bold text-slate-900">
          Upload Research Paper
        </h1>
        <p className="text-lg text-slate-600 max-w-xl mx-auto">
          Drop your PDF here. Our AI will extract the text, analyze the
          methodology, and prepare it for interactive chat.
        </p>
      </div>

      <div className="w-full">
        <DropZone
          onUpload={handleUpload}
          isUploading={isUploading}
          progress={progress}
          uploadError={error} />
        
      </div>

      <div className="mt-12 grid grid-cols-3 gap-8 text-center max-w-2xl w-full text-sm text-slate-500">
        <div>
          <div className="font-semibold text-slate-900 mb-1">1. Upload</div>
          <p>Securely upload your PDF document</p>
        </div>
        <div>
          <div className="font-semibold text-slate-900 mb-1">2. Process</div>
          <p>AI extracts text and generates embeddings</p>
        </div>
        <div>
          <div className="font-semibold text-slate-900 mb-1">3. Analyze</div>
          <p>Get summaries, keywords, and chat</p>
        </div>
      </div>
    </div>);

}
