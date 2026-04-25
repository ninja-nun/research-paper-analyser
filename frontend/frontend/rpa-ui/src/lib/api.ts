import { Paper, PaperSummary, KeywordsData } from '../types';

// Mock Data
const MOCK_PAPERS: Paper[] = [
{
  id: 'p1',
  title: 'Attention Is All You Need',
  authors: [
  'Ashish Vaswani',
  'Noam Shazeer',
  'Niki Parmar',
  'Jakob Uszkoreit'],

  year: 2017,
  status: 'Embedded',
  doi: '10.48550/arXiv.1706.03762',
  journal: 'NeurIPS',
  affiliations: ['Google Brain', 'Google Research'],
  uploadDate: '2023-10-01T12:00:00Z'
},
{
  id: 'p2',
  title:
  'BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding',
  authors: [
  'Jacob Devlin',
  'Ming-Wei Chang',
  'Kenton Lee',
  'Kristina Toutanova'],

  year: 2018,
  status: 'Summarized',
  doi: '10.48550/arXiv.1810.04805',
  journal: 'NAACL',
  affiliations: ['Google AI Language'],
  uploadDate: '2023-10-05T09:30:00Z'
},
{
  id: 'p3',
  title: 'Language Models are Few-Shot Learners',
  authors: ['Tom B. Brown', 'Benjamin Mann', 'Nick Ryder', 'Melanie Subbiah'],
  year: 2020,
  status: 'Parsed',
  uploadDate: '2023-10-10T14:15:00Z'
}];


const MOCK_SUMMARY: PaperSummary = {
  brief:
  'This paper proposes the Transformer, a novel network architecture based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. It achieves state-of-the-art results on translation tasks while being more parallelizable and requiring significantly less time to train.',
  sections: {
    abstract:
    'The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.',
    introduction:
    'Recurrent neural networks, long short-term memory and gated recurrent neural networks in particular, have been firmly established as state of the art approaches in sequence modeling and transduction problems such as language modeling and machine translation.',
    methodology:
    'Most competitive neural sequence transduction models have an encoder-decoder structure. Here, the encoder maps an input sequence of symbol representations to a sequence of continuous representations. The Transformer follows this overall architecture using stacked self-attention and point-wise, fully connected layers.',
    results:
    'On the WMT 2014 English-to-German translation task, the big transformer model achieves a BLEU score of 28.4, improving over the existing best results, including ensembles, by over 2.0 BLEU.',
    discussion:
    'The Transformer is the first sequence transduction model based entirely on attention, replacing the recurrent layers most commonly used in encoder-decoder architectures with multi-headed self-attention.',
    conclusion:
    'In this work, we presented the Transformer, the first sequence transduction model based entirely on attention. For translation tasks, the Transformer can be trained significantly faster than architectures based on recurrent or convolutional layers.'
  }
};

const MOCK_KEYWORDS: KeywordsData = {
  keywords: [
  { term: 'Attention Mechanism', score: 0.95, method: 'TF-IDF' },
  { term: 'Transformer', score: 0.92, method: 'TextRank' },
  { term: 'Machine Translation', score: 0.88, method: 'KeyBERT' },
  { term: 'Sequence Transduction', score: 0.85, method: 'TF-IDF' },
  { term: 'Self-Attention', score: 0.82, method: 'TextRank' },
  { term: 'Neural Networks', score: 0.75, method: 'KeyBERT' },
  { term: 'BLEU Score', score: 0.7, method: 'TF-IDF' }],

  concepts: [
  'Deep Learning',
  'Natural Language Processing',
  'Parallel Computing']

};

// Helper to simulate network delay
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const api = {
  getPapers: async (): Promise<Paper[]> => {
    await delay(800);
    return MOCK_PAPERS;
  },
  getPaper: async (id: string): Promise<Paper> => {
    await delay(600);
    const paper = MOCK_PAPERS.find((p) => p.id === id);
    if (!paper) throw new Error('Paper not found');
    return paper;
  },
  uploadPaper: async (file: File): Promise<{paper_id: string;}> => {
    await delay(2000);
    return { paper_id: `p${Math.floor(Math.random() * 1000)}` };
  },
  deletePaper: async (id: string): Promise<void> => {
    await delay(500);
  },
  getSummary: async (id: string): Promise<PaperSummary> => {
    await delay(1200);
    return MOCK_SUMMARY;
  },
  getKeywords: async (id: string): Promise<KeywordsData> => {
    await delay(1000);
    return MOCK_KEYWORDS;
  },
  chat: async (
  id: string,
  message: string)
  : Promise<{answer: string;sources: string[];}> => {
    await delay(1500);
    return {
      answer: `Based on the paper, regarding "${message}", the authors state that the Transformer architecture allows for significantly more parallelization compared to RNNs. This is achieved by relying entirely on self-attention mechanisms rather than sequential processing.`,
      sources: [
      'Section 3.2: Attention mechanisms have become an integral part of compelling sequence modeling and transduction models in various tasks, allowing modeling of dependencies without regard to their distance in the input or output sequences.',
      'Section 4: To the best of our knowledge, however, the Transformer is the first transduction model relying entirely on self-attention to compute representations of its input and output without using sequence-aligned RNNs or convolution.']

    };
  }
};