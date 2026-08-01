import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { Layers, FileText, ChevronRight, AlertCircle, Loader2 } from "lucide-react";

interface PaperItem {
  id: number;
  title: string;
  authors_text: string;
  publication_year: number;
}

interface ComparisonItem {
  id: number;
  title: string;
  authors: string;
  year: number;
  methodology: string;
  datasets: string[];
  algorithms: string[];
  metrics: string[];
  limitations: string;
  future_work: string;
}

export const Compare: React.FC = () => {
  const [papers, setPapers] = useState<PaperItem[]>([]);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [comparisonData, setComparisonData] = useState<ComparisonItem[]>([]);
  
  const [loadingList, setLoadingList] = useState(true);
  const [loadingMatrix, setLoadingMatrix] = useState(false);
  const [error, setError] = useState("");

  const loadPapers = async () => {
    try {
      const data = await api.getPapers();
      // Only keep completed papers
      setPapers(data.filter((p: any) => p.status === "completed"));
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    loadPapers();
  }, []);

  const handleCheckboxChange = (id: number) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const handleCompare = async () => {
    if (selectedIds.length < 1) {
      setError("Please select at least 1 paper to analyze.");
      return;
    }
    setError("");
    setLoadingMatrix(true);
    try {
      const data = await api.comparePapers(selectedIds);
      setComparisonData(data.comparison_data);
    } catch (err: any) {
      setError(err.message || "Failed to compile comparison matrix.");
    } finally {
      setLoadingMatrix(false);
    }
  };

  return (
    <div className="space-y-8 animate-float">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight">Methodological Compare Engine</h1>
        <p className="text-xs opacity-60 mt-1">Run structural side-by-side overlays of paper models, datasets, metrics, and parameters.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Selection Sidebar */}
        <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between h-[450px]">
          <div className="space-y-4">
            <h3 className="text-sm font-bold flex items-center gap-2 border-b border-slate-200/50 dark:border-slate-800/50 pb-3">
              <Layers className="w-5 h-5 text-indigo-500" />
              Select Articles
            </h3>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-500 text-[10px] px-3.5 py-2 rounded-xl flex items-center gap-1.5 font-semibold">
                <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="space-y-2.5 max-h-[250px] overflow-y-auto pr-1">
              {loadingList ? (
                <div className="text-center py-10 opacity-60 text-xs">Loading corpus...</div>
              ) : papers.length > 0 ? (
                papers.map((p, i) => (
                  <label
                    key={i}
                    className={`flex gap-2.5 items-start p-2.5 rounded-xl border cursor-pointer select-none transition-all duration-300 ${
                      selectedIds.includes(p.id)
                        ? "bg-indigo-500/10 border-indigo-500/50"
                        : "bg-slate-50/20 dark:bg-black/10 border-slate-200/20 dark:border-slate-800/40 hover:border-slate-400"
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={selectedIds.includes(p.id)}
                      onChange={() => handleCheckboxChange(p.id)}
                      className="mt-0.5 accent-indigo-500"
                    />
                    <div className="text-[10px] leading-tight space-y-0.5">
                      <span className="font-bold text-slate-700 dark:text-slate-200 line-clamp-2">{p.title}</span>
                      <span className="text-[9px] text-slate-400 block font-medium">({p.publication_year || "2026"})</span>
                    </div>
                  </label>
                ))
              ) : (
                <div className="text-center py-10 opacity-60 text-xs">No indexed papers found. Upload completed papers first.</div>
              )}
            </div>
          </div>

          <button
            onClick={handleCompare}
            disabled={loadingMatrix || selectedIds.length === 0}
            className={`w-full py-2.5 text-xs font-bold rounded-xl transition-all shadow flex items-center justify-center gap-1.5 ${
              selectedIds.length > 0
                ? "bg-accent-primary hover:bg-accent-dark text-white active:scale-98 cursor-pointer"
                : "bg-slate-200 dark:bg-slate-800 text-slate-400 cursor-not-allowed"
            }`}
          >
            {loadingMatrix ? (
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <>
                Compare Selected ({selectedIds.length})
                <ChevronRight className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

        {/* Matrix Result Board */}
        <div className="lg:col-span-3 glass-panel p-6 rounded-2xl overflow-hidden flex flex-col min-h-[450px]">
          <h3 className="text-sm font-bold mb-4 border-b border-slate-200/50 dark:border-slate-800/50 pb-3 flex items-center gap-2">
            <FileText className="w-5 h-5 text-indigo-500" />
            Comparative Parameters Grid
          </h3>

          {loadingMatrix ? (
            <div className="flex-1 flex flex-col items-center justify-center space-y-3">
              <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
              <p className="text-xs opacity-60">Re-indexing layouts and mapping matrix overlap...</p>
            </div>
          ) : comparisonData.length > 0 ? (
            <div className="flex-1 overflow-x-auto overflow-y-auto max-h-[350px] scrollbar border border-slate-200/20 dark:border-slate-800/40 rounded-xl">
              <table className="w-full text-left text-[11px] border-collapse min-w-[700px]">
                <thead>
                  <tr className="bg-slate-100 dark:bg-panel-dark text-slate-500 dark:text-slate-400 font-bold border-b border-slate-200/40 dark:border-slate-800/50">
                    <th className="p-3 w-48 border-r border-slate-200/30 dark:border-slate-800/30">Attribute</th>
                    {comparisonData.map((d, idx) => (
                      <th key={idx} className="p-3 border-r border-slate-200/30 dark:border-slate-800/30 font-bold text-slate-700 dark:text-slate-100 max-w-[200px] truncate">
                        {d.title}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200/30 dark:divide-slate-800/40 font-medium">
                  {/* Authors Row */}
                  <tr>
                    <td className="p-3 font-bold bg-slate-50/50 dark:bg-[#121824]/30 border-r border-slate-200/30 dark:border-slate-800/30">Authors & Year</td>
                    {comparisonData.map((d, idx) => (
                      <td key={idx} className="p-3 border-r border-slate-200/30 dark:border-slate-800/30 text-slate-400 font-medium">
                        {d.authors} ({d.year})
                      </td>
                    ))}
                  </tr>
                  {/* Methodology Row */}
                  <tr>
                    <td className="p-3 font-bold bg-slate-50/50 dark:bg-[#121824]/30 border-r border-slate-200/30 dark:border-slate-800/30">Proposed Method</td>
                    {comparisonData.map((d, idx) => (
                      <td key={idx} className="p-3 border-r border-slate-200/30 dark:border-slate-800/30 text-slate-600 dark:text-slate-300 leading-relaxed font-medium">
                        {d.methodology}
                      </td>
                    ))}
                  </tr>
                  {/* Datasets Row */}
                  <tr>
                    <td className="p-3 font-bold bg-slate-50/50 dark:bg-[#121824]/30 border-r border-slate-200/30 dark:border-slate-800/30">Datasets Evaluated</td>
                    {comparisonData.map((d, idx) => (
                      <td key={idx} className="p-3 border-r border-slate-200/30 dark:border-slate-800/30">
                        <div className="flex flex-wrap gap-1">
                          {d.datasets.map((x, i) => (
                            <span key={i} className="px-2 py-0.5 bg-cyan-500/10 text-cyan-500 rounded text-[9px] font-bold">
                              {x}
                            </span>
                          ))}
                        </div>
                      </td>
                    ))}
                  </tr>
                  {/* Algorithms Row */}
                  <tr>
                    <td className="p-3 font-bold bg-slate-50/50 dark:bg-[#121824]/30 border-r border-slate-200/30 dark:border-slate-800/30">Algorithms/Models</td>
                    {comparisonData.map((d, idx) => (
                      <td key={idx} className="p-3 border-r border-slate-200/30 dark:border-slate-800/30">
                        <div className="flex flex-wrap gap-1">
                          {d.algorithms.map((x, i) => (
                            <span key={i} className="px-2 py-0.5 bg-emerald-500/10 text-emerald-500 rounded text-[9px] font-bold">
                              {x}
                            </span>
                          ))}
                        </div>
                      </td>
                    ))}
                  </tr>
                  {/* Accuracy Metrics Row */}
                  <tr>
                    <td className="p-3 font-bold bg-slate-50/50 dark:bg-[#121824]/30 border-r border-slate-200/30 dark:border-slate-800/30">Reported Metrics</td>
                    {comparisonData.map((d, idx) => (
                      <td key={idx} className="p-3 border-r border-slate-200/30 dark:border-slate-800/30 text-indigo-500 dark:text-indigo-400 font-bold">
                        {d.metrics.join(", ")}
                      </td>
                    ))}
                  </tr>
                  {/* Limitations Row */}
                  <tr>
                    <td className="p-3 font-bold bg-slate-50/50 dark:bg-[#121824]/30 border-r border-slate-200/30 dark:border-slate-800/30">Limitations Identified</td>
                    {comparisonData.map((d, idx) => (
                      <td key={idx} className="p-3 border-r border-slate-200/30 dark:border-slate-800/30 text-amber-500 leading-relaxed font-semibold">
                        {d.limitations}
                      </td>
                    ))}
                  </tr>
                  {/* Future Work Row */}
                  <tr>
                    <td className="p-3 font-bold bg-slate-50/50 dark:bg-[#121824]/30 border-r border-slate-200/30 dark:border-slate-800/30">Future Scope Work</td>
                    {comparisonData.map((d, idx) => (
                      <td key={idx} className="p-3 border-r border-slate-200/30 dark:border-slate-800/30 text-slate-500 leading-relaxed font-medium">
                        {d.future_work}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-center opacity-60 text-xs">
              Select papers on the left panel and compile to map side-by-side matrices.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
