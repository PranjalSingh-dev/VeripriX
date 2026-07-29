import React from 'react';

export default function Navbar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'detect', label: 'AI Detection (F1/F5)' },
    { id: 'compare', label: 'Image Comparison (F2)' },
    { id: 'search', label: 'Reverse Search (F3)' },
    { id: 'video', label: 'Video Analysis (F9)' },
    { id: 'history', label: 'Scan History' },
  ];

  return (
    <header className="glass-panel sticky top-0 z-50 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 via-indigo-500 to-purple-500 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <span className="font-bold text-xl text-white">V</span>
        </div>
        <div>
          <h1 className="font-extrabold text-xl tracking-tight gradient-text">VeriPix</h1>
          <p className="text-xs text-slate-400 font-medium">AI Verification & Search Platform</p>
        </div>
      </div>

      <nav className="flex gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
              activeTab === tab.id
                ? 'bg-slate-800 text-cyan-400 border border-cyan-500/30 shadow-md shadow-cyan-500/10'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </nav>

      <div className="flex items-center gap-2">
        <span className="px-3 py-1 text-xs font-semibold text-cyan-400 bg-cyan-950/60 border border-cyan-500/30 rounded-full">
          v1.0.0
        </span>
      </div>
    </header>
  );
}
