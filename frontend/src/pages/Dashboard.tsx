import React, { useState, useEffect } from "react";
import { api } from "../services/api";
import { FileText, Tag, Users, ShieldAlert, Award, RefreshCw, BarChart2, CheckCircle2, Loader2, AlertCircle } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface DashboardStats {
  metrics: {
    total_papers: number;
    total_topics: number;
    total_authors: number;
    total_gaps: number;
    total_ideas: number;
  };
  topic_distribution: Array<{ name: string; count: number }>;
  recent_papers: Array<{ id: number; title: string; status: string; date: string }>;
}

export const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadStats = async () => {
    setLoading(true);
    try {
      const data = await api.getDashboardStats();
      setStats(data);
      setError("");
    } catch (err: any) {
      setError(err.message || "Failed to load dashboard metrics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center py-20 space-y-4">
        <Loader2 className="w-10 h-10 text-indigo-500 animate-spin" />
        <p className="text-sm opacity-60">Synchronizing database aggregations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 glass-panel rounded-2xl text-red-500 flex items-center gap-3">
        <AlertCircle className="w-6 h-6" />
        <p className="text-sm font-semibold">{error}</p>
      </div>
    );
  }

  if (!stats) return null;

  const cardItems = [
    { label: "Research Papers", count: stats.metrics.total_papers, icon: <FileText className="w-6 h-6 text-indigo-500" />, desc: "Indexed PDFs" },
    { label: "Active Authors", count: stats.metrics.total_authors, icon: <Users className="w-6 h-6 text-slate-500" />, desc: "Mapped collaborators" },
    { label: "Core Topics", count: stats.metrics.total_topics, icon: <Tag className="w-6 h-6 text-violet-500" />, desc: "Identified categories" },
    { label: "Detected Gaps", count: stats.metrics.total_gaps, icon: <ShieldAlert className="w-6 h-6 text-amber-500" />, desc: "Methodological overlays" },
    { label: "Novel Ideas", count: stats.metrics.total_ideas, icon: <Award className="w-6 h-6 text-emerald-500" />, desc: "SIH & IEEE drafts" }
  ];

  return (
    <div className="space-y-8 animate-float">
      {/* Top Banner */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight">Overview Dashboard</h1>
          <p className="text-xs opacity-60 mt-1">Real-time telemetry and scientific paper mapping statistics.</p>
        </div>
        <button
          onClick={loadStats}
          className="p-2.5 bg-slate-100 hover:bg-slate-200 dark:bg-panel-dark dark:hover:bg-slate-800 border border-slate-200/50 dark:border-slate-800/80 rounded-xl transition-all duration-300 shadow hover:shadow-md"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Metrics Cards Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-5 gap-6">
        {cardItems.map((item, i) => (
          <div key={i} className="glass-card p-5 flex flex-col justify-between h-36">
            <div className="flex justify-between items-start">
              <span className="text-[10px] uppercase font-bold tracking-wider text-slate-400">
                {item.label}
              </span>
              {item.icon}
            </div>
            <div>
              <h2 className="text-3xl font-extrabold text-slate-800 dark:text-slate-100 mt-2">
                {item.count}
              </h2>
              <p className="text-[10px] text-slate-400 font-medium mt-1">
                {item.desc}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Analytics Visualization Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Topic Frequency Bar Chart */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col h-[380px]">
          <h3 className="text-md font-bold mb-4 flex items-center gap-2">
            <BarChart2 className="w-5 h-5 text-indigo-500" />
            Trending Research Clusters
          </h3>
          <div className="flex-1 w-full text-xs">
            {stats.topic_distribution.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats.topic_distribution} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#1e293b1a" />
                  <XAxis dataKey="name" stroke="#888888" fontSize={9} tickLine={false} axisLine={false} />
                  <YAxis stroke="#888888" fontSize={10} tickLine={false} axisLine={false} allowDecimals={false} />
                  <Tooltip 
                    contentStyle={{ background: "#0f172a", border: "none", borderRadius: "12px", color: "#fff", fontSize: "11px" }}
                    labelStyle={{ fontWeight: "bold" }}
                  />
                  <Bar dataKey="count" fill="url(#indigoGrad)" radius={[6, 6, 0, 0]} barSize={35}>
                    <defs>
                      <linearGradient id="indigoGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#6366f1" />
                        <stop offset="100%" stopColor="#4f46e5" />
                      </linearGradient>
                    </defs>
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center opacity-60">
                No active topic data available. Seed or upload papers.
              </div>
            )}
          </div>
        </div>

        {/* Recent Processing Queue */}
        <div className="glass-panel p-6 rounded-2xl flex flex-col h-[380px] justify-between">
          <div>
            <h3 className="text-md font-bold mb-4 flex items-center gap-2">
              <CheckCircle2 className="w-5 h-5 text-indigo-500" />
              Document Processing Logs
            </h3>
            <div className="space-y-3.5 max-h-[250px] overflow-y-auto pr-1">
              {stats.recent_papers.length > 0 ? (
                stats.recent_papers.map((p, i) => (
                  <div key={i} className="flex justify-between items-center p-3 rounded-xl bg-slate-100/50 dark:bg-[#0b101c]/40 border border-slate-200/20 dark:border-slate-800/40">
                    <div className="max-w-[70%] space-y-0.5">
                      <h4 className="text-xs font-bold truncate text-slate-700 dark:text-slate-200">
                        {p.title}
                      </h4>
                      <span className="text-[9px] text-slate-400 block font-medium">
                        {p.date}
                      </span>
                    </div>
                    <div className="flex items-center gap-1.5">
                      {p.status === "completed" ? (
                        <span className="px-2 py-0.5 text-[9px] bg-green-500/10 text-green-500 rounded-full font-bold">
                          Indexed
                        </span>
                      ) : p.status === "processing" ? (
                        <span className="px-2 py-0.5 text-[9px] bg-indigo-500/10 text-indigo-500 rounded-full font-bold flex items-center gap-1">
                          <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-ping"></span>
                          Parsing
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 text-[9px] bg-red-500/10 text-red-500 rounded-full font-bold">
                          Failed
                        </span>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center text-xs opacity-60 pt-20">
                  No uploads processed.
                </div>
              )}
            </div>
          </div>

          <div className="text-[10px] opacity-40 text-center border-t border-slate-200/50 dark:border-slate-800/50 pt-3">
            Platform parses layout structure containing algorithms, parameters, datasets and metrics.
          </div>
        </div>
      </div>
    </div>
  );
};
