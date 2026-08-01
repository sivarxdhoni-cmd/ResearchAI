import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { ShieldAlert, Award, FileText, Zap, Loader2, Layers, Copy, CheckCircle, X } from "lucide-react";

interface GapItem {
  id: number;
  topic_id: number;
  topic_name: string;
  description: string;
  missing_methodology: string;
  missing_dataset: string;
  missing_hardware: string;
  missing_model: string;
  innovation_score: number;
  detected_at: string;
}

interface IdeaItem {
  id: number;
  gap_id?: number;
  title: string;
  description: string;
  type: string; // IEEE, SIH, Patent, Startup
  target_audience: string;
  novelty_score: number;
  roadmap_steps: Array<{ phase: string; details: string }>;
}

export const GapExplorer: React.FC = () => {
  const [gaps, setGaps] = useState<GapItem[]>([]);
  const [ideas, setIdeas] = useState<IdeaItem[]>([]);
  const [topics, setTopics] = useState<Array<{ id: number; name: string }>>([]);
  const [selectedTopicId, setSelectedTopicId] = useState<string>("");
  
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [scanMsg, setScanMsg] = useState("");
  
  // Lit review state
  const [litLoading, setLitLoading] = useState(false);
  const [litReview, setLitReview] = useState<{ title: string; markdown: string } | null>(null);
  const [copied, setCopied] = useState(false);

  const loadData = async () => {
    setLoading(true);
    try {
      const gapData = await api.getGaps();
      const ideaData = await api.getIdeas();
      setGaps(gapData);
      setIdeas(ideaData);
      
      // We can query papers to compile topics if stats doesn't map IDs.
      const papers = await api.getPapers();
      const mappedTopics: Record<string, number> = {};
      const topicIdList: Array<{ id: number; name: string }> = [];
      
      papers.forEach((p: any) => {
        (p.topics || []).forEach((t: any) => {
          if (!mappedTopics[t.name]) {
            mappedTopics[t.name] = t.id;
            topicIdList.push({ id: t.id, name: t.name });
          }
        });
      });
      setTopics(topicIdList);
      if (topicIdList.length > 0 && !selectedTopicId) {
        setSelectedTopicId(String(topicIdList[0].id));
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleScan = async () => {
    if (!selectedTopicId) return;
    setScanning(true);
    setScanMsg("Comparing methodologies & extracting limitations in background...");
    try {
      await api.scanGaps(Number(selectedTopicId));
      setScanMsg("Scan complete! Updating ideas...");
      setTimeout(() => {
        loadData();
        setScanMsg("");
        setScanning(false);
      }, 3000);
    } catch (err: any) {
      setScanMsg(`Scan failed: ${err.message}`);
      setScanning(false);
    }
  };

  const handleGenerateLitReview = async (topicName: string) => {
    setLitLoading(true);
    setLitReview(null);
    try {
      const data = await api.generateLiteratureReview(topicName);
      setLitReview({
        title: data.title,
        markdown: data.markdown_content
      });
    } catch (err: any) {
      alert(`Failed to compile literature review: ${err.message}`);
    } finally {
      setLitLoading(false);
    }
  };

  const handleCopyReview = () => {
    if (!litReview) return;
    navigator.clipboard.writeText(litReview.markdown);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8">
      {/* Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Research Gap & Idea Engine</h1>
          <p className="text-xs opacity-60 mt-1">Cross-correlate papers, identify blind spots, and draft novel academic research proposals.</p>
        </div>

        {/* Scan Actions */}
        {topics.length > 0 && (
          <div className="flex items-center gap-3 bg-white/40 dark:bg-panel-dark/40 backdrop-blur p-2.5 rounded-xl border border-slate-200/50 dark:border-slate-800/50">
            <select
              value={selectedTopicId}
              onChange={(e) => setSelectedTopicId(e.target.value)}
              className="px-3 py-1.5 text-xs bg-slate-100 dark:bg-[#0b101c] outline-none border border-slate-200/50 dark:border-slate-800/80 rounded-lg cursor-pointer font-semibold"
            >
              {topics.map((t, idx) => (
                <option key={idx} value={t.id}>{t.name}</option>
              ))}
            </select>
            <button
              onClick={handleScan}
              disabled={scanning}
              className="px-3.5 py-1.5 bg-accent-primary hover:bg-accent-dark disabled:bg-slate-700 text-white text-xs font-bold rounded-lg shadow transition-all flex items-center gap-1.5 cursor-pointer"
            >
              {scanning ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Zap className="w-3.5 h-3.5" />}
              Scan Gaps
            </button>
          </div>
        )}
      </div>

      {scanMsg && (
        <div className="bg-indigo-500/10 border border-indigo-500/20 text-indigo-500 text-xs px-4 py-2.5 rounded-xl text-center font-semibold">
          {scanMsg}
        </div>
      )}

      {loading ? (
        <div className="flex-1 flex flex-col items-center justify-center py-20 space-y-4">
          <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
          <p className="text-sm opacity-60">Scanning matrix intersections...</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Gaps List (Left Column) */}
          <div className="lg:col-span-7 space-y-6">
            <h3 className="text-md font-bold flex items-center gap-2 border-b border-slate-200/50 dark:border-slate-800/50 pb-3">
              <ShieldAlert className="w-5 h-5 text-amber-500" />
              Detected Research Blindspots
            </h3>

            {gaps.length > 0 ? (
              gaps.map((gap, i) => (
                <div key={i} className="glass-panel p-5 rounded-2xl space-y-4 border border-slate-200/30 dark:border-slate-800/30">
                  <div className="flex justify-between items-start">
                    <span className="px-2.5 py-1 bg-violet-500/10 text-violet-500 rounded-lg text-[9px] font-bold">
                      Topic: {gap.topic_name}
                    </span>
                    <div className="flex items-center gap-1">
                      <span className="text-[9px] uppercase font-bold text-slate-400">Innovation Score:</span>
                      <span className="text-xs font-black text-amber-500">{gap.innovation_score}%</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-700 dark:text-slate-200 font-medium leading-relaxed">
                    {gap.description}
                  </p>

                  <div className="grid grid-cols-2 gap-4 text-[10px] pt-3 border-t border-slate-200/30 dark:border-slate-800/30">
                    <div>
                      <span className="font-bold text-slate-400">Missing Method/Model:</span>
                      <p className="text-slate-600 dark:text-slate-300 mt-0.5 leading-snug">{gap.missing_methodology || "N/A"}</p>
                    </div>
                    <div>
                      <span className="font-bold text-slate-400">Missing Benchmark:</span>
                      <p className="text-slate-600 dark:text-slate-300 mt-0.5 leading-snug">{gap.missing_dataset || "N/A"}</p>
                    </div>
                    <div>
                      <span className="font-bold text-slate-400">Untested hardware:</span>
                      <p className="text-slate-600 dark:text-slate-300 mt-0.5 leading-snug">{gap.missing_hardware || "N/A"}</p>
                    </div>
                    <div className="flex flex-col justify-between">
                      <div>
                        <span className="font-bold text-slate-400">Suggested Model:</span>
                        <p className="text-slate-600 dark:text-slate-300 mt-0.5 leading-snug">{gap.missing_model || "N/A"}</p>
                      </div>
                      <button
                        onClick={() => handleGenerateLitReview(gap.topic_name)}
                        className="text-[9px] font-bold text-indigo-500 hover:underline mt-2 self-start flex items-center gap-1 cursor-pointer"
                      >
                        <FileText className="w-3.5 h-3.5" /> Compile Literature Review
                      </button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="glass-panel p-10 rounded-2xl text-center opacity-60 text-xs">
                No research gaps identified. Add articles and trigger scan.
              </div>
            )}
          </div>

          {/* Ideas Timeline (Right Column) */}
          <div className="lg:col-span-5 space-y-6">
            <h3 className="text-md font-bold flex items-center gap-2 border-b border-slate-200/50 dark:border-slate-800/50 pb-3">
              <Award className="w-5 h-5 text-emerald-500" />
              Novel Research Proposals
            </h3>

            {ideas.length > 0 ? (
              ideas.map((idea, i) => (
                <div key={i} className="glass-panel p-5 rounded-2xl space-y-4 border border-emerald-500/10 hover:border-emerald-500/30 transition-all duration-300">
                  <div className="flex justify-between items-start">
                    <span className={`px-2 py-0.5 text-[9px] font-bold rounded-lg ${
                      idea.type === "IEEE" ? "bg-indigo-500/10 text-indigo-500" : "bg-emerald-500/10 text-emerald-500"
                    }`}>
                      {idea.type} Idea
                    </span>
                    <div className="flex items-center gap-1">
                      <span className="text-[9px] uppercase font-bold text-slate-400">Novelty:</span>
                      <span className="text-xs font-black text-emerald-500">{idea.novelty_score}%</span>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-xs font-extrabold text-slate-700 dark:text-slate-100 leading-snug">
                      {idea.title}
                    </h4>
                    <p className="text-[11px] text-slate-500 dark:text-slate-300 mt-2 leading-relaxed">
                      {idea.description}
                    </p>
                  </div>

                  {idea.roadmap_steps && idea.roadmap_steps.length > 0 && (
                    <div className="pt-3 border-t border-slate-200/30 dark:border-slate-800/30 space-y-2">
                      <span className="text-[9px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1">
                        <Layers className="w-3.5 h-3.5" /> Project Roadmap
                      </span>
                      <div className="pl-2 border-l border-indigo-500/30 space-y-2.5">
                        {idea.roadmap_steps.map((step, idx) => (
                          <div key={idx} className="relative pl-3 text-[10px]">
                            <span className="absolute -left-[12.5px] top-1 w-2.5 h-2.5 rounded-full bg-indigo-500 border border-white dark:border-panel-dark"></span>
                            <span className="font-bold text-slate-600 dark:text-slate-200">{step.phase}</span>
                            <p className="text-slate-400 mt-0.5 leading-snug">{step.details}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="glass-panel p-10 rounded-2xl text-center opacity-60 text-xs">
                No novel proposals drafted. Trigger a gap scan to generate ideas.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Lit Review Modal/Slide-out */}
      {litLoading && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm flex items-center justify-center">
          <div className="glass-panel p-6 rounded-2xl max-w-sm text-center space-y-4">
            <Loader2 className="w-10 h-10 text-indigo-500 animate-spin mx-auto" />
            <div>
              <h4 className="text-xs font-bold">Compiling Literature Review</h4>
              <p className="text-[10px] text-slate-400 mt-1">Reading local corpus passages and synthesising markdown tables...</p>
            </div>
          </div>
        </div>
      )}

      {litReview && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel rounded-3xl w-full max-w-3xl max-h-[85vh] flex flex-col overflow-hidden shadow-2xl animate-float">
            {/* Header */}
            <div className="p-5 border-b border-slate-200/50 dark:border-slate-800/50 flex justify-between items-center bg-white/40 dark:bg-panel-dark/40 backdrop-blur">
              <h3 className="text-sm font-extrabold text-indigo-500">{litReview.title}</h3>
              <div className="flex items-center gap-3">
                <button
                  onClick={handleCopyReview}
                  className="px-3.5 py-1.5 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 border border-slate-200/50 dark:border-slate-800/80 text-xs font-semibold rounded-lg flex items-center gap-1.5 cursor-pointer transition-colors"
                >
                  {copied ? <CheckCircle className="w-4 h-4 text-green-500" /> : <Copy className="w-4 h-4" />}
                  {copied ? "Copied!" : "Copy Markdown"}
                </button>
                <button
                  onClick={() => setLitReview(null)}
                  className="p-1.5 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Content body */}
            <div className="flex-1 overflow-y-auto p-8 text-xs leading-relaxed font-mono bg-slate-50/50 dark:bg-black/30 scrollbar">
              <pre className="whitespace-pre-wrap font-sans text-slate-600 dark:text-slate-300">
                {litReview.markdown}
              </pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
