import React, { useState } from 'react';

export default function DetectionResultCard({ result, previewUrl }) {
  const [showHeatmap, setShowHeatmap] = useState(false);

  if (!result) return null;

  return (
    <div className="glass-panel p-6 rounded-2xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Analysis Verdict</span>
          <h2 className={`text-2xl font-black ${result.is_ai ? 'text-amber-400' : 'text-emerald-400'}`}>
            {result.verdict}
          </h2>
        </div>
        <div className="text-right">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Confidence Score</span>
          <div className="text-3xl font-extrabold gradient-text">
            {result.confidence}%
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <h4 className="text-sm font-semibold text-slate-300">
              {showHeatmap ? 'Grad-CAM Explainability Heatmap (F5)' : 'Original Image'}
            </h4>
            {result.heatmap_url && (
              <button
                onClick={() => setShowHeatmap(!showHeatmap)}
                className="text-xs text-cyan-400 hover:underline font-medium"
              >
                {showHeatmap ? 'Show Original' : 'Toggle Heatmap (Grad-CAM)'}
              </button>
            )}
          </div>
          <div className="relative rounded-xl overflow-hidden bg-slate-900 border border-slate-800 aspect-video flex items-center justify-center">
            <img
              src={showHeatmap ? result.heatmap_url : previewUrl}
              alt="Scan preview"
              className="max-h-full object-contain"
            />
          </div>
        </div>

        <div className="space-y-4">
          <h4 className="text-sm font-semibold text-slate-300">Forensic Signals & EXIF (F6)</h4>
          <div className="glass-card p-4 rounded-xl space-y-2 text-xs">
            <div className="flex justify-between border-b border-slate-800/80 pb-2">
              <span className="text-slate-400">Model Engine</span>
              <span className="font-mono text-cyan-400">{result.explanation?.model_architecture || 'ResNet50'}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/80 pb-2">
              <span className="text-slate-400">FFT Frequency Artifact Score</span>
              <span className="font-mono text-slate-200">{result.explanation?.frequency_artifact_score}</span>
            </div>
            <div className="flex justify-between border-b border-slate-800/80 pb-2">
              <span className="text-slate-400">EXIF Status</span>
              <span className={result.exif_data?.has_exif ? "text-emerald-400" : "text-amber-400 font-bold"}>
                {result.exif_data?.has_exif ? "Present" : "Missing (Typical for AI asset)"}
              </span>
            </div>
            {result.exif_data?.camera_make && (
              <div className="flex justify-between">
                <span className="text-slate-400">Camera / Device</span>
                <span className="text-slate-200">{result.exif_data.camera_make} {result.exif_data.camera_model}</span>
              </div>
            )}
          </div>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
            <h5 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">Key Diagnostic Signals</h5>
            <ul className="space-y-1 text-xs text-slate-300">
              {result.explanation?.signals?.map((sig, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
                  {sig}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
