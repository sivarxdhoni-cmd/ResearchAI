import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { UploadCloud, FileText, CheckCircle2, Trash2, X, Globe, Plus, AlertCircle, Calendar } from "lucide-react";

interface PaperItem {
  id: number;
  title: string;
  authors_text: string;
  publication_year: number;
  conference_journal: string;
  upload_date: string;
  status: string;
}

export const Upload: React.FC = () => {
  const [papers, setPapers] = useState<PaperItem[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  
  // Optional metadata inputs
  const [showMeta, setShowMeta] = useState(false);
  const [year, setYear] = useState("");
  const [conf, setConf] = useState("");
  const [doi, setDoi] = useState("");
  const [arxiv, setArxiv] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const loadPapers = async () => {
    try {
      const data = await api.getPapers();
      setPapers(data);
    } catch (err: any) {
      console.error(err);
    }
  };

  useEffect(() => {
    loadPapers();
    // Poll paper statuses every 4 seconds to update when processing finishes
    const interval = setInterval(loadPapers, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.type === "application/pdf") {
        setSelectedFile(file);
      } else {
        setError("Only PDF files are supported.");
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUploadSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      const metadata = {
        publication_year: year ? parseInt(year) : undefined,
        conference_journal: conf || undefined,
        doi: doi || undefined,
        arxiv_url: arxiv || undefined
      };
      
      await api.uploadPaper(selectedFile, metadata);
      setSuccess("PDF uploaded successfully. Analyzing section layouts in background...");
      setSelectedFile(null);
      setYear("");
      setConf("");
      setDoi("");
      setArxiv("");
      setShowMeta(false);
      loadPapers();
    } catch (err: any) {
      setError(err.message || "Failed to process PDF upload.");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm("Are you sure you want to delete this paper and remove all its embedding vectors and graph relations?")) {
      return;
    }
    try {
      await api.deletePaper(id);
      loadPapers();
    } catch (err: any) {
      alert(err.message || "Failed to delete paper.");
    }
  };

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight">Paper Corpus Manager</h1>
        <p className="text-xs opacity-60 mt-1">Upload and process PDF papers to extract structures, embeddings, and graphs.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Form Panel */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col justify-between h-fit">
          <form onSubmit={handleUploadSubmit} className="space-y-5">
            <h3 className="text-md font-bold flex items-center gap-2 border-b border-slate-200/50 dark:border-slate-800/50 pb-3">
              <UploadCloud className="w-5 h-5 text-indigo-500" />
              Upload Scientific Article
            </h3>

            {error && (
              <div className="bg-red-500/10 border border-red-500/20 text-red-500 text-xs px-4 py-2.5 rounded-xl flex items-center gap-2">
                <AlertCircle className="w-4 h-4" />
                <span>{error}</span>
              </div>
            )}
            {success && (
              <div className="bg-green-500/10 border border-green-500/20 text-green-500 text-xs px-4 py-2.5 rounded-xl flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 animate-bounce" />
                <span>{success}</span>
              </div>
            )}

            {/* Drop Zone */}
            <div
              onDragEnter={handleDrag}
              onDragOver={handleDrag}
              onDragLeave={handleDrag}
              onDrop={handleDrop}
              className={`border-2 border-dashed rounded-2xl p-6 text-center transition-all duration-300 ${
                dragActive ? "border-indigo-500 bg-indigo-500/5" : "border-slate-300 dark:border-slate-800 bg-slate-50/20 dark:bg-black/10"
              }`}
            >
              <input
                type="file"
                id="file-upload"
                accept=".pdf"
                className="hidden"
                onChange={handleFileChange}
              />
              {selectedFile ? (
                <div className="space-y-3">
                  <FileText className="w-10 h-10 mx-auto text-indigo-500 animate-pulse" />
                  <div>
                    <p className="text-xs font-bold text-slate-700 dark:text-slate-200 truncate max-w-[200px] mx-auto">
                      {selectedFile.name}
                    </p>
                    <p className="text-[10px] text-slate-400 mt-1">
                      {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => setSelectedFile(null)}
                    className="p-1 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 rounded-full text-slate-400 hover:text-slate-200 transition-colors"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              ) : (
                <label htmlFor="file-upload" className="cursor-pointer space-y-3 block">
                  <UploadCloud className="w-12 h-12 mx-auto text-slate-400" />
                  <div>
                    <span className="text-xs font-bold text-indigo-500 hover:underline block">
                      Choose PDF file
                    </span>
                    <span className="text-[10px] text-slate-400 block mt-1">
                      or drag & drop here
                    </span>
                  </div>
                </label>
              )}
            </div>

            {/* Metadata Toggle */}
            <div className="border-t border-slate-200/50 dark:border-slate-800/50 pt-3">
              <button
                type="button"
                onClick={() => setShowMeta(!showMeta)}
                className="text-xs font-bold text-slate-400 hover:text-slate-200 flex items-center gap-1"
              >
                <Plus className={`w-3.5 h-3.5 transition-transform duration-300 ${showMeta ? 'rotate-45' : ''}`} />
                {showMeta ? "Hide Optional Metadata" : "Add Optional Metadata (DOI, arXiv)"}
              </button>

              {showMeta && (
                <div className="mt-4 space-y-3.5 animate-float">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="space-y-1">
                      <label className="text-[9px] uppercase font-bold tracking-wider text-slate-400 flex items-center gap-1">
                        <Calendar className="w-3 h-3" /> Year
                      </label>
                      <input
                        type="number"
                        placeholder="2026"
                        value={year}
                        onChange={(e) => setYear(e.target.value)}
                        className="w-full px-3 py-2 text-xs bg-slate-100/50 dark:bg-[#0b101c]/50 border border-slate-200/50 dark:border-slate-800/80 rounded-xl outline-none"
                      />
                    </div>
                    <div className="space-y-1">
                      <label className="text-[9px] uppercase font-bold tracking-wider text-slate-400">Conference/Journal</label>
                      <input
                        type="text"
                        placeholder="IEEE S&P"
                        value={conf}
                        onChange={(e) => setConf(e.target.value)}
                        className="w-full px-3 py-2 text-xs bg-slate-100/50 dark:bg-[#0b101c]/50 border border-slate-200/50 dark:border-slate-800/80 rounded-xl outline-none"
                      />
                    </div>
                  </div>
                  <div className="space-y-1">
                    <label className="text-[9px] uppercase font-bold tracking-wider text-slate-400">DOI Reference</label>
                    <input
                      type="text"
                      placeholder="10.1109/SP.2026.01"
                      value={doi}
                      onChange={(e) => setDoi(e.target.value)}
                      className="w-full px-3 py-2 text-xs bg-slate-100/50 dark:bg-[#0b101c]/50 border border-slate-200/50 dark:border-slate-800/80 rounded-xl outline-none"
                    />
                  </div>
                  <div className="space-y-1">
                    <label className="text-[9px] uppercase font-bold tracking-wider text-slate-400 flex items-center gap-1">
                      <Globe className="w-3 h-3" /> arXiv URL
                    </label>
                    <input
                      type="text"
                      placeholder="https://arxiv.org/abs/2402.12345"
                      value={arxiv}
                      onChange={(e) => setArxiv(e.target.value)}
                      className="w-full px-3 py-2 text-xs bg-slate-100/50 dark:bg-[#0b101c]/50 border border-slate-200/50 dark:border-slate-800/80 rounded-xl outline-none"
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Submit btn */}
            <button
              type="submit"
              disabled={loading || !selectedFile}
              className={`w-full py-3 text-xs font-bold rounded-xl transition-all shadow-md flex items-center justify-center gap-2 ${
                selectedFile
                  ? "bg-accent-primary hover:bg-accent-dark text-white active:scale-98 cursor-pointer"
                  : "bg-slate-200 dark:bg-slate-800 text-slate-400 cursor-not-allowed"
              }`}
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
              ) : (
                "Compile and Analyze PDF"
              )}
            </button>
          </form>
        </div>

        {/* Papers Grid List */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col justify-between min-h-[400px]">
          <div>
            <h3 className="text-md font-bold mb-4 border-b border-slate-200/50 dark:border-slate-800/50 pb-3 flex items-center gap-2">
              <FileText className="w-5 h-5 text-indigo-500" />
              Uploaded Paper Corpus
            </h3>

            <div className="space-y-3.5 max-h-[350px] overflow-y-auto pr-1">
              {papers.length > 0 ? (
                papers.map((p, i) => (
                  <div key={i} className="flex justify-between items-center p-3 rounded-xl bg-slate-100/50 dark:bg-[#0b101c]/40 border border-slate-200/20 dark:border-slate-800/40">
                    <div className="max-w-[75%] space-y-1">
                      <h4 className="text-xs font-bold text-slate-700 dark:text-slate-200 truncate">
                        {p.title}
                      </h4>
                      <p className="text-[10px] text-slate-400 truncate font-medium">
                        Authors: {p.authors_text || "Unknown"}
                      </p>
                      <div className="flex gap-2.5 text-[9px] text-slate-400 items-center font-medium">
                        <span>Year: {p.publication_year || "2026"}</span>
                        <span>•</span>
                        <span>Date: {p.upload_date.split("T")[0]}</span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {p.status === "completed" ? (
                        <span className="px-2 py-0.5 text-[9px] bg-green-500/10 text-green-500 rounded-full font-bold">
                          Completed
                        </span>
                      ) : p.status === "processing" ? (
                        <span className="px-2 py-0.5 text-[9px] bg-indigo-500/10 text-indigo-500 rounded-full font-bold flex items-center gap-1">
                          <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping"></span>
                          Analyzing
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 text-[9px] bg-red-500/10 text-red-500 rounded-full font-bold">
                          Error
                        </span>
                      )}
                      
                      <button
                        onClick={() => handleDelete(p.id)}
                        className="p-2 text-slate-400 hover:text-red-500 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg transition-colors cursor-pointer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-xs opacity-60 pt-24 space-y-2">
                  <FileText className="w-10 h-10 mx-auto text-slate-500" />
                  <p>No papers uploaded yet. Initialize index above.</p>
                </div>
              )}
            </div>
          </div>
          
          <div className="text-[10px] opacity-40 text-center border-t border-slate-200/50 dark:border-slate-800/50 pt-3 mt-4">
            Upload articles to generate semantic embedding partitions. Mapped relations are synced directly.
          </div>
        </div>
      </div>
    </div>
  );
};
