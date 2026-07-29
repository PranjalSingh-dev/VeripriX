import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ImageUploader from './components/ImageUploader';
import DetectionResultCard from './components/DetectionResultCard';
import ImageComparisonView from './components/ImageComparisonView';

export default function App() {
  const [activeTab, setActiveTab] = useState('detect');
  
  // Dashboard stats state
  const [stats, setStats] = useState({
    total_scans: 0,
    ai_detection_rate: 0,
    comparisons_run: 0
  });

  // History list state
  const [historyItems, setHistoryItems] = useState([]);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);

  // Global Toast State
  const [toast, setToast] = useState(null);

  // Detection tab state
  const [detectionFile, setDetectionFile] = useState(null);
  const [detectionPreview, setDetectionPreview] = useState(null);
  const [detectionResult, setDetectionResult] = useState(null);
  const [isDetecting, setIsDetecting] = useState(false);

  // Comparison tab state
  const [compFileA, setCompFileA] = useState(null);
  const [compFileB, setCompFileB] = useState(null);
  const [compPreviewA, setCompPreviewA] = useState(null);
  const [compPreviewB, setCompPreviewB] = useState(null);
  const [compResult, setCompResult] = useState(null);
  const [isComparing, setIsComparing] = useState(false);

  // Reverse Search state
  const [searchResult, setSearchResult] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  // Video state
  const [videoResult, setVideoResult] = useState(null);
  const [isVideoAnalyzing, setIsVideoAnalyzing] = useState(false);

  // Show toast utility
  const showToast = (message, type = 'info') => {
    setToast({ message, type });
    setTimeout(() => setToast(null), 4000);
  };

  // Fetch stats from backend
  const fetchStats = async () => {
    try {
      const res = await fetch('/api/history/stats');
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (e) {
      console.error("Failed to load database statistics", e);
    }
  };

  // Fetch history list
  const fetchHistory = async () => {
    setIsLoadingHistory(true);
    try {
      const res = await fetch('/api/history');
      if (res.ok) {
        const data = await res.json();
        setHistoryItems(data);
      }
    } catch (e) {
      console.error("Failed to fetch scan history", e);
    } finally {
      setIsLoadingHistory(false);
    }
  };

  // Delete scan history record
  const handleDeleteScan = async (scanId) => {
    try {
      const res = await fetch(`/api/history/${scanId}`, { method: 'DELETE' });
      if (res.ok) {
        showToast("Scan record deleted successfully", "success");
        fetchHistory();
        fetchStats();
      }
    } catch (e) {
      showToast("Failed to delete scan record", "error");
    }
  };

  // Trigger stats and history fetching on component mount
  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    if (activeTab === 'history') {
      fetchHistory();
    }
    fetchStats();
  }, [activeTab]);

  // Handle Detection upload
  const handleDetectionUpload = async (file) => {
    setDetectionFile(file);
    setDetectionPreview(URL.createObjectURL(file));
    setIsDetecting(true);
    setDetectionResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/detect', { method: 'POST', body: formData });
      if (!res.ok) throw new Error("Backend unavailable");
      const data = await res.json();
      setDetectionResult(data);
      showToast("AI Detection completed successfully", "success");
      fetchStats();
    } catch (e) {
      console.error(e);
      // Fallback mock payload for offline browser dev
      setDetectionResult({
        verdict: "AI-Generated Image",
        confidence: 94.2,
        is_ai: true,
        heatmap_url: URL.createObjectURL(file),
        explanation: {
          frequency_artifact_score: 0.824,
          model_architecture: "ResNet50 / Universal Fake Probe",
          signals: ["Diffusion grid frequency artifacts detected", "Noise variance inconsistency"]
        },
        exif_data: { has_exif: false, warning: "Missing EXIF metadata" }
      });
      showToast("Showing simulated verification (offline mode)", "warning");
    } finally {
      setIsDetecting(false);
    }
  };

  // Handle Comparison execution
  const runComparison = async () => {
    if (!compFileA || !compFileB) return;
    setIsComparing(true);
    setCompResult(null);

    const formData = new FormData();
    formData.append('file_a', compFileA);
    formData.append('file_b', compFileB);

    try {
      const res = await fetch('/api/compare', { method: 'POST', body: formData });
      if (!res.ok) throw new Error("Backend unavailable");
      const data = await res.json();
      setCompResult(data);
      showToast("Multi-layer forensic comparison completed", "success");
      fetchStats();
    } catch (e) {
      setCompResult({
        verdict: "Near-Duplicate (Edited / Cropped)",
        overall_similarity: 88.5,
        phash_distance: 4,
        cosine_similarity: 0.912,
        ssim_score: 0.842,
        diff_heatmap_url: compPreviewA
      });
      showToast("Showing simulated comparison (offline mode)", "warning");
    } finally {
      setIsComparing(false);
    }
  };

  // Handle Reverse Search
  const handleReverseSearch = async (file) => {
    setIsSearching(true);
    setSearchResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/reverse-search', { method: 'POST', body: formData });
      if (!res.ok) throw new Error("Backend unavailable");
      const data = await res.json();
      setSearchResult(data);
      showToast("Reverse search returned web sources", "success");
      fetchStats();
    } catch (e) {
      setSearchResult({
        total_matches: 3,
        matches: [
          { source_url: "https://example.com/source", page_title: "Original Media Publication", domain_name: "example.com", match_confidence: 0.95 },
          { source_url: "https://stock.org/image", page_title: "Stock Asset Listing", domain_name: "stock.org", match_confidence: 0.88 },
          { source_url: "https://socialmedia.com/post/9823471", page_title: "Viral Image Discussion Thread", domain_name: "socialmedia.com", match_confidence: 0.76 },
        ]
      });
      showToast("Showing simulated search matches (offline mode)", "warning");
    } finally {
      setIsSearching(false);
    }
  };

  // Handle Video analysis
  const handleVideoUpload = async (file) => {
    setIsVideoAnalyzing(true);
    setVideoResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/detect-video', { method: 'POST', body: formData });
      if (!res.ok) throw new Error("Backend unavailable");
      const data = await res.json();
      setVideoResult(data);
      showToast("Video frame-by-frame analysis completed", "success");
      fetchStats();
    } catch (e) {
      setVideoResult({
        overall_verdict: "AI-Generated Video",
        overall_confidence: 91.5,
        frames_analyzed: 5,
        frame_timeline: [
          { timestamp_sec: 0.0, confidence: 92.0, is_ai: true },
          { timestamp_sec: 1.0, confidence: 95.0, is_ai: true },
          { timestamp_sec: 2.0, confidence: 88.0, is_ai: true },
          { timestamp_sec: 3.0, confidence: 91.0, is_ai: true },
          { timestamp_sec: 4.0, confidence: 92.0, is_ai: true },
        ]
      });
      showToast("Showing simulated video timeline (offline mode)", "warning");
    } finally {
      setIsVideoAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col relative pb-12">
      {/* Toast Alert popup */}
      {toast && (
        <div className="fixed top-6 right-6 z-50 glass-panel px-6 py-4 rounded-xl shadow-2xl border-l-4 border-cyan-400 flex items-center gap-3 animate-bounce">
          <div className="w-2 h-2 rounded-full bg-cyan-400"></div>
          <span className="text-sm font-semibold text-slate-200">{toast.message}</span>
        </div>
      )}

      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main stats cards layout */}
      <section className="max-w-6xl w-full mx-auto px-6 mt-8 grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="glass-panel p-5 rounded-2xl flex items-center justify-between border-l-4 border-cyan-500">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Scans Run</span>
            <p className="text-3xl font-extrabold text-white mt-1">{stats.total_scans}</p>
          </div>
          <div className="text-cyan-400 bg-cyan-950/40 p-3 rounded-xl border border-cyan-500/20">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2" /></svg>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl flex items-center justify-between border-l-4 border-amber-500">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">AI Identification Rate</span>
            <p className="text-3xl font-extrabold text-white mt-1">{stats.ai_detection_rate}%</p>
          </div>
          <div className="text-amber-400 bg-amber-950/40 p-3 rounded-xl border border-amber-500/20">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-2xl flex items-center justify-between border-l-4 border-purple-500">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Comparisons Executed</span>
            <p className="text-3xl font-extrabold text-white mt-1">{stats.comparisons_run}</p>
          </div>
          <div className="text-purple-400 bg-purple-950/40 p-3 rounded-xl border border-purple-500/20">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" /></svg>
          </div>
        </div>
      </section>

      <main className="flex-1 max-w-6xl w-full mx-auto p-6 space-y-8">
        {/* Tab 1: AI Detection */}
        {activeTab === 'detect' && (
          <div className="space-y-8">
            <div className="text-center max-w-2xl mx-auto space-y-2">
              <h2 className="text-3xl font-extrabold tracking-tight">
                AI Image Detection & Explainability
              </h2>
              <p className="text-slate-400 text-sm font-medium">
                Upload any photo to verify whether it was generated by Midjourney, DALL-E, Stable Diffusion, or Flux, complete with Grad-CAM heatmaps.
              </p>
            </div>

            <ImageUploader
              onUpload={handleDetectionUpload}
              title="Drop photo here for AI Verification"
              description="Supports JPG, PNG, WebP, HEIC up to 15MB"
            />

            {isDetecting && (
              <div className="glass-panel p-8 rounded-2xl text-center space-y-3">
                <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p className="text-sm font-semibold text-slate-300">Analyzing noise patterns & frequency spectrum...</p>
              </div>
            )}

            {detectionResult && (
              <DetectionResultCard result={detectionResult} previewUrl={detectionPreview} />
            )}
          </div>
        )}

        {/* Tab 2: Image Comparison */}
        {activeTab === 'compare' && (
          <div className="space-y-8">
            <div className="text-center max-w-2xl mx-auto space-y-2">
              <h2 className="text-3xl font-extrabold tracking-tight">
                Forensic Image Comparison (Same/Different)
              </h2>
              <p className="text-slate-400 text-sm font-medium">
                Compare two images using perceptual hashing (`pHash`), vector embeddings, and SSIM pixel-difference visual heatmaps.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <ImageUploader
                onUpload={(f) => { setCompFileA(f); setCompPreviewA(URL.createObjectURL(f)); }}
                title="Upload Image A"
                description={compFileA ? compFileA.name : "Select first image"}
              />
              <ImageUploader
                onUpload={(f) => { setCompFileB(f); setCompPreviewB(URL.createObjectURL(f)); }}
                title="Upload Image B"
                description={compFileB ? compFileB.name : "Select second image"}
              />
            </div>

            {compFileA && compFileB && (
              <div className="text-center">
                <button
                  onClick={runComparison}
                  disabled={isComparing}
                  className="gradient-btn px-8 py-3 rounded-xl font-bold text-white shadow-lg text-sm disabled:opacity-50"
                >
                  {isComparing ? 'Comparing image datasets...' : 'Run Multi-Layer Comparison'}
                </button>
              </div>
            )}

            {compResult && (
              <ImageComparisonView comparison={compResult} previewA={compPreviewA} previewB={compPreviewB} />
            )}
          </div>
        )}

        {/* Tab 3: Reverse Search */}
        {activeTab === 'search' && (
          <div className="space-y-8">
            <div className="text-center max-w-2xl mx-auto space-y-2">
              <h2 className="text-3xl font-extrabold tracking-tight">
                Web Reverse Image Search (F3)
              </h2>
              <p className="text-slate-400 text-sm font-medium">
                Trace original image provenance and find where else an image appears online across web indexing engines.
              </p>
            </div>

            <ImageUploader
              onUpload={handleReverseSearch}
              title="Upload Image for Reverse Search"
            />

            {isSearching && (
              <div className="glass-panel p-8 rounded-2xl text-center space-y-3">
                <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p className="text-sm font-semibold text-slate-300">Searching web indexing engines...</p>
              </div>
            )}

            {searchResult && (
              <div className="glass-panel p-6 rounded-2xl space-y-4">
                <div className="flex justify-between items-center border-b border-slate-800 pb-4">
                  <h3 className="text-lg font-bold text-slate-200">Found {searchResult.total_matches} Web Sources</h3>
                  <span className="text-xs text-slate-400 font-medium">Sorted by match confidence</span>
                </div>
                
                <div className="grid grid-cols-1 gap-4">
                  {searchResult.matches.map((item, idx) => (
                    <div key={idx} className="glass-card p-4 rounded-xl flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all duration-200 hover:border-cyan-500/20">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 text-[10px] font-bold uppercase rounded bg-slate-800 text-cyan-400 tracking-wider">
                            {item.domain_name || 'Web Source'}
                          </span>
                          <h4 className="font-bold text-slate-100">{item.page_title}</h4>
                        </div>
                        <a href={item.source_url} target="_blank" rel="noreferrer" className="text-xs text-slate-400 truncate max-w-xl block hover:underline hover:text-cyan-400">
                          {item.source_url}
                        </a>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-xs text-slate-400">Confidence</span>
                        <span className="px-3.5 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-sm font-mono font-bold text-cyan-400">
                          {Math.round(item.match_confidence * 100)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 4: Video Detection */}
        {activeTab === 'video' && (
          <div className="space-y-8">
            <div className="text-center max-w-2xl mx-auto space-y-2">
              <h2 className="text-3xl font-extrabold tracking-tight">
                Video AI Frame Detection (F9)
              </h2>
              <p className="text-slate-400 text-sm font-medium">
                Sample video frames at 1 fps interval, run frame-by-frame AI classification, and view the suspicion timeline.
              </p>
            </div>

            <ImageUploader
              onUpload={handleVideoUpload}
              title="Upload Video File (MP4/WebM)"
              accept="video/*"
            />

            {isVideoAnalyzing && (
              <div className="glass-panel p-8 rounded-2xl text-center space-y-3">
                <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p className="text-sm font-semibold text-slate-300">Extracting frames and executing temporal analysis...</p>
              </div>
            )}

            {videoResult && (
              <div className="glass-panel p-6 rounded-2xl space-y-6">
                <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                  <div>
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Overall Video Verdict</span>
                    <h3 className={`text-2xl font-black ${videoResult.overall_verdict.includes('AI') ? 'text-amber-400' : 'text-emerald-400'}`}>
                      {videoResult.overall_verdict}
                    </h3>
                  </div>
                  <div className="text-right">
                    <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Aggregated Confidence</span>
                    <div className="text-3xl font-extrabold gradient-text">{videoResult.overall_confidence}%</div>
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="text-sm font-semibold text-slate-300">Interactive Frame Suspicion Timeline</h4>
                  <div className="flex gap-2 h-36 items-end bg-slate-900/50 p-4 rounded-xl border border-slate-800">
                    {videoResult.frame_timeline.map((frame, idx) => (
                      <div 
                        key={idx} 
                        className="flex-1 flex flex-col items-center gap-2 group cursor-pointer"
                      >
                        <div className="text-[10px] font-mono text-slate-400 opacity-0 group-hover:opacity-100 transition-opacity">
                          {frame.confidence}%
                        </div>
                        <div 
                          style={{ height: `${frame.confidence}%` }}
                          className={`w-full rounded-t-md transition-all duration-300 ${
                            frame.is_ai 
                              ? 'bg-gradient-to-t from-amber-600 to-amber-400 hover:from-amber-500' 
                              : 'bg-gradient-to-t from-cyan-600 to-cyan-400 hover:from-cyan-500'
                          }`}
                        ></div>
                        <span className="text-[10px] font-mono text-slate-400 mt-1">{frame.timestamp_sec}s</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="space-y-3">
                  <h4 className="text-sm font-semibold text-slate-300 font-medium">Detailed Frame Analysis</h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                    {videoResult.frame_timeline.map((frame, idx) => (
                      <div key={idx} className="glass-card p-4 rounded-xl flex items-center justify-between">
                        <div>
                          <span className="text-[10px] text-slate-400 font-mono block">Frame #{frame.frame_index}</span>
                          <span className="text-sm font-bold text-white font-mono">{frame.timestamp_sec}s timestamp</span>
                        </div>
                        <span className={`px-2.5 py-1 rounded-md text-xs font-mono font-bold ${
                          frame.is_ai ? 'bg-amber-950/60 text-amber-400 border border-amber-500/20' : 'bg-cyan-950/60 text-cyan-400 border border-cyan-500/20'
                        }`}>
                          {frame.confidence}% AI
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Tab 5: Scan History */}
        {activeTab === 'history' && (
          <div className="space-y-6">
            <div className="text-center max-w-2xl mx-auto space-y-2">
              <h2 className="text-3xl font-extrabold tracking-tight">Scan History</h2>
              <p className="text-slate-400 text-sm font-medium">Review all past forensic checks, detection verdicts, and comparisons saved to database.</p>
            </div>

            {isLoadingHistory ? (
              <div className="glass-panel p-12 text-center text-slate-400 space-y-3">
                <div className="w-8 h-8 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin mx-auto"></div>
                <p className="text-sm font-semibold">Syncing with database history...</p>
              </div>
            ) : historyItems.length === 0 ? (
              <div className="glass-panel p-12 rounded-2xl text-center text-slate-400 text-sm border-2 border-dashed border-slate-800">
                <p className="text-base font-bold text-slate-300">No scans found</p>
                <p className="mt-1 text-slate-500">Run a detection, comparison, or search task to populate history.</p>
              </div>
            ) : (
              <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse text-sm">
                    <thead>
                      <tr className="bg-slate-900/80 border-b border-slate-800 text-slate-400 font-bold">
                        <th className="p-4">Target Image / Pair</th>
                        <th className="p-4">Analysis Category</th>
                        <th className="p-4">Diagnostic Verdict</th>
                        <th className="p-4">Confidence</th>
                        <th className="p-4">Date Run</th>
                        <th className="p-4 text-center">Action</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 bg-slate-950/20">
                      {historyItems.map((item) => (
                        <tr key={item.id} className="hover:bg-slate-900/30 transition-colors">
                          <td className="p-4 font-mono font-bold text-slate-200 truncate max-w-xs">{item.image_url}</td>
                          <td className="p-4">
                            <span className="px-2.5 py-0.5 rounded text-[11px] font-bold uppercase bg-slate-800 text-slate-300 border border-slate-700">
                              {item.feature_type}
                            </span>
                          </td>
                          <td className="p-4">
                            <span className={`font-bold ${
                              item.verdict?.includes('AI') 
                                ? 'text-amber-400' 
                                : item.verdict?.includes('Real') || item.verdict?.includes('Matches') 
                                  ? 'text-emerald-400' 
                                  : 'text-cyan-400'
                            }`}>
                              {item.verdict}
                            </span>
                          </td>
                          <td className="p-4 font-mono font-semibold text-slate-300">
                            {item.confidence ? `${item.confidence}%` : 'N/A'}
                          </td>
                          <td className="p-4 text-xs text-slate-400">
                            {new Date(item.created_at).toLocaleDateString()} {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </td>
                          <td className="p-4 text-center">
                            <button
                              onClick={() => handleDeleteScan(item.id)}
                              className="text-red-400 hover:text-red-300 transition-colors p-1 bg-red-950/20 border border-red-500/10 hover:border-red-500/30 rounded"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
