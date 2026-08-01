import React, { useState } from "react";
import { api } from "../services/api";
import { Shield, Mail, Lock, User, GraduationCap, CheckCircle } from "lucide-react";

interface AuthProps {
  onLoginSuccess: () => void;
}

export const Auth: React.FC<AuthProps> = ({ onLoginSuccess }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("Student");
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSuccess("");

    try {
      if (isLogin) {
        await api.login(email, password);
        onLoginSuccess();
      } else {
        await api.register(email, password, fullName, role);
        setSuccess("Registration successful! Switching to login...");
        setTimeout(() => {
          setIsLogin(true);
          setSuccess("");
          setPassword("");
        }, 2000);
      }
    } catch (err: any) {
      setError(err.message || "Authentication process failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center glow-bg px-4 relative">
      <div className="absolute inset-0 bg-[#0f172a]/10 dark:bg-black/40 pointer-events-none" />

      {/* Main card */}
      <div className="w-full max-w-md glass-panel p-8 rounded-3xl relative z-10 shadow-2xl border-white/20 dark:border-slate-800/80">
        <div className="text-center space-y-2 mb-8">
          <div className="w-12 h-12 bg-indigo-500 rounded-2xl flex items-center justify-center mx-auto shadow-lg animate-float">
            <Shield className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-2xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 via-purple-500 to-cyan-500">
            ResearchMind AI
          </h2>
          <p className="text-xs text-slate-400 font-medium">
            AI-Powered Scientific Research Gap Identifier Platform
          </p>
        </div>

        {/* Action Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 text-red-500 text-xs px-4 py-2.5 rounded-xl text-center font-medium">
              {error}
            </div>
          )}
          {success && (
            <div className="bg-green-500/10 border border-green-500/20 text-green-500 text-xs px-4 py-2.5 rounded-xl text-center font-medium flex items-center justify-center gap-2">
              <CheckCircle className="w-4 h-4" />
              {success}
            </div>
          )}

          {!isLogin && (
            <>
              {/* Full Name */}
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Full Name</label>
                <div className="relative">
                  <User className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    required
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    placeholder="Dr. Sarah Jenkins"
                    className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-100/50 dark:bg-[#0b101c]/50 border border-slate-200/50 dark:border-slate-800/80 rounded-xl outline-none focus:border-indigo-500 transition-all"
                  />
                </div>
              </div>

              {/* Scholar Role Selection */}
              <div className="space-y-1">
                <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Research Role</label>
                <div className="relative">
                  <GraduationCap className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-400" />
                  <select
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-100/50 dark:bg-[#0b101c]/50 border border-slate-200/50 dark:border-slate-800/80 rounded-xl outline-none focus:border-indigo-500 transition-all appearance-none cursor-pointer text-slate-600 dark:text-slate-300 font-medium"
                  >
                    <option value="Student">Student (General Access)</option>
                    <option value="Research Scholar">Research Scholar (Upload & Scan)</option>
                    <option value="Professor">Professor (Full Access)</option>
                    <option value="Research Lab">Research Lab (Enterprise Analytics)</option>
                  </select>
                </div>
              </div>
            </>
          )}

          {/* Email */}
          <div className="space-y-1">
            <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="scholar@researchmind.ai"
                className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-100/50 dark:bg-[#0b101c]/50 border border-slate-200/50 dark:border-slate-800/80 rounded-xl outline-none focus:border-indigo-500 transition-all"
              />
            </div>
          </div>

          {/* Password */}
          <div className="space-y-1">
            <label className="text-[10px] uppercase font-bold tracking-wider text-slate-400">Password</label>
            <div className="relative">
              <Lock className="absolute left-3.5 top-3 w-4 h-4 text-slate-400" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-10 pr-4 py-2.5 text-sm bg-slate-100/50 dark:bg-[#0b101c]/50 border border-slate-200/50 dark:border-slate-800/80 rounded-xl outline-none focus:border-indigo-500 transition-all"
              />
            </div>
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-bold text-sm rounded-xl hover:from-indigo-600 hover:to-purple-700 active:scale-98 transition-all shadow-lg hover:shadow-indigo-500/20 duration-300 mt-2 flex items-center justify-center gap-2"
          >
            {loading ? (
              <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
            ) : isLogin ? (
              "Sign In"
            ) : (
              "Create Account"
            )}
          </button>
        </form>

        {/* Toggle */}
        <div className="mt-6 text-center text-xs">
          <span className="text-slate-400 font-medium">
            {isLogin ? "New to the platform? " : "Already have an account? "}
          </span>
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setError("");
            }}
            className="text-indigo-500 hover:text-indigo-600 font-bold underline outline-none"
          >
            {isLogin ? "Register here" : "Sign in here"}
          </button>
        </div>
      </div>
    </div>
  );
};
