import React, { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import { api } from "./services/api";
import { Auth } from "./pages/Auth";
import { Dashboard } from "./pages/Dashboard";
import { Upload } from "./pages/Upload";
import { Compare } from "./pages/Compare";
import { Chat } from "./pages/Chat";
import { GapExplorer } from "./pages/GapExplorer";
import { GraphVisualizer } from "./components/GraphVisualizer";
import { 
  Shield, LayoutDashboard, UploadCloud, Layers, 
  MessageSquare, ShieldAlert, GitBranch, Moon, Sun, LogOut, User, Menu, X 
} from "lucide-react";

export const App: React.FC = () => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem("token"));
  const [userProfile, setUserProfile] = useState<{ fullName: string; role: string } | null>(null);
  const [darkMode, setDarkMode] = useState<boolean>(
    localStorage.getItem("theme") === "dark" || 
    (!localStorage.getItem("theme") && window.matchMedia("(prefers-color-scheme: dark)").matches)
  );
  
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    // Sync dark mode class
    if (darkMode) {
      document.documentElement.classList.add("dark");
      localStorage.setItem("theme", "dark");
    } else {
      document.documentElement.classList.remove("dark");
      localStorage.setItem("theme", "light");
    }
  }, [darkMode]);

  const loadUserProfile = async () => {
    if (!isAuthenticated) return;
    try {
      const data = await api.getMe();
      setUserProfile({
        fullName: data.full_name,
        role: data.role
      });
    } catch (err) {
      console.error("Failed to load user profile:", err);
      handleLogout();
    }
  };

  useEffect(() => {
    loadUserProfile();
  }, [isAuthenticated]);

  const handleLoginSuccess = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    api.logout();
    setIsAuthenticated(false);
    setUserProfile(null);
  };

  if (!isAuthenticated) {
    return <Auth onLoginSuccess={handleLoginSuccess} />;
  }

  const sidebarLinks = [
    { label: "Dashboard", path: "/", icon: <LayoutDashboard className="w-4 h-4" /> },
    { label: "Paper Manager", path: "/upload", icon: <UploadCloud className="w-4 h-4" /> },
    { label: "Compare Matrix", path: "/compare", icon: <Layers className="w-4 h-4" /> },
    { label: "AI Chat Assistant", path: "/chat", icon: <MessageSquare className="w-4 h-4" /> },
    { label: "Research Gap Explorer", path: "/gaps", icon: <ShieldAlert className="w-4 h-4" /> },
    { label: "Knowledge Graph", path: "/graph", icon: <GitBranch className="w-4 h-4" /> }
  ];

  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-background-light dark:bg-background-dark text-slate-800 dark:text-slate-100 transition-colors duration-300">
        
        {/* Desktop Sidebar */}
        <aside className="hidden md:flex flex-col justify-between w-64 bg-white/70 dark:bg-[#121b2d]/70 backdrop-blur border-r border-slate-200/50 dark:border-slate-800/50 p-6 shrink-0 z-20 shadow-lg">
          <div className="space-y-8">
            {/* Logo */}
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 bg-indigo-500 rounded-xl flex items-center justify-center shadow-md">
                <Shield className="w-4.5 h-4.5 text-white" />
              </div>
              <div>
                <h2 className="text-sm font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500">
                  ResearchMind AI
                </h2>
                <span className="text-[8px] font-bold text-slate-400 uppercase tracking-widest block mt-0.5">Platform</span>
              </div>
            </div>

            {/* Navigation links */}
            <nav className="space-y-1.5">
              {sidebarLinks.map((link, i) => (
                <Link
                  key={i}
                  to={link.path}
                  className="flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-xs font-bold text-slate-500 hover:text-indigo-500 dark:text-slate-400 dark:hover:text-slate-200 hover:bg-slate-100/50 dark:hover:bg-slate-800/40 border border-transparent hover:border-slate-200/20 dark:hover:border-slate-800/20 transition-all duration-300 shadow-sm hover:shadow"
                >
                  {link.icon}
                  {link.label}
                </Link>
              ))}
            </nav>
          </div>

          {/* User profile & Actions */}
          <div className="space-y-4 pt-6 border-t border-slate-200/50 dark:border-slate-800/50">
            {userProfile && (
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-slate-100 dark:bg-slate-800 border border-slate-200/50 dark:border-slate-800/50 rounded-xl flex items-center justify-center shrink-0">
                  <User className="w-4 h-4 text-slate-400" />
                </div>
                <div className="max-w-[130px] truncate leading-tight">
                  <span className="text-xs font-extrabold text-slate-700 dark:text-slate-200 truncate block">
                    {userProfile.fullName}
                  </span>
                  <span className="text-[9px] text-slate-400 font-semibold uppercase tracking-wider block mt-0.5">
                    {userProfile.role}
                  </span>
                </div>
              </div>
            )}

            <div className="flex items-center justify-between gap-2.5">
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2.5 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-xl text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
              >
                {darkMode ? <Sun className="w-4.5 h-4.5" /> : <Moon className="w-4.5 h-4.5" />}
              </button>
              
              <button
                onClick={handleLogout}
                className="flex-1 flex items-center justify-center gap-1.5 py-2.5 bg-red-500/10 hover:bg-red-500 text-red-500 hover:text-white text-xs font-bold rounded-xl transition-all shadow hover:shadow-red-500/10 cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
                Log Out
              </button>
            </div>
          </div>
        </aside>

        {/* Mobile Menu Sidebar Overlay */}
        {mobileMenuOpen && (
          <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm md:hidden flex">
            <aside className="w-64 bg-white dark:bg-[#121b2d] p-6 flex flex-col justify-between shadow-2xl h-full animate-float">
              <div className="space-y-8">
                <div className="flex justify-between items-center">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-indigo-500 rounded-xl flex items-center justify-center">
                      <Shield className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-sm font-extrabold">ResearchMind AI</span>
                  </div>
                  <button onClick={() => setMobileMenuOpen(false)} className="p-1 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg">
                    <X className="w-5 h-5" />
                  </button>
                </div>
                
                <nav className="space-y-2">
                  {sidebarLinks.map((link, i) => (
                    <Link
                      key={i}
                      to={link.path}
                      onClick={() => setMobileMenuOpen(false)}
                      className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800/40"
                    >
                      {link.icon}
                      {link.label}
                    </Link>
                  ))}
                </nav>
              </div>
              
              <div className="space-y-4 pt-4 border-t border-slate-200 dark:border-slate-800">
                <button onClick={handleLogout} className="w-full flex items-center justify-center gap-2 py-2.5 bg-red-500/10 text-red-500 rounded-xl text-xs font-bold">
                  <LogOut className="w-4 h-4" /> Log Out
                </button>
              </div>
            </aside>
            <div className="flex-1" onClick={() => setMobileMenuOpen(false)} />
          </div>
        )}

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col min-h-screen overflow-hidden">
          {/* Header */}
          <header className="p-4 md:px-8 border-b border-slate-200/50 dark:border-slate-800/50 flex justify-between items-center bg-white/40 dark:bg-panel-dark/40 backdrop-blur z-10 shadow-sm">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setMobileMenuOpen(true)}
                className="md:hidden p-1.5 hover:bg-slate-200 dark:hover:bg-slate-800 rounded-lg text-slate-400 hover:text-slate-200 transition-colors"
              >
                <Menu className="w-5 h-5" />
              </button>
              <span className="text-[10px] uppercase font-extrabold tracking-wider text-indigo-500/80 px-2.5 py-1 bg-indigo-500/10 rounded-full border border-indigo-500/20 shadow-sm">
                IEEE / SIH Demo Version
              </span>
            </div>
            
            <div className="flex items-center gap-3">
              {/* Header profile view for mobile */}
              <div className="md:hidden w-8 h-8 bg-slate-100 dark:bg-slate-800 border border-slate-200/50 rounded-xl flex items-center justify-center">
                <User className="w-4 h-4 text-slate-400" />
              </div>
              <span className="hidden md:inline text-xs text-slate-400 font-semibold tracking-wide">
                Current Time: {new Date().toLocaleDateString()}
              </span>
            </div>
          </header>

          {/* Page Routing */}
          <main className="flex-1 overflow-y-auto p-6 md:p-8 scrollbar">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<Upload />} />
              <Route path="/compare" element={<Compare />} />
              <Route path="/chat" element={<Chat />} />
              <Route path="/gaps" element={<GapExplorer />} />
              <Route path="/graph" element={<div className="space-y-6">
                <div>
                  <h1 className="text-3xl font-extrabold tracking-tight">Interactive Knowledge Graph</h1>
                  <p className="text-xs opacity-60 mt-1">Render semantic paths bridging papers, topics, authors, benchmarks, and research gaps.</p>
                </div>
                <GraphVisualizer />
              </div>} />
              <Route path="*" element={<Navigate to="/" />} />
            </Routes>
          </main>
        </div>

      </div>
    </BrowserRouter>
  );
};
export default App;
