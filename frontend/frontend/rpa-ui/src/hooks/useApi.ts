import { useState, useEffect, useCallback } from 'react';
import { api } from '../lib/api';
import { Paper, PaperSummary, KeywordsData } from '../types';

// Custom hooks simulating React Query behavior for standalone environment
export function usePapers() {
  const [data, setData] = useState<Paper[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    api.
    getPapers().
    then(setData).
    catch(setError).
    finally(() => setIsLoading(false));
  }, []);

  return { data, isLoading, error };
}

export function usePaper(id: string | undefined) {
  const [data, setData] = useState<Paper | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    api.
    getPaper(id).
    then(setData).
    catch(setError).
    finally(() => setIsLoading(false));
  }, [id]);

  return { data, isLoading, error };
}

export function useSummary(id: string | undefined) {
  const [data, setData] = useState<PaperSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    api.
    getSummary(id).
    then(setData).
    catch(console.error).
    finally(() => setIsLoading(false));
  }, [id]);

  return { data, isLoading };
}

export function useKeywords(id: string | undefined) {
  const [data, setData] = useState<KeywordsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setIsLoading(true);
    api.
    getKeywords(id).
    then(setData).
    catch(console.error).
    finally(() => setIsLoading(false));
  }, [id]);

  return { data, isLoading };
}

export function useUpload() {
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);

  const mutateAsync = async (file: File) => {
    setIsUploading(true);
    setProgress(10);

    // Simulate progress
    const interval = setInterval(() => {
      setProgress((p) => Math.min(p + 15, 90));
    }, 300);

    try {
      const res = await api.uploadPaper(file);
      setProgress(100);
      return res;
    } finally {
      clearInterval(interval);
      setTimeout(() => {
        setIsUploading(false);
        setProgress(0);
      }, 500);
    }
  };

  return { mutateAsync, isUploading, progress };
}