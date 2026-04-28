import { create } from 'zustand';
import { ChatMessage } from '../types';

interface PaperState {
  activePaperId: string | null;
  chatHistory: Record<string, ChatMessage[]>;
  setActivePaperId: (id: string | null) => void;
  addChatMessage: (paperId: string, message: ChatMessage) => void;
  clearChatHistory: (paperId: string) => void;
}

export const usePaperStore = create<PaperState>((set) => ({
  activePaperId: null,
  chatHistory: {},
  setActivePaperId: (id) => set({ activePaperId: id }),
  addChatMessage: (paperId, message) =>
  set((state) => ({
    chatHistory: {
      ...state.chatHistory,
      [paperId]: [...(state.chatHistory[paperId] || []), message]
    }
  })),
  clearChatHistory: (paperId) =>
  set((state) => {
    const newHistory = { ...state.chatHistory };
    delete newHistory[paperId];
    return { chatHistory: newHistory };
  })
}));