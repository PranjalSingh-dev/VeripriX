import React from 'react';

export default function ImageComparisonView({ comparison, previewA, previewB }) {
  if (!comparison) return null;

  return (
    <div className="glass-panel p-6 rounded-2xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Comparison Result</span>
          <h2 className="text-2xl font-black text-cyan-400">{comparison.verdict}</h2>
        </div>
        <div className="text-right">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Overall Similarity</span>
          <div className="text-3xl font-extrabold gradient-text">{comparison.overall_similarity}%</div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="space-y-2">
          <span className="text-xs font-semibold text-slate-400">Image A</span>
          <div className="rounded-xl overflow-hidden bg-slate-900 border border-slate-800 aspect-square flex items-center justify-center">
            <img src={previewA} alt="Image A" className="max-h-full object-contain" />
          </div>
        </div>

        <div className="space-y-2">
          <span className="text-xs font-semibold text-slate-400">Image B</span>
          <div className="rounded-xl overflow-hidden bg-slate-900 border border-slate-800 aspect-square flex items-center justify-center">
            <img src={previewB} alt="Image B" className="max-h-full object-contain" />
          </div>
        </div>

        <div className="space-y-2">
          <span className="text-xs font-semibold text-cyan-400">SSIM Diff Heatmap (What Changed)</span>
          <div className="rounded-xl overflow-hidden bg-slate-900 border border-cyan-500/30 aspect-square flex items-center justify-center">
            {comparison.diff_heatmap_url ? (
              <img src={comparison.diff_heatmap_url} alt="SSIM Diff" className="max-h-full object-contain" />
            ) : (
              <span className="text-xs text-slate-500">Diff Map Unavailable</span>
            )}
          </div>
        </div>
      </div>

      <div className="glass-card p-4 rounded-xl grid grid-cols-3 gap-4 text-center text-xs">
        <div>
          <span className="text-slate-400 block mb-1">pHash Hamming Distance</span>
          <span className="font-mono font-bold text-slate-200 text-sm">{comparison.phash_distance}</span>
        </div>
        <div>
          <span className="text-slate-400 block mb-1">Cosine Embedding Similarity</span>
          <span className="font-mono font-bold text-cyan-400 text-sm">{comparison.cosine_similarity}</span>
        </div>
        <div>
          <span className="text-slate-400 block mb-1">SSIM Score</span>
          <span className="font-mono font-bold text-indigo-400 text-sm">{comparison.ssim_score}</span>
        </div>
      </div>
    </div>
  );
}
