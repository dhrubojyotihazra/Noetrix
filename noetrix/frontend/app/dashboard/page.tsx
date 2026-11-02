"use client";

import React, { useState, useEffect } from "react";
import {
  Sparkles,
  Play,
  CheckCircle2,
  Circle,
  ShieldAlert,
  ArrowUpRight,
  ArrowDownRight,
  MoreHorizontal,
  Bell,
  Search,
  Globe,
  Sliders,
  Terminal,
  Layers,
  Share2,
  Plus,
  RefreshCw,
  X
} from "lucide-react";

interface RunItem {
  id: string;
  name: string;
  time: string;
  latency: string;
  status: "Live" | "Paused" | "Completed";
  description: string;
}

export default function GlassDashboardPage() {
  // Preset mode: 'flux' (AI Studio matching screenshot) or 'noetrix' (Candidate ATS)
  const [appMode, setAppMode] = useState<"flux" | "noetrix">("flux");
  
  // Checklist reactive state
  const [checklist, setChecklist] = useState([
    { id: 1, text: "Create your first workspace", done: true },
    { id: 2, text: "Deploy an AI agent", done: true },
    { id: 3, text: "Configure data connectors", done: false },
    { id: 4, text: "Set up approval workflows", done: false },
  ]);

  // Live Stream items
  const [runs, setRuns] = useState<RunItem[]>([
    { id: "1", name: "Claims Checker", time: "3 min ago", latency: "2.1s", status: "Live", description: "Stateless resume claim cross-validation with zero hallucination guarantee." },
    { id: "2", name: "KYC Validator", time: "4 min ago", latency: "1.8s", status: "Live", description: "Identity scrubbing and phone/email PII sanitization." },
    { id: "3", name: "Fraud Monitor", time: "7 min ago", latency: "15s", status: "Paused", description: "Keyword stuffing trigger alert (heuristic velocity threshold exceeded)." },
    { id: "4", name: "Audit Analyzer", time: "10 min ago", latency: "1.2s", status: "Live", description: "6-tier deterministic tie-breaking matrix execution." },
  ]);

  const [isStreaming, setIsStreaming] = useState(true);
  const [selectedRun, setSelectedRun] = useState<RunItem | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [tokensCount, setTokensCount] = useState(2.4);

  // Toast trigger
  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3000);
  };

  // Checklist toggle
  const toggleCheck = (id: number) => {
    setChecklist(prev =>
      prev.map(item => item.id === id ? { ...item, done: !item.done } : item)
    );
    const item = checklist.find(c => c.id === id);
    showToast(item?.done ? `Milestone ${id} marked incomplete` : `Milestone ${id} completed!`);
  };

  const completedCount = checklist.filter(c => c.done).length;
  const progressPercent = Math.round((completedCount / checklist.length) * 100);

  // Streaming run simulation
  useEffect(() => {
    if (!isStreaming) return;
    const interval = setInterval(() => {
      const candidates = [
        { name: "NLP Embedding Scorer", latency: "0.45s", description: "MiniLM Cosine vector alignment verified" },
        { name: "Zero-Fabrication Validator", latency: "1.10s", description: "Bullet rewrite cross-checked against source resume" },
        { name: "ATS Parser Sanitizer", latency: "0.28s", description: "Two-column heuristic and contact parsing complete" },
        { name: "Soft Knockout Guard", latency: "0.19s", description: "50% must-have criteria floor checked" }
      ];
      const pick = candidates[Math.floor(Math.random() * candidates.length)];
      const newRun: RunItem = {
        id: Date.now().toString(),
        name: pick.name,
        time: "Just now",
        latency: pick.latency,
        status: Math.random() > 0.85 ? "Paused" : "Live",
        description: pick.description
      };
      setRuns(prev => [newRun, ...prev.slice(0, 4)]);
    }, 4500);

    return () => clearInterval(interval);
  }, [isStreaming]);

  // Demo launch trigger
  const handleLaunchDemo = () => {
    showToast("🚀 Simulating live AI screening batch run...");
    setTimeout(() => {
      setTokensCount(prev => +(prev + 0.1).toFixed(1));
      const demoRun: RunItem = {
        id: Date.now().toString(),
        name: appMode === "flux" ? "Synth-Agent 409" : "Alex Chen (Senior ML Engineer)",
        time: "Just now",
        latency: "0.62s",
        status: "Live",
        description: "Scored across 6 deterministic dimensions: 94% composite score."
      };
      setRuns(prev => [demoRun, ...prev.slice(0, 4)]);
      showToast("✅ Run complete: 94% compliance calibrated!");
    }, 800);
  };

  return (
    <div className="relative min-h-screen bg-[#E9EEF4] text-slate-800 p-4 md:p-8 overflow-x-hidden selection:bg-amber-200">
      
      {/* Dynamic Background Mesh Gradient Blobs */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div className="absolute top-[8%] right-[15%] w-[640px] h-[520px] rounded-full bg-gradient-to-tr from-[#FFAA5B]/50 via-[#FBBF24]/35 to-[#FDE68A]/50 blur-[100px] animate-pulse"></div>
        <div className="absolute top-[32%] right-[28%] w-[420px] h-[360px] rounded-full bg-[#FB923C]/30 blur-[90px]"></div>
        <div className="absolute bottom-[4%] left-[6%] w-[480px] h-[380px] rounded-full bg-[#BAE6FD]/35 blur-[100px]"></div>
      </div>

      <div className="relative z-10 max-w-[1500px] mx-auto flex flex-col gap-6">

        {/* ============================================================== */}
        {/* TOP NAVIGATION BAR                                             */}
        {/* ============================================================== */}
        <header className="bg-white/60 backdrop-blur-xl border border-white/80 rounded-2xl px-5 py-3 flex items-center justify-between shadow-sm">
          
          <div className="flex items-center gap-6">
            <div 
              onClick={() => setAppMode(prev => prev === "flux" ? "noetrix" : "flux")}
              className="flex items-center gap-2.5 cursor-pointer select-none"
              title="Click to toggle preset (Flux UI vs Noetrix ATS)"
            >
              <div className="w-8 h-8 rounded-full bg-slate-900 flex items-center justify-center text-amber-300 shadow-sm ring-2 ring-white">
                <Sparkles className="w-4 h-4 animate-spin-slow" />
              </div>
              <span className="text-xl font-bold tracking-tight text-slate-900">
                {appMode === "flux" ? "Flux" : "Noetrix"}
              </span>
            </div>

            <div className="hidden md:flex items-center gap-1.5 pl-3 border-l border-slate-300/60">
              <button className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-slate-900 text-white text-xs font-semibold shadow-sm">
                <Layers className="w-3.5 h-3.5 text-yellow-400" />
                <span>Dashboard</span>
              </button>
              
              <button className="w-8 h-8 rounded-full flex items-center justify-center text-slate-600 hover:bg-white/80 transition" title="Terminal">
                <Terminal className="w-4 h-4" />
              </button>
              <button className="w-8 h-8 rounded-full flex items-center justify-center text-slate-600 hover:bg-white/80 transition" title="Data Connectors">
                <Share2 className="w-4 h-4" />
              </button>
              <button className="w-8 h-8 rounded-full flex items-center justify-center text-slate-600 hover:bg-white/80 transition" title="Intelligence">
                <Sparkles className="w-4 h-4 text-amber-500" />
              </button>
              <button className="w-8 h-8 rounded-full flex items-center justify-center text-slate-600 hover:bg-white/80 transition" title="Settings">
                <Sliders className="w-4 h-4" />
              </button>
              <button className="w-7 h-7 rounded-full bg-white/80 border border-white flex items-center justify-center text-slate-700 hover:bg-white transition" title="New Component">
                <Plus className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden lg:flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[11px] font-semibold text-emerald-700">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
              <span className="w-2 h-2 rounded-full bg-emerald-500 -ml-3.5"></span>
              <span>All Systems Nominal</span>
            </div>

            <button className="w-8 h-8 rounded-full flex items-center justify-center text-slate-600 hover:bg-white/80 transition">
              <Search className="w-4 h-4" />
            </button>

            <button 
              onClick={() => showToast("Alerts: All candidate parsing guardrails are active.")}
              className="relative w-8 h-8 rounded-full flex items-center justify-center text-slate-600 hover:bg-white/80 transition"
            >
              <Bell className="w-4 h-4" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-rose-500 rounded-full ring-2 ring-white"></span>
            </button>

            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/70 border border-white text-xs text-slate-700">
              <Globe className="w-3.5 h-3.5 text-slate-500" />
              <span className="font-medium">English</span>
            </div>

            <button 
              onClick={() => setAppMode(prev => prev === "flux" ? "noetrix" : "flux")}
              className="px-2.5 py-1 rounded-full bg-slate-900/10 hover:bg-slate-900/15 border border-white text-[11px] font-semibold text-slate-800 transition"
            >
              {appMode === "flux" ? "Flux Preset" : "Noetrix ATS"}
            </button>

            <div className="relative">
              <img 
                src="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&h=120&q=80" 
                alt="Aisha" 
                className="w-9 h-9 rounded-full object-cover ring-2 ring-white shadow-sm"
              />
              <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-emerald-500 ring-2 ring-white"></span>
            </div>
          </div>
        </header>

        {/* ============================================================== */}
        {/* WELCOME BANNER & ACTION BAR                                    */}
        {/* ============================================================== */}
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900">
              {appMode === "flux" ? "Welcome Back, Aisha" : "Welcome Back, Dhrubojyoti"}
              <span className="inline-block ml-2 text-2xl">👋</span>
            </h1>
            <p className="text-slate-500 text-sm mt-1">
              {appMode === "flux" 
                ? "Your AI environment is monitoring agents, runs and compliance." 
                : "Your AI screening engine is monitoring resumes, candidate runs, and compliance."}
            </p>
          </div>

          <div className="flex items-center flex-wrap gap-2.5">
            <button 
              onClick={() => showToast("Opening New Agent creation modal")}
              className="px-4 py-2 rounded-xl bg-white/70 hover:bg-white text-xs font-semibold text-slate-800 border border-white shadow-sm transition flex items-center gap-2"
            >
              <Plus className="w-3.5 h-3.5 text-slate-600" />
              <span>{appMode === "flux" ? "New Agent" : "Screen Resume"}</span>
            </button>

            <button 
              onClick={() => showToast("Opening Data Connectors modal")}
              className="px-4 py-2 rounded-xl bg-white/70 hover:bg-white text-xs font-semibold text-slate-800 border border-white shadow-sm transition flex items-center gap-2"
            >
              <Share2 className="w-3.5 h-3.5 text-slate-600" />
              <span>Connect Data</span>
            </button>

            <button 
              onClick={() => showToast("Audit log: All candidate evaluations verified deterministic")}
              className="px-4 py-2 rounded-xl bg-white/70 hover:bg-white text-xs font-semibold text-slate-800 border border-white shadow-sm transition flex items-center gap-2"
            >
              <ShieldAlert className="w-3.5 h-3.5 text-slate-600" />
              <span>Review Approval</span>
            </button>

            <button 
              onClick={() => showToast("Navigating to Recruiter Workspace")}
              className="px-4 py-2 rounded-xl bg-white/70 hover:bg-white text-xs font-semibold text-slate-800 border border-white shadow-sm transition flex items-center gap-2"
            >
              <Layers className="w-3.5 h-3.5 text-slate-600" />
              <span>View Workspace</span>
            </button>

            {/* Signature High-Visibility Yellow Launch Demo Button */}
            <button 
              onClick={handleLaunchDemo}
              className="px-5 py-2 rounded-xl bg-[#FACC15] hover:bg-[#EAB308] text-slate-950 font-bold text-xs flex items-center gap-2 shadow-sm hover:scale-105 active:scale-95 transition transform"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>Launch Demo</span>
            </button>
          </div>
        </div>

        {/* ============================================================== */}
        {/* TOP ROW: GETTING STARTED & COMPLIANCE PULSE                    */}
        {/* ============================================================== */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
          
          {/* 1. GETTING STARTED CHECKLIST */}
          <div className="lg:col-span-7 bg-white/60 backdrop-blur-xl border border-white/80 rounded-3xl p-6 flex flex-col justify-between shadow-sm hover:shadow-md transition">
            <div>
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-xl font-bold text-slate-900 tracking-tight">Getting Started</h2>
                  <p className="text-slate-500 text-xs mt-1">This checklist highlights the onboarding milestone you need to complete</p>
                </div>
                <span className="text-sm font-extrabold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
                  {progressPercent}%
                </span>
              </div>

              {/* Progress Bar Track */}
              <div className="w-full bg-slate-200/70 h-2.5 rounded-full mt-4 overflow-hidden p-0.5">
                <div 
                  className="bg-gradient-to-r from-emerald-500 to-teal-400 h-full rounded-full transition-all duration-500 ease-out" 
                  style={{ width: `${progressPercent}%` }}
                />
              </div>

              {/* Checklist Items */}
              <div className="mt-5 space-y-3">
                {checklist.map(item => (
                  <div 
                    key={item.id}
                    onClick={() => toggleCheck(item.id)}
                    className="group flex items-center gap-3.5 p-2 rounded-xl hover:bg-white/60 transition cursor-pointer"
                  >
                    {item.done ? (
                      <div className="w-5 h-5 rounded-full bg-emerald-500 text-white flex items-center justify-center flex-shrink-0 shadow-sm transition">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                      </div>
                    ) : (
                      <div className="w-5 h-5 rounded-full border-2 border-slate-300 text-transparent flex items-center justify-center flex-shrink-0 group-hover:border-slate-500 transition">
                        <Circle className="w-3.5 h-3.5" />
                      </div>
                    )}
                    <span className={`text-sm font-medium ${item.done ? "text-slate-800 line-through opacity-70" : "text-slate-800 group-hover:text-slate-950"}`}>
                      {item.text}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200/60 flex items-center justify-between text-xs text-slate-400 mt-4">
              <span>Click any milestone to toggle status</span>
              <button 
                onClick={() => {
                  setChecklist(prev => prev.map(c => ({ ...c, done: false })));
                  showToast("Checklist reset to 0%");
                }} 
                className="text-emerald-700 font-semibold hover:underline"
              >
                Reset
              </button>
            </div>
          </div>

          {/* 2. COMPLIANCE PULSE (Speedometer Gauge) */}
          <div className="lg:col-span-5 bg-white/60 backdrop-blur-xl border border-white/80 rounded-3xl p-6 flex flex-col justify-between shadow-sm hover:shadow-md transition">
            <div>
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-slate-900 tracking-tight">Compliance pulse</h2>
                <button className="text-slate-400 hover:text-slate-700">
                  <MoreHorizontal className="w-4 h-4" />
                </button>
              </div>

              {/* Speedometer SVG Gauge */}
              <div className="relative w-64 mx-auto mt-2 flex flex-col items-center">
                <svg viewBox="0 0 200 115" className="w-full">
                  <path d="M 20 100 A 80 80 0 0 1 180 100" fill="none" stroke="#E2E8F0" strokeWidth="14" strokeLinecap="round" />
                  {/* Orange Segment */}
                  <path d="M 20 100 A 80 80 0 0 1 55 45" fill="none" stroke="#F97316" strokeWidth="14" strokeLinecap="round" className="cursor-pointer hover:opacity-80 transition" />
                  {/* Green Segment */}
                  <path d="M 64 38 A 80 80 0 0 1 136 38" fill="none" stroke="#22C55E" strokeWidth="14" strokeLinecap="round" className="cursor-pointer hover:opacity-80 transition" />
                  {/* Blue Segment */}
                  <path d="M 145 45 A 80 80 0 0 1 180 100" fill="none" stroke="#3B82F6" strokeWidth="14" strokeLinecap="round" className="cursor-pointer hover:opacity-80 transition" />
                </svg>

                <div className="absolute bottom-1 text-center select-none">
                  <span className="block text-[11px] font-semibold text-slate-400 uppercase tracking-wider">Policy Coverage</span>
                  <span className="text-3xl font-extrabold text-slate-900 tracking-tight">94%</span>
                </div>
              </div>

              {/* Policy List */}
              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between text-xs py-1.5 px-3 rounded-xl bg-white/50 border border-white">
                  <span className="font-medium text-slate-700">Data Privacy (DAT-001)</span>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-bold text-[10px]">Active</span>
                </div>
                <div className="flex items-center justify-between text-xs py-1.5 px-3 rounded-xl bg-white/50 border border-white">
                  <span className="font-medium text-slate-700">Applicant Bias (APR-104)</span>
                  <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-700 font-bold text-[10px]">Active</span>
                </div>
                <div className="flex items-center justify-between text-xs py-1.5 px-3 rounded-xl bg-white/50 border border-white">
                  <span className="font-medium text-slate-700">Security Tracking (SEC-008)</span>
                  <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-700 font-bold text-[10px]">Audit</span>
                </div>
              </div>
            </div>
          </div>

        </div>

        {/* ============================================================== */}
        {/* MIDDLE ROW: 4 METRIC STAT CARDS WITH SPARKLINE VISUALIZATIONS */}
        {/* ============================================================== */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          
          {/* Card 1: Tokens */}
          <div className="bg-white/60 backdrop-blur-xl border border-white/80 rounded-2xl p-5 flex flex-col justify-between shadow-sm hover:shadow-md transition">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Tokens</span>
                <MoreHorizontal className="w-3.5 h-3.5 text-slate-400" />
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-extrabold text-slate-900 tracking-tight">{tokensCount}M</span>
                <span className="text-[11px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-md flex items-center">
                  <ArrowUpRight className="w-3 h-3 mr-0.5" /> 7.8%
                </span>
              </div>
              <span className="text-[11px] text-slate-400 block mt-0.5">Compare from last 24hrs</span>
            </div>

            <div className="mt-4 pt-2 relative">
              <div className="flex items-end justify-between h-10 gap-1">
                {[20, 35, 18, 45, 60, 25, 40, 75, 30, 85, 40, 50, 70, 90, 45, 60, 80, 55, 65, 95].map((h, i) => (
                  <div 
                    key={i} 
                    style={{ height: `${h}%` }} 
                    className={`w-1 rounded-t-sm transition-all duration-300 hover:scale-110 ${i >= 16 ? "bg-emerald-500" : "bg-slate-300/70"}`}
                  />
                ))}
              </div>
              <span className="absolute -top-3.5 right-6 text-[10px] font-bold text-slate-400">8h</span>
            </div>
          </div>

          {/* Card 2: Cost */}
          <div className="bg-white/60 backdrop-blur-xl border border-white/80 rounded-2xl p-5 flex flex-col justify-between shadow-sm hover:shadow-md transition">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Cost</span>
                <MoreHorizontal className="w-3.5 h-3.5 text-slate-400" />
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-extrabold text-slate-900 tracking-tight">$127</span>
                <span className="text-[11px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-md flex items-center">
                  <ArrowUpRight className="w-3 h-3 mr-0.5" /> 1.5%
                </span>
              </div>
              <span className="text-[11px] text-slate-400 block mt-0.5">Compare from last 24hrs</span>
            </div>

            <div className="mt-4 pt-2 relative">
              <svg viewBox="0 0 100 35" className="w-full h-10 overflow-visible">
                <defs>
                  <linearGradient id="waveGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#10B981" stopOpacity="0.35" />
                    <stop offset="100%" stopColor="#10B981" stopOpacity="0.0" />
                  </linearGradient>
                </defs>
                <path d="M 0 35 Q 15 32, 28 26 T 55 18 T 80 8 L 88 15 L 100 24 L 100 35 Z" fill="url(#waveGrad)" />
                <path d="M 0 32 Q 15 30, 28 26 T 55 18 T 80 8 L 88 15 L 100 24" fill="none" stroke="#10B981" strokeWidth="2" strokeLinecap="round" />
                <circle cx="80" cy="8" r="2.5" fill="#10B981" />
              </svg>
              <span className="absolute -top-3.5 right-4 text-[10px] font-bold text-slate-400">16h</span>
            </div>
          </div>

          {/* Card 3: Success Rate */}
          <div className="bg-white/60 backdrop-blur-xl border border-white/80 rounded-2xl p-5 flex flex-col justify-between shadow-sm hover:shadow-md transition">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">Success Rate</span>
                <MoreHorizontal className="w-3.5 h-3.5 text-slate-400" />
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-extrabold text-slate-900 tracking-tight">97.3%</span>
                <span className="text-[11px] font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded-md flex items-center">
                  <ArrowUpRight className="w-3 h-3 mr-0.5" /> 1.2%
                </span>
              </div>
              <span className="text-[11px] text-slate-400 block mt-0.5">Compare from last month</span>
            </div>

            <div className="mt-4 pt-2 relative">
              <div className="flex items-end justify-between h-10 gap-1.5">
                {[55, 70, 60, 80, 75, 90, 85, 98, 92, 97].map((h, i) => (
                  <div 
                    key={i} 
                    style={{ height: `${h}%` }} 
                    className={`w-1.5 rounded-t-sm transition-all duration-300 ${h > 90 ? "bg-emerald-500" : "bg-slate-300"}`} 
                  />
                ))}
              </div>
              <span className="absolute -top-3.5 right-6 text-[10px] font-bold text-slate-400">24h</span>
            </div>
          </div>

          {/* Card 4: P95 Latency */}
          <div className="bg-white/60 backdrop-blur-xl border border-white/80 rounded-2xl p-5 flex flex-col justify-between shadow-sm hover:shadow-md transition">
            <div>
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-500">P95 Latency</span>
                <MoreHorizontal className="w-3.5 h-3.5 text-slate-400" />
              </div>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-2xl font-extrabold text-slate-900 tracking-tight">234ms</span>
                <span className="text-[11px] font-bold text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded-md flex items-center">
                  <ArrowDownRight className="w-3 h-3 mr-0.5" /> 4.5%
                </span>
              </div>
              <span className="text-[11px] text-slate-400 block mt-0.5">Compare from last month</span>
            </div>

            <div className="mt-4 pt-2 relative">
              <svg viewBox="0 0 100 35" className="w-full h-10">
                <defs>
                  <linearGradient id="latencyGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#F43F5E" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#FBBF24" stopOpacity="0.05" />
                  </linearGradient>
                </defs>
                <path d="M 0 26 Q 20 20, 35 28 T 60 18 T 85 24 L 100 20 L 100 35 L 0 35 Z" fill="url(#latencyGrad)" />
                <path d="M 0 26 Q 20 20, 35 28 T 60 18 T 85 24 L 100 20" fill="none" stroke="#F43F5E" strokeWidth="1.8" />
                <circle cx="60" cy="18" r="2.5" fill="#F43F5E" />
              </svg>
              <span className="absolute -top-3.5 right-6 text-[10px] font-bold text-slate-400">12h</span>
            </div>
          </div>

        </div>

        {/* ============================================================== */}
        {/* BOTTOM ROW: 30-DAY FORECAST & LIVE RUNS STREAM TABLE           */}
        {/* ============================================================== */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch mb-6">
          
          {/* 1. 30-Day Cost Forecast */}
          <div className="lg:col-span-5 bg-white/60 backdrop-blur-xl border border-white/80 rounded-3xl p-6 flex flex-col justify-between shadow-sm hover:shadow-md transition">
            <div>
              <h2 className="text-sm font-semibold text-slate-500">30-day Cost Forecast</h2>
              <div className="flex items-baseline gap-2 mt-1">
                <span className="text-3xl font-extrabold text-slate-900 tracking-tight">$3,890</span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">+1.5% Projected spend for next 30 days</p>

              <div className="mt-6">
                <div className="flex justify-between text-[11px] font-bold text-slate-500 mb-1.5 px-0.5">
                  <span>40%</span>
                  <span className="pl-14">30%</span>
                  <span>40%</span>
                </div>

                <div className="flex items-center gap-2">
                  <div className="flex-1 flex gap-1 items-center">
                    {[...Array(9)].map((_, i) => (
                      <div key={i} className="h-3 w-1.5 rounded-sm bg-sky-400 hover:scale-125 transition" />
                    ))}
                  </div>
                  <div className="w-24 h-3.5 rounded-sm bg-gradient-to-r from-orange-500 to-amber-500 shadow-sm" />
                  <div className="flex-1 flex gap-1 items-center justify-end">
                    {[...Array(8)].map((_, i) => (
                      <div key={i} className="h-3 w-1.5 rounded-sm bg-emerald-500 hover:scale-125 transition" />
                    ))}
                  </div>
                </div>

                <div className="flex items-center gap-5 mt-4 text-xs">
                  <div className="flex items-center gap-1.5 text-slate-600">
                    <span className="w-2 h-2 rounded-full bg-sky-400"></span>
                    <span>Unused</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-600">
                    <span className="w-2 h-2 rounded-full bg-orange-500"></span>
                    <span>Used</span>
                  </div>
                  <div className="flex items-center gap-1.5 text-slate-600">
                    <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                    <span>Reserved</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-6 pt-3 border-t border-slate-200/60 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-slate-600 font-medium">
                <ShieldAlert className="w-4 h-4 text-amber-500" />
                <span>Confidence</span>
              </div>
              <div>
                <span className="font-extrabold text-slate-900">87%</span>
                <span className="text-slate-400 ml-1">in last month</span>
              </div>
            </div>
          </div>

          {/* 2. Live Runs Stream */}
          <div className="lg:col-span-7 bg-white/60 backdrop-blur-xl border border-white/80 rounded-3xl p-6 flex flex-col justify-between shadow-sm hover:shadow-md transition">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                  <h2 className="text-base font-bold text-slate-900 tracking-tight">Live Runs Stream</h2>
                </div>

                <div className="flex items-center gap-2">
                  <button 
                    onClick={() => {
                      setIsStreaming(prev => !prev);
                      showToast(!isStreaming ? "Stream resumed" : "Stream paused");
                    }}
                    className="px-2.5 py-1 rounded-full bg-white/70 hover:bg-white text-[11px] font-semibold text-slate-700 border border-white transition flex items-center gap-1"
                  >
                    <span className={`w-1.5 h-1.5 rounded-full ${isStreaming ? "bg-emerald-500" : "bg-slate-400"}`}></span>
                    <span>Stream: {isStreaming ? "ON" : "OFF"}</span>
                  </button>
                  <span className="px-2.5 py-0.5 rounded-full bg-slate-900 text-white font-bold text-[11px] shadow-sm">
                    Live ({runs.length})
                  </span>
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="border-b border-slate-200/80 text-slate-400 font-semibold">
                      <th className="pb-2.5 pl-2">Name</th>
                      <th className="pb-2.5">Time</th>
                      <th className="pb-2.5">Latency</th>
                      <th className="pb-2.5 text-right pr-2">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100/80">
                    {runs.map(run => (
                      <tr 
                        key={run.id}
                        onClick={() => setSelectedRun(run)}
                        className="group hover:bg-white/80 transition cursor-pointer"
                      >
                        <td className="py-3 pl-2 font-medium text-slate-800 flex items-center gap-2">
                          <span className={`w-1.5 h-1.5 rounded-full ${run.status === "Paused" ? "bg-rose-500" : "bg-emerald-500"}`}></span>
                          <span>{run.name}</span>
                        </td>
                        <td className="py-3 text-slate-500">{run.time}</td>
                        <td className="py-3 text-slate-600 font-mono">{run.latency}</td>
                        <td className="py-3 text-right pr-2">
                          <span className={`px-2.5 py-0.5 rounded-full font-bold text-[10px] ${run.status === "Paused" ? "bg-rose-100 text-rose-700" : "bg-emerald-100/80 text-emerald-800"}`}>
                            {run.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-200/60 flex items-center justify-between text-xs text-slate-400 mt-3">
              <span>Click any run row to inspect telemetry trace</span>
              <span className="text-slate-600 font-medium">Auto-refreshed live</span>
            </div>
          </div>

        </div>

      </div>

      {/* Slide-Over Run Telemetry Drawer */}
      {selectedRun && (
        <div 
          className="fixed inset-0 bg-slate-900/30 backdrop-blur-sm z-50 flex justify-end animate-fade-slide-down"
          onClick={() => setSelectedRun(null)}
        >
          <div 
            className="w-full max-w-md bg-white/95 backdrop-blur-2xl h-full shadow-2xl p-6 flex flex-col justify-between border-l border-white"
            onClick={e => e.stopPropagation()}
          >
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-slate-200">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Run Telemetry</span>
                  <h3 className="text-lg font-bold text-slate-900">{selectedRun.name}</h3>
                </div>
                <button 
                  onClick={() => setSelectedRun(null)}
                  className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-slate-500 hover:bg-slate-200"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              <div className="mt-5 space-y-4 text-xs">
                <div>
                  <span className="text-slate-400 block font-medium">Status & Execution Time</span>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`px-2.5 py-0.5 rounded-full font-bold text-xs ${selectedRun.status === "Paused" ? "bg-rose-100 text-rose-700" : "bg-emerald-100 text-emerald-700"}`}>
                      {selectedRun.status}
                    </span>
                    <span className="font-mono text-slate-700 font-semibold">{selectedRun.latency}</span>
                  </div>
                </div>

                <div>
                  <span className="text-slate-400 block font-medium">Execution Summary</span>
                  <p className="mt-1 text-slate-700 bg-slate-50 p-3 rounded-xl border border-slate-200 leading-relaxed">
                    {selectedRun.description}
                  </p>
                </div>

                <div>
                  <span className="text-slate-400 block font-medium">Telemetry Trace Log</span>
                  <div className="mt-1 bg-slate-900 text-emerald-400 p-3 rounded-xl font-mono text-[11px] h-48 overflow-y-auto leading-relaxed">
                    [00:01.02] INGEST: Stream packet received<br />
                    [00:01.15] VALIDATOR: Schema verified (Zero-Fabrication)<br />
                    [00:01.42] EMBEDDING: Cosine alignment score = 0.941<br />
                    [00:01.78] KNOCKOUT: 50% must-have check passed<br />
                    [00:02.10] OUTPUT: Stateless ephemeral cache cleared<br />
                    [00:02.10] STATUS: SUCCESS (0 PII leaked)
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-slate-200 flex items-center justify-end gap-2">
              <button 
                onClick={() => setSelectedRun(null)} 
                className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-600 hover:bg-slate-100"
              >
                Dismiss
              </button>
              <button 
                onClick={() => {
                  showToast("Telemetry diagnostic exported");
                  setSelectedRun(null);
                }} 
                className="px-4 py-2 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800"
              >
                Export JSON
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-slate-900 text-white px-4 py-2.5 rounded-xl text-xs font-semibold shadow-xl border border-slate-700 flex items-center gap-2 animate-fade-slide-down">
          <span className="w-2 h-2 rounded-full bg-yellow-400"></span>
          <span>{toastMessage}</span>
        </div>
      )}

    </div>
  );
}
