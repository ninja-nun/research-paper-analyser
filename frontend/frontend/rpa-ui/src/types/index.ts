export type PaperStatus =
'Parsed' |
'Summarized' |
'Embedded' |
'Processing' |
'Failed';

export interface Paper {
  id: string;
  title: string;
  authors: string[];
  year: number;
  status: PaperStatus;
  doi?: string;
  journal?: string;
  affiliations?: string[];
  uploadDate: string;
}

export interface PaperSummary {
  brief: string;
  sections: {
    abstract: string;
    introduction: string;
    methodology: string;
    results: string;
    discussion: string;
    conclusion: string;
  };
}

export interface Keyword {
  term: string;
  score: number;
  method: string;
}

export interface KeywordsData {
  keywords: Keyword[];
  concepts: string[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  timestamp: number;
}