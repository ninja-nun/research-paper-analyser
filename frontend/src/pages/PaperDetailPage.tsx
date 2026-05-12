import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import { usePaper, useSummary, useKeywords } from '../hooks/useApi';
import { usePaperStore } from '../store/paperStore';
import { MetadataPanel } from '../components/paper/MetadataPanel';
import { SectionTabs, TabType } from '../components/paper/SectionTabs';
import { SummaryView } from '../components/paper/SummaryView';
import { KeywordCloud } from '../components/keywords/KeywordCloud';
import { KeywordChart } from '../components/keywords/KeywordChart';
import { ChatPanel } from '../components/chat/ChatPanel';
import { PdfPreview } from '../components/paper/PdfPreview';
import { Button } from '../components/ui/Button';
export function PaperDetailPage() {
  const { paperId } = useParams<{
    paperId: string;
  }>();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<TabType>('summary');
  const setActivePaperId = usePaperStore((state) => state.setActivePaperId);
  useEffect(() => {
    if (paperId) {
      setActivePaperId(paperId);
    }
    return () => setActivePaperId(null);
  }, [paperId, setActivePaperId]);
  const { data: paper, isLoading: isPaperLoading } = usePaper(paperId);
  const { data: summary, isLoading: isSummaryLoading } = useSummary(paperId);
  const { data: keywords, isLoading: isKeywordsLoading } = useKeywords(paperId);
  if (!paperId) return null;
  return (
    <div className="p-4 md:p-6 lg:p-8 max-w-[1600px] mx-auto w-full">
      <div className="mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/papers')}
          className="gap-2 -ml-2 text-slate-500">
          
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Button>
      </div>

      <div className="flex flex-col lg:flex-row gap-8 items-start">
        {/* Left Panel - Sticky Metadata */}
        <div className="w-full lg:w-[320px] xl:w-[380px] shrink-0">
          <MetadataPanel
            paper={paper || undefined}
            isLoading={isPaperLoading} />
          
        </div>

        {/* Right Panel - Main Content */}
        <div className="flex-1 w-full min-w-0">
          <SectionTabs activeTab={activeTab} onChange={setActiveTab} />

          <div className="min-h-[600px]">
            {activeTab === 'summary' &&
            <SummaryView
              summary={summary || undefined}
              isLoading={isSummaryLoading} />

            }

            {activeTab === 'keywords' &&
            <div className="grid md:grid-cols-2 gap-6">
                <KeywordCloud
                keywords={keywords?.keywords}
                concepts={keywords?.concepts}
                isLoading={isKeywordsLoading} />
              
                <KeywordChart
                keywords={keywords?.keywords}
                isLoading={isKeywordsLoading} />
              
              </div>
            }

            {activeTab === 'chat' && <ChatPanel paperId={paperId} />}

            {activeTab === 'preview' && <PdfPreview paper={paper || undefined} />}
          </div>
        </div>
      </div>
    </div>);

}
