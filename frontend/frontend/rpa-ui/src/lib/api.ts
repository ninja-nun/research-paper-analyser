import { KeywordsData, Paper, PaperSummary } from '../types';

const BASE = '/api';

export const api = {
  uploadPaper: async (file: File): Promise<{ paper_id: string }> => {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(await res.text());
    const data = await res.json();
    return { paper_id: data.paper_id };
  },

  getPapers: async (): Promise<Paper[]> => {
    const res = await fetch(`${BASE}/paper`);
    if (!res.ok) return [];
    const data = await res.json();
    return [backendPaperToFrontend(data)];
  },

  getPaper: async (_id: string): Promise<Paper> => {
    const res = await fetch(`${BASE}/paper`);
    if (!res.ok) throw new Error('Paper not found');
    const data = await res.json();
    return backendPaperToFrontend(data);
  },

  getSummary: async (_id: string): Promise<PaperSummary> => {
    const res = await fetch(`${BASE}/summarize`, { method: 'POST' });
    if (!res.ok) throw new Error('Summarize failed');
    const data = await res.json();
    return {
      brief: data.summaries?.brief ?? '',
      sections: {
        abstract: data.summaries?.abstract ?? '',
        introduction: data.summaries?.introduction ?? '',
        methodology: data.summaries?.methodology ?? '',
        results: data.summaries?.results ?? '',
        discussion: data.summaries?.discussion ?? '',
        conclusion: data.summaries?.conclusion ?? '',
      },
    };
  },

  getKeywords: async (_id: string): Promise<KeywordsData> => {
    const res = await fetch(`${BASE}/keywords`);
    if (!res.ok) throw new Error('Keywords failed');
    const data = await res.json();
    return {
      keywords: (data.keyword_details ?? []).map((k: any) => ({
        term: k.term,
        score: k.score,
        method: k.method,
      })),
      concepts: data.concepts ?? [],
    };
  },

  chat: async (_id: string, message: string): Promise<{ answer: string; sources: string[] }> => {
    const res = await fetch(`${BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: message, top_k: 3 }),
    });
    if (!res.ok) throw new Error('Chat failed');
    const data = await res.json();
    return { answer: data.answer, sources: data.sources ?? [] };
  },

  deletePaper: async (_id: string): Promise<void> => {
    // Backend has no delete endpoint yet.
  },
};

function backendPaperToFrontend(data: any): Paper {
  return {
    id: data.paper_id,
    title: data.title ?? data.metadata?.title ?? 'Untitled',
    authors: data.authors ?? data.metadata?.authors ?? [],
    year: data.year ?? data.metadata?.year ?? 0,
    status: 'Embedded',
    doi: data.doi ?? data.metadata?.doi,
    journal: data.journal ?? data.metadata?.journal,
    uploadDate: new Date().toISOString(),
  };
}
